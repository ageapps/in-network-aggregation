import time
import sys
import os
import math
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from mini_ml_framework.modules.helpers import *
from mini_ml_framework.modules.trainer import trainBatchGD, trainGD
from mini_ml_framework.modules import Linear, LossMSE, ReLu, Tanh, Sequential
from customprotocol import *
from python_sockets.client import Client


HOST = 'localhost'
PORT = 12344
QUEUE_SIZE = 5
UDP_CLIENT = True
HEADER_SIZE = 20
scale_factor = 1
worker_number = 1
client = None

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


def get_formated_message(status, step, weights):
    values = []
    values.append(status)
    values.append(step)
    values.extend(scale_up(weights, scale_factor))
    return values


def on_params_update(update_params, step):
    print('Updating params')
    for i, current_param in enumerate(update_params):
        if len(current_param) == 0:
            continue

        current_param = current_param.tolist()
        columns = len(current_param[0])
        for c in range(columns):
            # get values by column
            w = [row[c] for row in current_param]
            # send weights
            print('Step {} | Sending weights: {}'.format(step, current_param))
            msg = get_formated_message(STATE_LEARNING, step, w)
            answer = client.send_message(msg, wait_answer=True)
            status = answer[0]
            step = answer[1]
            new_parameters = answer[2:]
            # print(new_parameters)
            new_parameters = scale_down(new_parameters, scale_factor)
            print('Got answer: ', answer)
            if status != STATE_LEARNING:
                raise Exception('Error on answer')

            if len(new_parameters) == len(w):
                for j, row in enumerate(param):
                    row[c] = new_parameters[j]

                update_params[i] = np.array(param)
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
    worker_name = 'worker'+datetime.now().strftime('-%H:%M:%S')
    
    if len(sys.argv) > 1:
        host = sys.argv[1]

    proto = CustomProtocol()
    client = Client(PORT, host=host, udp=UDP_CLIENT, protocol=proto)

    print('Initializing worker ' + worker_name)
    while True:
        answer = client.send_message(
            get_formated_message(current_state, 0, []), wait_answer=True)
        status = answer[0]
        step = answer[1]
        new_parameters = answer[2:]

        if status == current_state:
            print('Worker successfully registered')
        else:
            print('Error on setup | message:{}'.format(answer))
            break

        if len(new_parameters) > 0:
            iterations = new_parameters[0]
            eta = new_parameters[1]
            input_size = new_parameters[2]
            output_size = new_parameters[3]
            scale_factor = new_parameters[4]
            eta = eta / scale_factor
            worker_number = step
            print('Parameters | iterations: {} | eta: {} | in: {} | out: {} | scale: {} | workers: {}'.format(
                iterations, eta, input_size, output_size, scale_factor, worker_number))
            break

        else:
            print('Waiting for setup data')
            time.sleep(2)

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
        status = answer[0]
        step = answer[1]
        parameters = answer[2:]
        if status == STATE_LEARNING:
            current_state = STATE_WAITING
            print('Start learning')
            break

        time.sleep(2)

    cost = trainGD(model, optim, X, Y, iterations, eta=eta,
                   update_func=on_params_update, v=False)
    plotCostAndData(model, X, Y, cost, fig_name=worker_name)
    # client.send_message({ 'name': 'Time', 'time': time.time()})


if __name__ == '__main__':
    main()
