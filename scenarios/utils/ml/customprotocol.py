import struct
import re

STATE_SETUP = 0
STATE_LEARNING = 1
STATE_FINISHED = 2
STATE_ERROR = 3
STATE_WRONG_STEP = 4
# this state is only used by workers
STATE_WAITING = 10


class CustomProtocol(object):
    """ Protocol based on  max_packet_size in bytes

    The packet has the following structure

    |   status 1   |
    |     step 4       |   param0 4   |   param1 4   |
    |     param2 4    |   param3 4   |   param4 4   |
    """
    def __init__(self, header_mask='! B i i i i i i', encoding='utf-8', debug=False):
        self.fragmented_flag = 1
        self.header_mask = header_mask
        self.header_elements = len(re.sub('[^A-Za-z?]+', '', header_mask))
        self.header_size = struct.calcsize(header_mask)
        self.debug = debug

    def encode(self, values: list) -> bytes:
        assert ( len(values) <= self.header_elements), "Input values are not the correct size: {} | should be: {}".format(len(values), self.header_elements) 
        if len(values) < self.header_elements:
            padding = [0] * (self.header_elements-len(values))
            values.extend(padding)
        return struct.pack(self.header_mask, *values)

    def get_messages_to_send(self, values: list) -> list:
        fragment = self.encode(values)
        if self.debug:
            print("Sending fragment: {}".format(fragment))
        return [fragment]

    def decode(self, msg_bytes):
        assert len(msg_bytes) == self.header_size, "Message received not correct size: {} | should be: {}".format(len(msg_bytes), self.header_size)
        return list(struct.unpack(self.header_mask, msg_bytes))
    

    def receive_packet(self, receive_fn):
        result = receive_fn(self.header_size)
        address = None
        if isinstance(result, tuple):
            msg_bytes, address = result
        else:
            msg_bytes = result
        
        if self.debug:
            print("Received: {}".format(msg_bytes))
        return msg_bytes, address

    def receive_from_socket(self, receive_fn) -> (object, tuple):
        """receive message using the given function by the client/server
        
        Raises:
            Exception: Receiving
        
        Returns:
            (data, address)
        """

        address = None
        msg_bytes, address = self.receive_packet(receive_fn)
        if not len(msg_bytes):
            raise Exception("Error receiving the header")
            return

        data = self.decode(msg_bytes)
        return data, address
