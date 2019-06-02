/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

#include "header"
#include "parser"

const bit<4> NODE_NUMBER = 2;


const bit<32> MAX_STEPS = ((1 << 20) - 1);
const bit<32> MAX_NODES = ((1 << 3) - 1);

const bit<32> WEIGHTS_NUMBER = 5;

// status messages
const bit<8> STATUS_UPSTREAM = 0;
const bit<8> STATUS_DOWNSTREAM = 1;
const bit<8> STATUS_ERROR = 2;
const bit<8> STATUS_WRONG_STEP = 3;

const bit<32> COUNTER_IDX = 0x1;

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {

    action drop() {
        mark_to_drop();
    }
    
    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }
    
    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = drop();
    }

    action send_answer() {
        standard_metadata.egress_spec = standard_metadata.ingress_port;
        macAddr_t tmp = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = hdr.ethernet.srcAddr;
        hdr.ethernet.srcAddr = tmp;
    }

    apply {
        if (hdr.agg.isValid()) {
            send_answer();
        } else{
            if (hdr.ipv4.isValid()){
                ipv4_lpm.apply();
            }
        }
     }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    
    // aggregated gradients from step-1
    register<bit<32>>(WEIGHTS_NUMBER) curr_aggregation;
    register<bit<32>>(WEIGHTS_NUMBER) acc_aggregation;
    register<bit<4>>(MAX_NODES) node_counter;

    // counter of nodes that I received the gradient from
    register<bit<32>>(MAX_STEPS) step_counter;
    bit<32> current_step;
    bit<4> node_count;
    bit<32> temp_value;
    
    action aggregate() {
        // increase node counter
        node_counter.write(COUNTER_IDX, node_count+1);

        // aggregate values
        curr_aggregation.read(temp_value, 0);
        curr_aggregation.write(0, temp_value + hdr.agg.weight_0);

        curr_aggregation.read(temp_value, 1);
        curr_aggregation.write(1, temp_value + hdr.agg.weight_1);
        
        curr_aggregation.read(temp_value, 2);
        curr_aggregation.write(2, temp_value + hdr.agg.weight_2);

        curr_aggregation.read(temp_value, 3);
        curr_aggregation.write(3, temp_value + hdr.agg.weight_3);

        curr_aggregation.read(temp_value, 4);
        curr_aggregation.write(4, temp_value + hdr.agg.weight_4);
    }
    
    action next_step() {
        // increase step count
        step_counter.write(COUNTER_IDX, current_step+1);

        // reset node counter to 1
        node_counter.write(COUNTER_IDX, 1);

        // cache curr_aggregation into acc_aggregation
        // reset curr_aggregation
        curr_aggregation.read(temp_value, 0);
        curr_aggregation.write(0, hdr.agg.weight_0);
        acc_aggregation.write(0, temp_value);

        curr_aggregation.read(temp_value, 1);
        curr_aggregation.write(1, hdr.agg.weight_1);
        acc_aggregation.write(1, temp_value);
        
        curr_aggregation.read(temp_value, 2);
        curr_aggregation.write(2, hdr.agg.weight_2);
        acc_aggregation.write(2, temp_value);

        curr_aggregation.read(temp_value, 3);
        curr_aggregation.write(3, hdr.agg.weight_3);
        acc_aggregation.write(3, temp_value);

        curr_aggregation.read(temp_value, 4);
        curr_aggregation.write(4, hdr.agg.weight_4);
        acc_aggregation.write(4, temp_value);
    }

    action update_header() {
        acc_aggregation.read(hdr.agg.weight_0, 0);
        acc_aggregation.read(hdr.agg.weight_1, 1);
        acc_aggregation.read(hdr.agg.weight_2, 2);
        acc_aggregation.read(hdr.agg.weight_3, 3);
        acc_aggregation.read(hdr.agg.weight_4, 4);
    }

    action set_error(in bit<8> type) {
        hdr.agg.status = type;
    }

    action get_counters() {
        step_counter.read(current_step, COUNTER_IDX);
        node_counter.read(node_count, COUNTER_IDX);
    }

    apply {
        if (hdr.agg.isValid()){
            if (hdr.agg.status == STATUS_UPSTREAM) {
                get_counters();
                if (node_count == NODE_NUMBER){
                    if ((current_step+1) == hdr.agg.step){
                        next_step();
                        update_header();
                    } else {
                        set_error(STATUS_WRONG_STEP);
                    }
                } else {
                    if (current_step == (hdr.agg.step)){
                        aggregate();
                        update_header();
                    } else {
                        set_error(STATUS_WRONG_STEP);
                    }
                }
            } else {
                set_error(STATUS_ERROR);
            }
        }
    }
}


/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
