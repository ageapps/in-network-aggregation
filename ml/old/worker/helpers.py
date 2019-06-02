import json

ENCODING = "utf-8"

def get_formated_json_message(json_msg, header_size):
    return get_formated_message(json.dumps(json_msg))


def get_formated_message(msg, header_size):
    msg_len = str(len(msg))
    print("Sending message | length:{} data:{}".format(msg_len, msg))
    if len(msg_len) > header_size:
        print("Message too long | Message: {}".format(msg))
        return ""

    header = msg_len.ljust(header_size)
    return msg, header

def get_message_bytes(msg, header_size):
    if isinstance(msg, str):
        data, header = get_formated_message(msg, header_size)
    else:
        data, header = get_formated_json_message(msg, header_size)
    
    return bytes(data, ENCODING), bytes(header, ENCODING)


def send_message(socket, msg_b, destination, udp=False):
    if udp:
        socket.sendto(msg_b, destination)
    else:
        socket.sendall(msg_b)


def receive_message(socket, header_size):
      msg_header = socket.recv(header_size)
      if not len(msg_header):
          return None

      msg_len = int(msg_header.decode(ENCODING).strip())
      return {"header": msg_len, "data": socket.recv(msg_len).decode(ENCODING)}


def receive_udp_message(socket, header_size):
      msg_header, address = socket.recvfrom(header_size)
      if not len(msg_header):
          return None

      msg_len = int(msg_header.decode(ENCODING).strip())
      msg_data, address = socket.recvfrom(msg_len)
      return {"sender": address, "header": msg_len, "data": msg_data.decode(ENCODING)}

