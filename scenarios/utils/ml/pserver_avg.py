import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../utils'))
import statistics

from python_sockets.server import UDPServer
from .customprotocol import *


class PServer(object):
    def __init__(self, port, host, params):
        self.port = port
        s_params = ' '.join(["i"]*params)
        protocol = CustomProtocol(header_mask='! B B I ' + s_params)
        self.server = UDPServer(port, host, protocol=protocol)

    def get_formated_message(self, status, workers, step, weights):
        values = []
        values.append(status)
        values.append(workers)
        values.append(step)
        values.extend(weights)
        return values

    def aggregate_values(self, params, new_values):
        print('Old values', params)
        if len(params) == 0:
            print('Params size is 0', new_values)
            return new_values

        assert len(params) == len(
            new_values), 'Sizes are not the same: {}/{}'.format(len(params), len(new_values))

        print('Aggregating parameters')
        for i, param in enumerate(params):
            params[i] = (param + new_values[i])
        
        print('New values', params)
        return params

    def send_error(self, destination, error=STATE_ERROR, workers=0):
        self.server.send_message(self.get_formated_message(error,workers,0,[]), destination)

    def run(self, worker_num, learning_parameters, bcast=True):
        assert len(learning_parameters) >= 6, "Wrong learning parameters"
      
        self.bcast = bcast
        iterations = learning_parameters[0]
        scaled_eta = learning_parameters[1]
        input_size = learning_parameters[2]
        input_features = learning_parameters[3]
        output_classes = learning_parameters[4]
        scale_factor = learning_parameters[5]
        eta = scaled_eta/scale_factor

        self.server.start()
        current_status = STATE_SETUP
        workers = []
        current_step = 0
        curr_aggregation = [] # matrix N_nodes X N_weights
        acc_aggregation = [] # vector N_weights
        
        print("Params | workers: {} | iterations: {} | eta: {} | input: {} | feat: {} | out: {} | scale: {}".format(
            worker_num, iterations, eta, input_size, input_features, output_classes, scale_factor
        ))

        while True:
            print('Waiting for messages...')
            msg, client_address = self.server.receive_message(send_answer=False)
            status = msg[0]
            _ = msg[1]
            step = msg[2]
            parameters = msg[3:]

            if status is STATE_WRONG_STEP or status is STATE_ERROR:
                print('Received error message: {}'.format(msg))
                continue
            
            if status != current_status:
                print('Received message in another state: {}/{}'.format(status, current_status))
                msg = self.get_formated_message(current_status, len(workers), current_step, [])
                self.server.send_message(msg, client_address)
                continue


            if current_status == STATE_SETUP:
                # setup phase
                if client_address not in workers:
                    print('Registering worker: {}'.format(client_address))
                    msg = self.get_formated_message(STATE_SETUP, worker_num, len(workers), learning_parameters)
                    workers.append(client_address)
                    print('Sending setup')
                    self.server.send_message(msg, client_address)
                else:
                    print('Worker {} is already registered'.format(client_address))
                    self.send_error(client_address, workers=len(workers))

                if len(workers) == worker_num:
                    print('All workers registered')
                    current_status = STATE_LEARNING
                    workers = []

            elif current_status == STATE_LEARNING:

                if int(step) != current_step:
                    print('Wrong step {}/{}'.format(step, current_step))
                    self.send_error(client_address, error=STATE_WRONG_STEP)
                    continue
                else:
                    if client_address not in workers:
                        workers.append(client_address)
                        curr_aggregation = self.aggregate_values(curr_aggregation, parameters)

                        if not self.bcast:
                            print('Sending parameters to worker {}:{}'.format(client_address[0],client_address[1]))
                            # send accumulated params
                            msg = self.get_formated_message(current_status, len(workers), current_step, acc_aggregation)
                            self.server.send_message(msg, client_address)
                    else:
                        print('Worker {} is already aggregated'.format(client_address))
                        self.send_error(client_address, workers=len(workers))

                if len(workers) == worker_num:
                    print('All workers aggregated in step:', current_step)
                    acc_aggregation = curr_aggregation
                    curr_aggregation = []
                    
                    if self.bcast:
                        print('Broadcasting parameters to workers')
                        msg = self.get_formated_message(current_status, len(workers), current_step, acc_aggregation)
                        # Broadcast aggregated results
                        for w in workers:
                            self.server.send_message(msg, w)
                    
                    print('Next step')
                    current_step += 1                
                    workers = []
                    if current_step == iterations:
                        print('Finished')
                        sys.exit()
                        current_status = STATE_WAITING

            elif current_status == STATE_WAITING:
                print('Finished')
                sys.exit()
                pass
            else:
                print('Unknown key')
                sys.exit()

        self.server.stop()

