import time
import sys
import os
import math
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '../../utils'))

from ml.worker import *


HOST = '127.0.0.1'
PORT = 12344

def generate_data(input_size, output_classes):
    X = 2 * np.random.rand(input_size, output_classes)
    Y = 4 + 3*X+np.random.randn(input_size, output_classes)
    return X, Y

def main():
    host = HOST
    port = PORT
    worker_name = 'worker'+datetime.now().strftime('-%H:%M:%S')
    bizantine_factor = 1

    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        print('pass 2 arguments: <server ip>({}) <port>({})'.format(host, port))
        exit(1)

    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    if len(sys.argv) > 3:
        bizantine_factor = int(sys.argv[3])

    worker = Worker(port, host, worker_name, bizantine_factor, median=True)
    try:
        while True:
            worker.run(generate_data)
            print('Worker finished learning process')
    except KeyboardInterrupt:
        print('Stopping worker...')


if __name__ == '__main__':
    main()
