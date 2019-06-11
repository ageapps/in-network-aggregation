/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

#include "header"
#include "parser"
#include "params"

const bit<32> MAX_COUNTERS = ((1 << 20) - 1);

const bit<32> PARAM_NUMBER = 5;

// state messages
const bit<8> STATE_SETUP = 0;
const bit<8> STATE_LEARNING = 1;
const bit<8> STATE_FINISHED = 2;
const bit<8> STATE_ERROR = 3;
const bit<8> STATE_WRONG_STEP = 4;

const bit<32> NODES_IDX = 0x1;
const bit<32> STEP_IDX = 0x2;
const bit<32> STATE_IDX = 0x3;

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
        macAddr_t tmp_mac = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = hdr.ethernet.srcAddr;
        hdr.ethernet.srcAddr = tmp_mac;

        ip4Addr_t tmp_ip = hdr.ipv4.srcAddr;
        hdr.ipv4.srcAddr = hdr.ipv4.dstAddr;
        hdr.ipv4.dstAddr = tmp_ip;
        
        hdr.udp.dstPort = hdr.udp.srcPort;
        hdr.udp.srcPort = UDP_PORT;
        hdr.udp.checksum = 0;
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
    
    register<bit<32>>(PARAM_NUMBER) curr_aggregation;
    // aggregated gradients from step-1
    register<bit<32>>(PARAM_NUMBER) acc_aggregation;
    
    // register that holds counters of nodes, step, and state
    register<bit<32>>(MAX_COUNTERS) counters_register;


    bit<32> current_step;
    bit<8> current_state;
    bit<32> node_count;
    bit<32> temp_value;
    
    action aggregate() {
        curr_aggregation.read(temp_value, 0);
        curr_aggregation.write(0, temp_value + hdr.agg.param_0);

        curr_aggregation.read(temp_value, 1);
        curr_aggregation.write(1, temp_value + hdr.agg.param_1);
        
        curr_aggregation.read(temp_value, 2);
        curr_aggregation.write(2, temp_value + hdr.agg.param_2);

        curr_aggregation.read(temp_value, 3);
        curr_aggregation.write(3, temp_value + hdr.agg.param_3);

        curr_aggregation.read(temp_value, 4);
        curr_aggregation.write(4, temp_value + hdr.agg.param_4);
    }
    
    action update_aggregation() {
        // cache curr_aggregation into acc_aggregation
        // reset curr_aggregation
        curr_aggregation.read(temp_value, 0);
        curr_aggregation.write(0, 0);
        acc_aggregation.write(0, temp_value);

        curr_aggregation.read(temp_value, 1);
        curr_aggregation.write(1, 0);
        acc_aggregation.write(1, temp_value);
        
        curr_aggregation.read(temp_value, 2);
        curr_aggregation.write(2, 0);
        acc_aggregation.write(2, temp_value);

        curr_aggregation.read(temp_value, 3);
        curr_aggregation.write(3, 0);
        acc_aggregation.write(3, temp_value);

        curr_aggregation.read(temp_value, 4);
        curr_aggregation.write(4, 0);
        acc_aggregation.write(4, temp_value);
    }

    action send_aggregation() {
        acc_aggregation.read(hdr.agg.param_0, 0);
        acc_aggregation.read(hdr.agg.param_1, 1);
        acc_aggregation.read(hdr.agg.param_2, 2);
        acc_aggregation.read(hdr.agg.param_3, 3);
        acc_aggregation.read(hdr.agg.param_4, 4);
    }

    action send_error(in bit<8> type) {
        hdr.agg.state = type;
    }
    
    action send_current_state() {
        hdr.agg.state = current_state;
        hdr.agg.step = current_step;
    }

    action send_parameters() {
        hdr.agg.state = current_state;
        hdr.agg.step = NODE_NUMBER;
        hdr.agg.param_0 = ITERATIONS;
        hdr.agg.param_1 = ETA;
        hdr.agg.param_2 = INPUT_SIZE;
        hdr.agg.param_3 = OUTPUT_CLASSES;
        hdr.agg.param_4 = SCALE_FACTOR;
    }

    action load_counters() {
        counters_register.read(node_count, NODES_IDX);
        counters_register.read(current_step, STEP_IDX);
        counters_register.read(temp_value, STATE_IDX);
        current_state = (bit<8>)temp_value;
    }

    action update_state(in bit<8> state) {
        counters_register.write(STATE_IDX,(bit<32>)state);
    }

    action update_step(in bit<32> step) {
        current_step = step;
        counters_register.write(STEP_IDX, step);
    }

    action update_node_count(in bit<32> count) {
        node_count = count;
        counters_register.write(NODES_IDX, count);
    }

    apply {
        if (hdr.agg.isValid()){
            load_counters();
            if (hdr.agg.state == current_state) {
                if (current_state == STATE_SETUP){
                    update_node_count(node_count+1);
                    // TODO: check not duplicate nodes
                    send_parameters();
                    if (node_count == NODE_NUMBER){
                        update_state(STATE_LEARNING);
                        update_node_count(0);
                    } 
                } else if (current_state == STATE_LEARNING){
                    if (current_step == hdr.agg.step){
                        update_node_count(node_count+1);
                        aggregate();
                        if (node_count == NODE_NUMBER){
                            update_aggregation();
                            update_node_count(0);
                            if (current_step == ITERATIONS-1){
                                update_state(STATE_FINISHED);
                            } else {
                                update_step(current_step+1);
                            }
                        }
                        send_aggregation();
                    } else {
                        send_error(STATE_WRONG_STEP);
                    }
                } else if (current_state == STATE_FINISHED){
                    // state is finished, send state
                    send_current_state();
                } else {
                    send_error(STATE_ERROR);
                }
            } else {
                // if finished and another worker asks to start, back to initial
                if (current_state == STATE_FINISHED){
                    if (hdr.agg.state == STATE_SETUP){
                        update_state(STATE_SETUP);
                        update_step(0);
                        update_node_count(0);
                    } 
                }
                // state is wrong, answer with current state
                send_current_state();
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
