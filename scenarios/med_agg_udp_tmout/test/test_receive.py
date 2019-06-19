import sys
import os
import socket

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../utils'))
from python_sockets.server import UDPServer


PORT = 12344
HOST = socket.gethostbyname('')
# HOST = '10.0.1.1'
def main():
    server = UDPServer(PORT, HOST, debug=True)
    server.start()
    while True:
        print('Waiting for messages...')
        msg, client_address = server.receive_message(send_answer=False)
        print(client_address)
        print(msg)





if __name__ == '__main__':
    main()
