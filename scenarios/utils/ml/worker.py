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
from mini_ml_framework.modules import Linear, LossMSE, ReLu, Tanh, Sequential, Trainer
from python_sockets.client import Client

from .customprotocol import *


UDP_CLIENT = True
MAX_TRIES = 20



class Worker(object):
    def __init__(self, port, host, name, params, bizantine_factor=1, median=False):
        self.port = port
        self.host = host
        self.name = name
        self.bizantine_factor = bizantine_factor
        s_params = ' '.join(["i"]*params)
        self.protocol = CustomProtocol(header_mask='! B B I ' + s_params)
        self.median = median

    def scale_down(self, elements):
        for i, e in enumerate(elements):
            elements[i] = e / (self.scale_factor*self.aggregation_factor*self.bizantine_factor)
        return elements

    def scale_up(self, elements):
        new_e = []
        for i, e in enumerate(elements):
            new_e.append(int(round(e*self.scale_factor*self.bizantine_factor)))
        return new_e

    def get_formated_message(self, state, step, weights):
        values = []
        values.append(state)
        values.append(1)
        values.append(step)
        values.extend(self.scale_up(weights))
        return values

    def get_state_str(self, state):
        state_str = 'UNKNOWN'
        if state == STATE_SETUP:
            state_str = 'SETUP'
        elif state == STATE_LEARNING:
            state_str = 'LEARNING'
        elif state == STATE_WAITING:
            state_str = 'FINISHED'
        elif state == STATE_ERROR:
            state_str = 'ERROR'
        elif state == STATE_WRONG_STEP:
            state_str = 'WRONG_STEP'
        elif state == STATE_WAITING:
            state_str = 'WAITING'
        return state_str

    def flatten(self, params):
        flatted = []
        for i, current_param in enumerate(params):
            if len(current_param) > 0:
                flatted.append(current_param.flatten())
        return np.concatenate(flatted)
        
    def unflatten(self, old_params, flat_params):
        new_params = []
        offset = 0
        for i, current_param in enumerate(old_params):
            if len(current_param) > 0:
                items = current_param.shape[0]*current_param.shape[1]
                new = flat_params[offset:items+offset].reshape(current_param.shape[0], current_param.shape[1])
                offset = items
                new_params.append(new)
            else:
                new_params.append(current_param)
        
        return new_params

    def on_params_update(self, update_params, step):
        print('Updating params')
        update_fparams = self.flatten(update_params)
        
        msg = self.get_formated_message(STATE_LEARNING, step, update_fparams)
        print('Step {} | Sending: {}'.format(step, msg))
        # try aggregation
        for t in range(MAX_TRIES):
            answer = self.client.send_message(msg, wait_answer=True)
            answer_state = answer[0]
            print('Answer: {} | answer_state: {}'.format(answer, self.get_state_str(answer_state)))
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
        new_parameters = self.scale_down(new_parameters)
        print('Prams: {} | Lengths: {}/{}'.format(new_parameters, len(new_parameters), len(update_fparams)))
        if any(item != 0 for item in new_parameters) and len(new_parameters) >= len(update_fparams):
            update_params = self.unflatten(update_params, np.asarray(new_parameters))
        else:
            print('Empty weights')
        
        print('New update params are:', update_params)
        return update_params


    def run(self, fn_data_generator):
        current_state = STATE_SETUP
      
        self.client = Client(self.port, host=self.host, udp=UDP_CLIENT, protocol=self.protocol)

        print('Initializing worker',self.name)
        new_parameters = []
        register_request = self.get_formated_message(current_state, 0, new_parameters)
        answer = None
        failed = 0
        node_index = 0
        while True:

            try:
                answer = self.client.send_message(register_request, wait_answer=True)
            except socket.timeout:
                if failed >= MAX_TRIES:
                    raise Exception('Error on setup | message:{}'.format(answer))

                failed += 1
                print('Timeout {} | trying it again...'.format(failed))
                continue

            state = answer[0]
            worker_number = answer[1]
            step = answer[2]
            new_parameters = answer[3:]

            if self.median:
                self.aggregation_factor = 2
            else:
                self.aggregation_factor = worker_number

            if state == current_state:
                print('Worker successfully registered')
                break
            elif state == STATE_WAITING:
                print('No learing process available')
                time.sleep(2)
            else :
                print('Worker waiting')
                time.sleep(2)

        if answer is None:
            print('Not able to contact server in {}:{}'.format(self.host,self.port))
            exit(0)
        print('State in answer: {}'.format(state))
        if len(new_parameters) > 0 and state == current_state:
            iterations = new_parameters[0]
            eta = new_parameters[1]
            input_size = new_parameters[2]
            input_features = new_parameters[3]
            output_classes = new_parameters[4]
            self.scale_factor = new_parameters[5]
            eta = eta / self.scale_factor
            print('Parameters | iterations: {} | eta: {} | n: {} | in: {} | out: {} | scale: {} | workers: {}'.format(
                iterations, eta, input_size, input_features, output_classes, self.scale_factor, worker_number))
        else:
            raise Exception('Error with initial parameters')

        if (self.bizantine_factor > 1):
            print("++++++++++++++++++++++++++")
            print("THIS IS A BIZANTINE WORKER")
            print("BIZANTINE FACTOR - " + str(self.bizantine_factor))
            print("++++++++++++++++++++++++++")
        node_index = step
        X, Y = fn_data_generator(input_size, input_features, output_classes, node_index)
        model = Linear(X.shape[1], Y.shape[1])

        model1 = Sequential(
            Linear(input_features, 3),
            Tanh(),
            Linear(3, output_classes)
        )
        optim = LossMSE()
        trainer = Trainer(model, optim, v=True)

        current_state = STATE_WAITING
        while True:
            print('Waiting for other workers to start learning')
            answer = self.client.send_message(
                self.get_formated_message(current_state, 0, []), wait_answer=True)
            state = answer[0]
            step = answer[1]
            if state == STATE_LEARNING:
                current_state = STATE_LEARNING
                print('Start learning')
                break

            time.sleep(1)

        # your code
        cost, y_history, t_history = trainer.trainGD(X, Y, iterations, eta=0.001,
                      update_func=self.on_params_update)
        
        
        error = []

        for i, value in enumerate(y_history):
            y_pred = np.asarray(value)
            err = 100* np.sum(abs((y_pred-Y)/y_pred))/len(y_pred)
            error.append(err)


        median_str = 'MEDIAN' if self.median else 'MEAN'
        np.savetxt('error-{}.txt'.format(node_index), np.asarray(error))
        np.savetxt('time-{}.txt'.format(node_index), np.asarray(t_history))
        plotCostAndData(model, X, Y, cost, fig_name='fig-'+str(node_index) , title='Result of '+self.name + ' using ' + median_str)
        
        # client.send_message({ 'name': 'Time', 'time': time.time()})

