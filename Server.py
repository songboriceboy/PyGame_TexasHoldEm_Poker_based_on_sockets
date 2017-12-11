import socket

PORTS = [8000, 8001]


def start_server():
    sockets = []
    host = "127.0.0.1"
    print('Host: {}'.format(host))
    print('Ports: {}'.format(PORTS))
    for port in PORTS:
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind((host, port))
        serversocket.listen(2)
        sockets += [serversocket]
    print('Server started and listening')
    return sockets


def connect_client(serversocket):
    (clientsocket, address) = serversocket.accept()
    print('Connection to {} found!'.format(address))
    return clientsocket


def message_to_client(msg_string, clientsocket):
    clientsocket.send(msg_string.encode())


def answer_from_client(clientsocket):
    ans_string = clientsocket.recv(16).decode()
    return ans_string


def main():
    sockets = start_server()

    clients = [connect_client(s) for s in sockets]
    players = list()
    message_to_client('You`re player #1', clients[0])
    message_to_client('You`re player #2', clients[1])
    for c in clients:
        message_to_client('Your name?', c)
        players.append(answer_from_client(c))
        message_to_client('Name: OK', c)
    from GameProcess import runGame
    runGame(players[0], players[1], clients)
    for c in clients:
        c.close()


if __name__ == '__main__':
    main()
