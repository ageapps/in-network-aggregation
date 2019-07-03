#!/usr/bin/env python2

import sys
import os

import argparse
import os
import sys
from time import sleep
import subprocess



STATE_WAITING = 0
STATE_SETUP = 1
STATE_LEARNING = 2
STATE_ERROR = 3
STATE_WRONG_STEP = 4

# counters
NODES_IDX = 2
STEP_IDX = 3
STATE_IDX = 4

# parameter indexes
NODE_NUMBER_IDX = 0
ITERATIONS_IDX = 1
ETA_IDX = 2
INPUT_SIZE_IDX = 3
INPUT_FEATURES_IDX = 4
OUTPUT_CLASSES_IDX = 5
SCALE_FACTOR_IDX = 6

# parameter values
worker_number = 5
iterations = 50
eta = 0.001
input_size = 200
input_features = 5
output_classes = 1
scale_factor = 1000


def read_register(register, idx=-1, thrift_port=9090, sw=None):
    if sw: thrift_port = sw.thrift_port
    p = subprocess.Popen(['simple_switch_CLI', '--thrift-port', str(thrift_port)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if idx >= 0:
        stdout, stderr = p.communicate(input='register_read %s %d' % (register, idx))
        reg_val = filter(lambda l: ' %s[%d]' % (register, idx) in l, stdout.split('\n'))[0].split('= ', 1)[1]
        return long(reg_val)
    else:
        stdout, stderr = p.communicate(input='register_read %s' % (register))
        return filter(lambda l: ' %s=' % (register) in l, stdout.split('\n'))[0].split('= ', 1)[1]

def write_register(register, idx, value, thrift_port=9090, sw=None):
    if sw: thrift_port = sw.thrift_port
    p = subprocess.Popen(['simple_switch_CLI', '--thrift-port', str(thrift_port)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate(input='register_write %s %d %d' % (register, idx, value))
    success = not bool(stderr) and not 'Error' in stdout
    if not success:
        print(stdout)
        print(stderr)
    return success

def reset_learning():
    print("------- RESETING LEARNING -------")
    assert write_register('MyIngress.aggregation.counters_register', NODES_IDX, 0), 'Error resetting node count'
    print('Nodes reset')
    assert write_register('MyIngress.aggregation.counters_register', STEP_IDX, 0), 'Error resetting step count'
    print('Step reset')
    assert write_register('MyIngress.aggregation.counters_register', STATE_IDX, STATE_WAITING), 'Error resetting state'
    print('State reset')

def configure_learning():
    print("------- CONFIGURING LEARNING -------")
    assert write_register('MyIngress.aggregation.parameter_register', NODE_NUMBER_IDX, worker_number), 'Error setting node number'
    print('worker_number: {}'.format(worker_number))
    assert write_register('MyIngress.aggregation.parameter_register', ITERATIONS_IDX, iterations), 'Error setting interations'
    print('iterations: {}'.format(iterations))
    assert write_register('MyIngress.aggregation.parameter_register', ETA_IDX, int(eta*scale_factor)), 'Error setting eta'
    print('eta: {}'.format(eta))
    assert write_register('MyIngress.aggregation.parameter_register', INPUT_FEATURES_IDX, input_features), 'Error setting input features'
    print('input_features: {}'.format(input_features))
    assert write_register('MyIngress.aggregation.parameter_register', OUTPUT_CLASSES_IDX, output_classes), 'Error setting output classes'
    print('output_classes: {}'.format(output_classes))
    assert write_register('MyIngress.aggregation.parameter_register', SCALE_FACTOR_IDX, scale_factor), 'Error setting scale factor'
    print('scale_factor: {}'.format(scale_factor))
    assert write_register('MyIngress.aggregation.counters_register', STATE_IDX, STATE_SETUP), 'Error setting state'
    print('state: {}'.format('setup'))


def main():

    
    try:
        reset_learning()
        configure_learning()
        while True:
            sleep(2)
            print('\n----- Reading Registers -----')
            print('State: %d | Nodes: %d | Step: %d'  % \
            (read_register('MyIngress.aggregation.counters_register', STATE_IDX), 
            read_register('MyIngress.aggregation.counters_register', NODES_IDX),
            read_register('MyIngress.aggregation.counters_register', STEP_IDX)))
            print('W : %s' % (read_register('MyIngress.aggregation.acc_aggregation',-1)))

    except KeyboardInterrupt:
        print(' Shutting down.')

if __name__ == '__main__':
    main()
