import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../utils'))
import statistics

from python_sockets.server import UDPServer
from python_sockets.protocol import FragmentProtocol

from customprotocol import *

PORT = 12344
HOST = ''

iterations = 50
eta = 0.001
input_size = 200
input_features = 1
output_classes = 1
scale_factor = 1000


scaled_eta = int(eta * scale_factor)

learning_parameters = [
    iterations,
    scaled_eta,
    input_size,
    input_features,
    output_classes,
    scale_factor
]

def get_formated_message(status, workers, step, weights):
    values = []
    values.append(status)
    values.append(workers)
    values.append(step)
    values.extend(weights)
    return values

def get_medians(param_mtx):
    weights_cols = list(zip(*param_mtx))
    medians = []
    for v in weights_cols:
        median = statistics.median(v)
        medians.append(int(2*median))
    
    print('Medians are: {}'.format(medians))
    return medians

def aggregate_values(param_mtx, new_values):
    
    if len(param_mtx) > 0:
        assert len(param_mtx[0]) == len(
            new_values), 'Sizes are not the same: {}/{}'.format(len(param_mtx[0]), len(new_values))

    print('Aggregating parameters')
    param_mtx.append(new_values)
    return param_mtx

def send_error(server, destination, error=STATE_ERROR, workers=0):
    server.send_message(get_formated_message(error,workers,0,[]), destination)

def main():
    port = PORT
    worker_num = 1
    
    if len(sys.argv) > 1:
        worker_num = int(sys.argv[1])
    else:
        print('pass 2 arguments: <workers>({}) <port>({})'.format(worker_num, port))
        exit(1)

    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    proto = CustomProtocol(header_mask='! B B I i i i i i i')
    server = UDPServer(port, HOST, protocol=proto)
    server.start()
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
        msg, client_address = server.receive_message(send_answer=False)
        status = msg[0]
        worker = msg[1]
        step = msg[2]
        parameters = msg[3:]

        if status is STATE_WRONG_STEP or status is STATE_ERROR:
            print('Received error message: {}'.format(msg))
            continue
        
        if status != current_status:
            print('Received message in another state: {}/{}'.format(status, current_status))
            msg = get_formated_message(current_status, len(workers), current_step, [])
            server.send_message(msg, client_address)
            continue


        if current_status == STATE_SETUP:
            # setup phase
            if client_address not in workers:
                print('Registering worker: {}'.format(client_address))
                workers.append(client_address)
                print('Sending setup')
                msg = get_formated_message(STATE_SETUP, worker_num, current_step, learning_parameters)
                server.send_message(msg, client_address)
            else:
                print('Worker {} is already registered'.format(client_address))
                send_error(server, client_address, workers=len(workers))

            if len(workers) == worker_num:
                print('All workers registered')
                current_status = STATE_LEARNING
                workers = []

        elif current_status == STATE_LEARNING:

            if int(step) != current_step:
                print('Wrong step {}/{}'.format(step, current_step))
                send_error(server, client_address, error=STATE_WRONG_STEP)
                continue
            else:
                if client_address not in workers:
                    workers.append(client_address)
                    curr_aggregation = aggregate_values(curr_aggregation, parameters)
                    print('Sending parameters to worker {}:{}'.format(client_address[0],client_address[1]))
                    # send accumulated params
                    msg = get_formated_message(current_status, len(workers), current_step, acc_aggregation)
                    server.send_message(msg, client_address)
                else:
                    print('Worker {} is already aggregated'.format(client_address))
                    send_error(server, client_address, workers=len(workers))

            if len(workers) == worker_num:
                print('All workers aggregated in step:', current_step)
                acc_aggregation = get_medians(curr_aggregation)
                curr_aggregation = []
                print('Next step')
                current_step += 1                
                workers = []
                if current_step == iterations:
                    print('Finished')
                    sys.exit()
                    current_status = STATE_FINISHED

        elif current_status == STATE_FINISHED:
            print('Finished')
            sys.exit()
            pass
        else:
            print('Unknown key')
            sys.exit()

    server.stop()


if __name__ == '__main__':
    main()
