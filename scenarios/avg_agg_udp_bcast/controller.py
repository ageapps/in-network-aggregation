#!/usr/bin/env python2

import argparse
import os
import sys
from time import sleep
import subprocess

def read_register(register, idx, thrift_port=9090, sw=None):
        if sw: thrift_port = sw.thrift_port
        p = subprocess.Popen(['simple_switch_CLI', '--thrift-port', str(thrift_port)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if idx >= 0:
            stdout, stderr = p.communicate(input="register_read %s %d" % (register, idx))
            reg_val = filter(lambda l: ' %s[%d]' % (register, idx) in l, stdout.split('\n'))[0].split('= ', 1)[1]
            return long(reg_val)
        else:
            stdout, stderr = p.communicate(input="register_read %s" % (register))
            return filter(lambda l: ' %s=' % (register) in l, stdout.split('\n'))[0].split('= ', 1)[1]

def main():
    
    try:    
        # Print the tunnel counters every 2 seconds
        while True:
            sleep(2)
            print '\n----- Reading Registers -----'
            print 'State: %d | Nodes: %d | Step: %d'  % \
            (read_register("MyIngress.aggregation.counters_register", 1), 
            read_register("MyIngress.aggregation.counters_register", 2),
            read_register("MyIngress.aggregation.counters_register", 3))
            print 'Acc : %s' % (read_register("MyIngress.aggregation.acc_aggregation",-1))

    except KeyboardInterrupt:
        print " Shutting down."

if __name__ == '__main__':
    main()
