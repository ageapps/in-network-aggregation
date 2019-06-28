import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../utils'))
from python_sockets.client import Client

HOST = '127.0.0.1'
PORT = 12344
UDP_CLIENT = True


def main():
    host = HOST
    port = PORT
    msg = 'test'
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        msg = sys.argv[2]

    if len(sys.argv) > 3:
        port = sys.argv[3]

    client = Client(port, host=host, udp=UDP_CLIENT, debug=True)
    print("Sending")
    if client.send_message(msg) <= 0:
      print("Error sending packet")
    
    print("Receiving")
    print(client.receive_message()[0])


if __name__ == '__main__':
    main()
