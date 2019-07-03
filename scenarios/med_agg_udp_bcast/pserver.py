import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../utils'))

from ml.pserver_med import *

PORT = 12344
HOST = ''

iterations = 50
eta = 0.001
input_size = 200
input_features = 5
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

    pserver = PServer(PORT, HOST)
    pserver.run(worker_num,learning_parameters, bcast=True)
    

if __name__ == '__main__':
    main()
