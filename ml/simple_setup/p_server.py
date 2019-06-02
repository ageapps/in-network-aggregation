import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from python_sockets.server import UDPServer
from python_sockets.protocol import FragmentProtocol

from customprotocol import *

PORT = 12344
HOST = ''
UDP_SERVER = True
HEADER_SIZE = 20

iterations = 50
eta = 0.001
input_size = 200
output_size = 1
scale_factor = 1000

eta = int(eta * scale_factor)

learning_parameters = [
    iterations,
    eta,
    input_size,
    output_size,
    scale_factor
]

worker_num = 1

def get_formated_message(status, step, weights):
    values = []
    values.append(status)
    values.append(step)
    values.extend(weights)
    return values

def aggregate_values(params, new_values):
    if len(params) == 0:
        print('Params size is 0', params, new_values)
        return new_values

    assert len(params) == len(
        new_values), 'Sizes are not the same: {}/{}'.format(len(params), len(new_values))

    print('Aggregating parameters')
    for i, param in enumerate(params):
        params[i] = (param + new_values[i])

    return params


def send_error(server, destination):
    server.send_message(get_formated_message(STATE_ERROR,0,[]), destination)

def main():
    proto = CustomProtocol()
    server = UDPServer(PORT,HOST, protocol=proto)
    server.start()
    current_status = STATE_INITIAL
    workers = []
    current_step = 0
    aggregated_params = []
    cached_params = []

    while True:
        msg, client_address = server.receive_message(send_answer=False)
        status = msg[0]
        step = msg[1]
        parameters = msg[2:]

        if status > STATE_FINISHED:
            print('Received error message: {}'.format(msg))
            continue
        
        if status != current_status:
            print('Received message in another state: {}/{}'.format(status, current_status))
            msg = get_formated_message(current_status,0, [])
            server.send_message(msg, client_address)
            continue


        if current_status == STATE_INITIAL:
            # setup phase
            if client_address not in workers:
                print('Registering worker: {}'.format(client_address))
                workers.append(client_address)
                print('Sending parameters')
                msg = get_formated_message(STATE_INITIAL,worker_num, learning_parameters)
                server.send_message(msg, client_address)
            else:
                print('Worker {} is already registered'.format(client_address))
                send_error(server, client_address)

            if len(workers) == worker_num:
                print('All workers registered')
                current_status = STATE_LEARNING
                workers = []

        elif current_status == STATE_LEARNING:

            if int(step) != current_step:
                print('Wrong step {}/{}'.format(step, current_step))
                send_error(server, client_address)
                continue
            else:
                if client_address not in workers:
                    workers.append(client_address)
                    aggregated_params = aggregate_values(aggregated_params, parameters)
                else:
                    print('Worker {} is already aggregated'.format(client_address))
                    send_error(server, client_address)

            if len(workers) == worker_num:
                print('All workers aggregated in step:', current_step)
                cached_params = aggregated_params
                aggregated_params = []
                print('Next step')
                current_step += 1                
                print('Sending parameters to workers')
                msg = get_formated_message(current_status, current_step, cached_params)
                for w in workers:
                    server.send_message(msg, w)
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
