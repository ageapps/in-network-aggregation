#!/usr/bin/env python2

import argparse
import os
import sys
from time import sleep
import subprocess

def setup_mcast(mcast_id, ports, thrift_port=9090, sw=None):
        if sw: thrift_port = sw.thrift_port
        p = subprocess.Popen(['simple_switch_CLI', '--thrift-port', str(thrift_port)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        entries = []
        s = "mc_mgrp_create %d" % (mcast_id)
        entries.append(s)
        for port in range(1, ports+1):
            s = "mc_node_create %d00 %d" % (port, port)
            entries.append(s)
            s = "mc_node_associate %d %d" % (mcast_id, port-1)
            entries.append(s)
        
        stdout, stderr = p.communicate(input='\n'.join(entries))
    
        if stderr:
            print "Error: " + str(stderr)

        print stdout

       
def mc_dump(thrift_port=9090, sw=None):
    p = subprocess.Popen(['simple_switch_CLI', '--thrift-port', str(thrift_port)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate(input="mc_dump")
    print stdout


def main():
    ports = 5

    if len(sys.argv) > 1:
        ports = int(sys.argv[1])

    try:    
        setup_mcast(1, ports)
        mc_dump()
    except KeyboardInterrupt:
        print " Shutting down."

if __name__ == '__main__':
    main()
