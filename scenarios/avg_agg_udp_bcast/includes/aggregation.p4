/*************************************************************************
************  A G G R E G A T I O N   P R O C E S S I N G   **************
*************************************************************************/
control Aggregation(inout headers hdr, inout bit<2> result) {


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

        curr_aggregation.read(temp_value, 5);
        curr_aggregation.write(5, temp_value + hdr.agg.param_5);
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

        curr_aggregation.read(temp_value, 5);
        curr_aggregation.write(5, 0);
        acc_aggregation.write(5, temp_value);
    }

    action bcast_aggregation() {
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
        load_state();
        if (current_state == hdr.agg.state) {
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
                        aggregate();
                        increment_node_count();
                        if (node_count >= NODE_NUMBER){
                            update_aggregation();
                            bcast_aggregation();
                            update_node_count(0);
                            increment_step();
                            if (current_step >= ITERATIONS){
                                update_state(STATE_FINISHED);
                            }
                            result = RESULT_MCAST;
                        } else {
                            // still aggregating, drop it
                            result = RESULT_DROP;
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
