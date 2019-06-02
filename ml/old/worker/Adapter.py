import socket
import sys

from helpers import *

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)


class PS_Adapter(object):
    
    def __init__(self, port, host="127.0.0.1" , udp=False, header_size = 20):
        self.host = host
        self.port = port
        self.udp = udp
        self.header_size = header_size
        socket_kind = socket.SOCK_DGRAM if udp else socket.SOCK_STREAM 
        try:
            s = socket.socket(socket.AF_INET, socket_kind)
            if not udp:
                s.connect((HOST, PORT))
        except socket.error as err:
            print('Failed to start socket | Error: {}'.format(err))
            sys.exit()

        self.client_socket = s
    
    def send_weights(self, weights):
        msg_b, header_b = get_message_bytes(weights, self.header_size)
        if self.udp:
            socket.sendto(header_b, (self.host, self.port))
            socket.sendto(msg_b, (self.host, self.port))
        else:
            socket.sendall(header_b)
            socket.sendall(msg_b)

