/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

#include "includes/header.p4"
#include "includes/parser.p4"
#include "params"

const bit<32> MAX_COUNTERS = ((1 << 20) - 1);

const bit<32> PARAM_NUMBER = 6;
const bit<32> MAX_NODES = 6;

// state messages
const bit<8> STATE_SETUP = 0;
const bit<8> STATE_LEARNING = 1;
const bit<8> STATE_FINISHED = 2;
const bit<8> STATE_ERROR = 3;
const bit<8> STATE_WRONG_STEP = 4;

const bit<32> NODES_IDX = 0x2;
const bit<32> STEP_IDX = 0x3;
const bit<32> STATE_IDX = 0x4;
const bit<32> MEDIANS_IDX = 0x5;

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
    
    register<bit<32>>(PARAM_NUMBER*MAX_NODES) curr_aggregation;
    // aggregated gradients from step-1
    register<bit<32>>(PARAM_NUMBER) acc_aggregation;
    
    // register that holds counters of nodes, step, and state
    register<bit<32>>(MAX_COUNTERS) counters_register;


    bit<32> current_step;
    bit<8> current_state;
    bit<32> node_count;
    bit<32> temp_value;
    bit<32> median_index;
    
    action update_aggregation() {
        bit<32> temp_index = 0;
        bit<32> median1 = 0;
        bit<32> median2 = 0;
        bit<32> median_idx1 = 0;
        bit<32> median_idx2 = 0;

        // get stored median index
        counters_register.read(median_idx1, MEDIANS_IDX);

        if ((NODE_NUMBER & 1) == 0){
            // this means that the number is odd
            median_idx2 = median_idx1;
        } else {
            median_idx2 = median_idx1-1;
        }

        // param 0
        
        // get median value
        // median_idx + param offset (temp_index*NODE_NUMBER)
        curr_aggregation.read(median1, median_idx1+temp_index*NODE_NUMBER);
        curr_aggregation.read(median2, median_idx2+temp_index*NODE_NUMBER);
        acc_aggregation.write(temp_index, median1+median2);

        // param 1
        temp_index = temp_index + 1;
        // get median value
        // median_idx + param offset (temp_index*NODE_NUMBER)
        curr_aggregation.read(median1, median_idx1+temp_index*NODE_NUMBER);
        curr_aggregation.read(median2, median_idx2+temp_index*NODE_NUMBER);
        acc_aggregation.write(temp_index, median1+median2);

        
        // param 2
        temp_index = temp_index + 1;
        // get median value
        // median_idx + param offset (temp_index*NODE_NUMBER)
        curr_aggregation.read(median1, median_idx1+temp_index*NODE_NUMBER);
        curr_aggregation.read(median2, median_idx2+temp_index*NODE_NUMBER);
        acc_aggregation.write(temp_index, median1+median2);


        // param 3
        temp_index = temp_index + 1;
        // get median value
        // median_idx + param offset (temp_index*NODE_NUMBER)
        curr_aggregation.read(median1, median_idx1+temp_index*NODE_NUMBER);
        curr_aggregation.read(median2, median_idx2+temp_index*NODE_NUMBER);
        acc_aggregation.write(temp_index, median1+median2);


        // param 4
        temp_index = temp_index + 1;
        // get median value
        // median_idx + param offset (temp_index*NODE_NUMBER)
        curr_aggregation.read(median1, median_idx1+temp_index*NODE_NUMBER);
        curr_aggregation.read(median2, median_idx2+temp_index*NODE_NUMBER);
        acc_aggregation.write(temp_index, median1+median2);



        // param 5
        temp_index = temp_index + 1;
        // get median value
        // median_idx + param offset (temp_index*NODE_NUMBER)
        curr_aggregation.read(median1, median_idx1+temp_index*NODE_NUMBER);
        curr_aggregation.read(median2, median_idx2+temp_index*NODE_NUMBER);
        acc_aggregation.write(temp_index, median1+median2);

    }

    action sort_parameter(in bit<32> start_index, in bit<32> parameter) {
        bit<32> value = parameter;
        bit<32> temp = parameter;
        bit<32> temp2 = parameter;
        bit<32> current_index = start_index;
        
        curr_aggregation.read(temp_value, current_index);
        if (node_count > 1 && temp < temp_value){
            temp = temp_value;
            temp_value = value;
        }
        curr_aggregation.write(current_index, temp_value);


        current_index = current_index + 1;
        curr_aggregation.read(temp_value, current_index);
        if (node_count > 2 && temp < temp_value){
            temp2 = temp_value;
            temp_value = temp;
            temp = temp2;
        }
        curr_aggregation.write(current_index, temp_value);

        current_index = current_index + 1;
        curr_aggregation.read(temp_value, current_index);
        if (node_count > 3 && temp < temp_value){
            temp2 = temp_value;
            temp_value = temp;
            temp = temp2;
        }
        curr_aggregation.write(current_index, temp_value);

        current_index = current_index + 1;
        curr_aggregation.read(temp_value, current_index);
        if (node_count > 4 && temp < temp_value){
            temp2 = temp_value;
            temp_value = temp;
            temp = temp2;
        }
        curr_aggregation.write(current_index, temp_value);

        current_index = current_index + 1;
        curr_aggregation.read(temp_value, current_index);
        if (node_count > 5 && temp < temp_value){
            temp2 = temp_value;
            temp_value = temp;
            temp = temp2;
        }
        
        current_index = current_index + 1;
        curr_aggregation.read(temp_value, current_index);
        if (node_count > 6 && temp < temp_value){
            temp2 = temp_value;
            temp_value = temp;
            temp = temp2;
        }
        curr_aggregation.write(current_index, temp_value);

        curr_aggregation.write(start_index+(node_count-1), temp);
        
        counters_register.read(temp_value, MEDIANS_IDX);
        if ((node_count*2) == NODE_NUMBER-1 || (node_count*2) == NODE_NUMBER){
            // this should be the median index
            temp_value = node_count;
        }
        counters_register.write(MEDIANS_IDX, temp_value);
    }

    action send_aggregation() {
        hdr.agg.step = current_step;
        hdr.agg.node_count = (bit<8>)node_count;
        acc_aggregation.read(hdr.agg.param_0, 0);
        acc_aggregation.read(hdr.agg.param_1, 1);
        acc_aggregation.read(hdr.agg.param_2, 2);
        acc_aggregation.read(hdr.agg.param_3, 3);
        acc_aggregation.read(hdr.agg.param_4, 4);
        acc_aggregation.read(hdr.agg.param_5, 5);
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
        hdr.agg.node_count = (bit<8>)NODE_NUMBER;
        hdr.agg.step = current_step;
        hdr.agg.param_0 = ITERATIONS;
        hdr.agg.param_1 = ETA;
        hdr.agg.param_2 = INPUT_SIZE;
        hdr.agg.param_3 = INPUT_FEATURES;
        hdr.agg.param_4 = OUTPUT_CLASSES;
        hdr.agg.param_5 = SCALE_FACTOR;
    }

    action load_state() {
        counters_register.read(temp_value, STATE_IDX);
        current_state = (bit<8>)temp_value;
    }

    action load_counters() {
        counters_register.read(node_count, NODES_IDX);
        counters_register.read(current_step, STEP_IDX);
    }

    action update_state(in bit<8> state) {
        counters_register.write(STATE_IDX,(bit<32>)state);
    }

    action update_step(in bit<32> step) {
        counters_register.write(STEP_IDX, step);
    }

    action increment_step() {
        counters_register.read(temp_value, STEP_IDX);
        counters_register.write(STEP_IDX, temp_value+1);
        counters_register.read(current_step, STEP_IDX);
    }

    action update_node_count(in bit<32> count) {
        counters_register.write(NODES_IDX, count);
    }
    action increment_node_count() {
        counters_register.read(temp_value, NODES_IDX);
        counters_register.write(NODES_IDX, temp_value+1);
        counters_register.read(node_count, NODES_IDX);
    }

    apply {
        if (hdr.agg.isValid()){
            load_state();
            if (hdr.agg.state == current_state) {
                if (current_state == STATE_SETUP){
                    // TODO: check not duplicate nodes
                    @atomic {
                        load_counters();
                        send_parameters();
                        increment_node_count();
                        if (node_count == NODE_NUMBER){
                            update_node_count(0);
                            update_state(STATE_LEARNING);
                        } 
                    }
                } else if (current_state == STATE_LEARNING){
                    @atomic {
                        load_counters();
                        if (current_step == hdr.agg.step){
                            increment_node_count();
                            // sort all parameters
                            sort_parameter(0,hdr.agg.param_0);
                            sort_parameter(NODE_NUMBER,hdr.agg.param_1);
                            sort_parameter(2*NODE_NUMBER,hdr.agg.param_2);
                            sort_parameter(3*NODE_NUMBER,hdr.agg.param_3);
                            sort_parameter(4*NODE_NUMBER,hdr.agg.param_4);
                            sort_parameter(5*NODE_NUMBER,hdr.agg.param_5);
                            send_aggregation();

                            if (node_count >= NODE_NUMBER){
                                update_aggregation();
                                update_node_count(0);
                                increment_step();
                                if (current_step >= ITERATIONS){
                                    update_state(STATE_FINISHED);
                                }
                            }
                        } else {
                            hdr.agg.step = current_step;
                            send_error(STATE_WRONG_STEP);
                        }
                    }
                } else if (current_state == STATE_FINISHED){
                    @atomic {
                        load_counters();
                        // state is finished, send state
                        send_current_state();
                    }
                } else {
                    send_error(STATE_ERROR);
                }
            } else {
                // if finished and another worker asks to start, back to initial
                if (current_state == STATE_FINISHED){
                    if (hdr.agg.state == STATE_SETUP){
                        update_state(STATE_SETUP);
                        update_step(0);
                        update_aggregation();
                        update_node_count(0);
                    } 
                }
                @atomic {
                    load_counters();
                    // state is wrong, answer with current state
                    send_current_state();
                }
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
