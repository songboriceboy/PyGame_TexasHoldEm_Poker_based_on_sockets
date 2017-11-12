import socket

import jsonpickle

PORTS = [8000, 8001]


def connect_to_server():
    host = input('Host address: ')
    if host == '':
        host = '127.0.0.1'
    port = int(input('Port number: '))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((host, port))
    return server, port



def message_from_server(s):
    return s.recv(2048).decode()


def answer_to_server(msg_string, server):
    msg_string += ' '  # make sure something goes across
    server.send(msg_string.encode())


def process_server_message(msg, server, port):
    if msg[0] == '{':
        table = jsonpickle.decode(msg)
    elif '?' in msg:
        answer = input(msg)
        answer_to_server(answer, server)
    else:
        print(msg)


def main():
    skt, port = connect_to_server()

    while True:
        message = message_from_server(skt)
        if len(message) > 0:
            process_server_message(message, skt, port)


if __name__ == '__main__':
    main()