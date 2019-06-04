import time
import sys
import os
import math
import socket
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../utils'))

from mini_ml_framework.modules.helpers import *
from mini_ml_framework.modules.trainer import trainBatchGD, trainGD
from mini_ml_framework.modules import Linear, LossMSE, ReLu, Tanh, Sequential
from customprotocol import *
from python_sockets.client import Client


HOST = '127.0.0.1'
PORT = 12344
UDP_CLIENT = True
scale_factor = 1
worker_number = 1
client = None
MAX_TRIES = 20

def scale_up(elements, factor):
    for i, e in enumerate(elements):
        elements[i] = round(e*factor)
    return elements


def scale_down(elements, factor):
    for i, e in enumerate(elements):
        elements[i] = e / (factor*worker_number)
    return elements


def generate_data(input_size, output_size):
    X = 2 * np.random.rand(input_size, output_size)
    Y = 4 + 3*X+np.random.randn(input_size, output_size)
    return X, Y


def get_formated_message(state, step, weights):
    values = []
    values.append(state)
    values.append(1)
    values.append(step)
    values.extend(scale_up(weights, scale_factor))
    return values

def get_state_str(state):
    state_str = 'UNKNOWN'
    if state == STATE_INITIAL:
        state_str = 'INITIAL'
    elif state == STATE_LEARNING:
        state_str = 'LEARNING'
    elif state == STATE_FINISHED:
        state_str = 'FINISHED'
    elif state == STATE_ERROR:
        state_str = 'ERROR'
    elif state == STATE_WRONG_STEP:
        state_str = 'WRONG_STEP'
    elif state == STATE_WAITING:
        state_str = 'WAITING'
    return state_str


def on_params_update(update_params, step):
    print('Updating params')
    for i, current_param in enumerate(update_params):
        if len(current_param) == 0:
            continue

        current_param = current_param.tolist()
        columns = len(current_param[0])
        
        # get values by column
        for c in range(columns):
            w = [row[c] for row in current_param]
            # send weights
            msg = get_formated_message(STATE_LEARNING, step, w)
            print('Step {} | Sending: {}'.format(step, msg))
            # try aggregation
            for t in range(MAX_TRIES):
                answer = client.send_message(msg, wait_answer=True)
                answer_state = answer[0]
                print('Answer: {} | answer_state: {}'.format(answer, get_state_str(answer_state)))
                if answer_state != STATE_LEARNING:
                    print('trying again...')
                    time.sleep(0.1)
                else:
                    break
            
            answer_workers = answer[1]
            answer_step = answer[2]
            new_parameters = answer[3:]

            if answer_state != STATE_LEARNING:
              raise Exception('Error receiving parameters')
              
            if answer_workers <= 0:
              raise Exception('Error, workers cannot be 0 or less')
            
            

            if answer_step != step:
              raise Exception('Error wrong step | Current: {} | Received: {}'.format(step, answer_step))

            # print(new_parameters)
            new_parameters = scale_down(new_parameters, scale_factor)
            
            
            print('Prams: {} | Lengths: {}/{}'.format(new_parameters, len(new_parameters), len(w)))
            if any(item != 0 for item in new_parameters) and len(new_parameters) >= len(w):
                for j, row in enumerate(current_param):
                    current_param[j][c] = new_parameters[j]

                update_params[i] = np.array(current_param)
            else:
                print('Empty weights')

    print('New update params are:', update_params)
    return update_params


def main():
    global scale_factor
    global worker_number
    global client
    current_state = STATE_INITIAL
    host = HOST
    port = PORT
    worker_name = 'worker'+datetime.now().strftime('-%H:%M:%S')
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        print('pass 2 arguments: <server ip>({}) <port>({})'.format(host, port))
        exit(1)

    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    


    proto = CustomProtocol()
    client = Client(port, host=host, udp=UDP_CLIENT, protocol=proto)

    print('Initializing worker',worker_name,len(sys.argv) )
    new_parameters = []
    register_request = get_formated_message(current_state, 0, new_parameters)
    for i in range(5):
        try:
            answer = client.send_message(register_request, wait_answer=True)
        except socket.timeout:
            print('Timeout {} | trying it again...'.format(i))
            continue

        state = answer[0]
        worker_number = answer[1]
        step = answer[2]
        new_parameters = answer[3:]

        if state == current_state:
            print('Worker successfully registered')
            break
        elif state == STATE_FINISHED:
            print('Starting setup again')
            continue
        else :
            raise Exception('Error on setup | message:{}'.format(answer))

    if len(new_parameters) > 0 and state == current_state:
        iterations = new_parameters[0]
        eta = new_parameters[1]
        input_size = new_parameters[2]
        output_size = new_parameters[3]
        scale_factor = new_parameters[4]
        eta = eta / scale_factor
        print('Parameters | iterations: {} | eta: {} | in: {} | out: {} | scale: {} | workers: {}'.format(
            iterations, eta, input_size, output_size, scale_factor, worker_number))
    else:
        raise Exception('Error with initial parameters')

    x, y = generate_data(input_size, output_size)
    X = standarize(x)
    Y = standarize(y)
    model = Linear(X.shape[1], Y.shape[1])
    optim = LossMSE()

    current_state = STATE_WAITING
    while True:
        print('Waiting to start learning')
        answer = client.send_message(
            get_formated_message(current_state, 0, []), wait_answer=True)
        state = answer[0]
        step = answer[1]
        if state == STATE_LEARNING:
            current_state = STATE_WAITING
            print('Start learning')
            break

        time.sleep(1)

    cost = trainGD(model, optim, X, Y, iterations, eta=eta,
                   update_func=on_params_update, v=False)
    plotCostAndData(model, X, Y, cost, fig_name='fig-'+worker_name)
    # client.send_message({ 'name': 'Time', 'time': time.time()})


if __name__ == '__main__':
    main()
