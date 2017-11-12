import socket
import jsonpickle
import time

import TexasHoldEmPoker
from Poker import PokerPlayer

PORTS = [8000, 8001]


def start_server():
    sockets = []
    host = "127.0.0.1"
    print('Host: {}'.format(host))
    print('Ports: {}'.format(PORTS))
    for port in PORTS:
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind((host, port))
        serversocket.listen(5)
        sockets += [serversocket]
    print('server started and listening')
    return sockets


def connect_client(serversocket):
    (clientsocket, address) = serversocket.accept()
    print('connection to {} found!'.format(address))
    return clientsocket


def message_to_client(msg_string, clientsocket):
    clientsocket.send(msg_string.encode())


def answer_from_client(clientsocket):
    ans_string = clientsocket.recv(6).decode()
    return ans_string


def send_table_to_client(table, client):
    table_json = jsonpickle.encode(table)
    client.send(table_json.encode())


def main():
    sockets = start_server()

    clients = [connect_client(s) for s in sockets]
    players = list()
    clients[0].send(bytes(str('You`re player #1').encode('UTF-8')))
    clients[1].send(bytes(str('You`re player #2').encode('UTF-8')))
    for c in clients:
        message_to_client('Your name?', c)
        players.append(answer_from_client(c))
        message_to_client('Name:OK', c)
    runGame(players[0], players[1], clients)


def runGame(p1, p2, clients):
    global player1
    player1 = PokerPlayer(str(p1))
    global player2
    player2 = PokerPlayer(str(p2))
    TexasHoldEmPoker.getWelcomeScreen(player1, player2)
    thePot = TexasHoldEmPoker.Pot()
    blinds = TexasHoldEmPoker.randint(0, 1)

    while not (player1.getChipPile() == 0 or player2.getChipPile() == 0):
        theDeck = TexasHoldEmPoker.Deck()
        theDeck.shuffle()

        blinds += 1
        player1.setBlinds(blinds % 2 == 0)
        player2.setBlinds(blinds % 2 == 1)
        whoIsBigBlind = thePot.whoIsBigBlind(player1, player2)
        player1.betBlinds(thePot)
        player2.betBlinds(thePot)

        TexasHoldEmPoker.getSetUpScreen(player1, player2, whoIsBigBlind)
        if player1.getChipPile() == 0 or player2.getChipPile() == 0:
            break

        player1.dealHand(2, theDeck)
        player2.dealHand(2, theDeck)
        hands = list()
        hands.append(player1.getHand())
        hands.append(player2.getHand())
        ct = 0
        for c in clients:
            c.send(bytes(str("Your cards: ").encode('utf-8') + str(hands[ct][0]).encode('utf-8') + str(" and ").encode(
                'utf-8') + str(hands[ct][1]).encode('utf-8')))
            ct += 1
        hands[0] = player1.getChipPile()
        hands[1] = player2.getChipPile()
        print(hands)
        ct = 0
        for c in clients:
            c.send(bytes(str("Your chip pile: ").encode('utf-8') + str(hands[ct]).encode('utf-8')))
            ct += 1
        testBetMgr(clients, thePot, player1, player2)

        step = 1
        riverCards = TexasHoldEmPoker.River()
        while not (player1.getWinStatus() or player2.getWinStatus()) and step <= 3:
            riverCards.step(step, theDeck)
            if not (player1.isAllIn() or player2.isAllIn()):
                testBetMgr(clients, thePot, player1, player2, riverCards)
            step += 1

        if player1.getWinStatus():
            TexasHoldEmPoker.getWinPotScreen(player1, player2, player1, thePot, riverCards)
            thePot.awardPot(player1)
        elif player2.getWinStatus():
            TexasHoldEmPoker.getWinPotScreen(player1, player2, player2, thePot, riverCards)
            thePot.awardPot(player2)
        else:
            p1combo, p1ranking = player1.evaluate(riverCards.getRiver())
            p2combo, p2ranking = player2.evaluate(riverCards.getRiver())
            if p1ranking > p2ranking:
                TexasHoldEmPoker.getWinPotScreen(player1, player2, player1, thePot, riverCards, p1combo, p2combo)
                thePot.awardPot(player1)
            elif p1ranking < p2ranking:
                TexasHoldEmPoker.getWinPotScreen(player1, player2, player2, thePot, riverCards, p1combo, p2combo)
                print(thePot)
                thePot.awardPot(player2)
            else:
                if p1combo[0] > p2combo[0]:
                    TexasHoldEmPoker.getWinPotScreen(player1, player2, player1, thePot, riverCards, p1combo, p2combo)
                    thePot.awardPot(player1)
                elif p1combo[0] < p2combo[0]:
                    TexasHoldEmPoker.getWinPotScreen(player1, player2, player2, thePot, riverCards, p1combo, p2combo)
                    thePot.awardPot(player2)
                else:
                    if p1ranking == 2 and p2ranking == 2 and p1combo[0] == p2combo[0]:
                        if p1combo[2] > p2combo[2]:
                            TexasHoldEmPoker.getWinPotScreen(player1, player2, player1, thePot, riverCards, p1combo, p2combo)
                            thePot.awardPot(player1)
                        elif p1combo[2] < p2combo[2]:
                            TexasHoldEmPoker.getWinPotScreen(player1, player2, player2, thePot, riverCards, p1combo, p2combo)
                            thePot.awardPot(player2)
                    else:
                        if player1.getHigh()[0] > player2.getHigh()[0]:
                            TexasHoldEmPoker.getWinPotScreen(player1, player2, player1, thePot, riverCards, p1combo, p2combo)
                            thePot.awardPot(player1)
                        elif player1.getHigh()[0] < player2.getHigh()[0]:
                            TexasHoldEmPoker.getWinPotScreen(player1, player2, player2, thePot, riverCards, p1combo, p2combo)
                            thePot.awardPot(player2)
                        else:
                            TexasHoldEmPoker.getWinPotScreen(player1, player2, None, thePot, riverCards, p1combo, p2combo)
                            thePot.splitPot(player1, player2)
        player1.resetAll()
        player2.resetAll()

    if player1.getChipPile() == 0:
        TexasHoldEmPoker.declareChamp(player1, player2, player2)
        return True
    if player2.getChipPile() == 0:
        TexasHoldEmPoker.declareChamp(player1, player2, player1)
        return True


def testBetMgr(clients, thePot, player1, player2, riverCards=None):
    command = ''
    BetManager = {'': -1, 'bet': 0, 'call': 1, 'all-in': 2}

    choiceList1 = ['bet', 'call', 'all-in', 'fold']
    choiceList2 = ['call', 'fold']
    while True:
        command = ""
        if player1.getBigBlind() and len(command) == 0:
            if riverCards != None:
                clients[1].send(bytes(str("Choose from: ").encode('utf-8')))
                TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
                for el in choiceList1:
                    clients[1].send(bytes(str(el).encode('UTF-8')))
                    time.sleep(0.1)
                clients[1].send(bytes(str("Choose?").encode('utf-8')))
                command = str(answer_from_client(clients[1])).replace("b'", "").replace("'", "").replace(" ", "")
                print(command)
                while command == 'remind':
                    hand = player2.getHand()
                    clients[1].send(bytes(str("Your cards: ").encode('utf-8') + str(hand[0]).encode('utf-8') + str(
                        " and ").encode(
                        'utf-8') + str(hand[1]).encode('utf-8')))
                    clients[1].send(bytes(str("Your chip pile: ").encode('utf-8') + str(player2.getChipPile()).encode('utf-8')))
                    for el in choiceList1:
                        clients[1].send(bytes(el.encode('UTF-8')))
                        time.sleep(0.1)
                    clients[1].send(bytes(str("Choose?").encode('utf-8')))
                    command = str(answer_from_client(clients[1])).replace("b'", "").replace("'", "").replace(" ", "")
                    print(command)
            else:
                for el in choiceList1:
                    clients[1].send(bytes(el.encode('UTF-8')))
                    time.sleep(0.1)
                clients[1].send(bytes(str("Choose?").encode('utf-8')))
                command = str(answer_from_client(clients[1])).replace("b'", "").replace("'", "").replace(" ", "")
                print(command)
                while command == 'remind':
                    hand = player2.getHand()
                    clients[1].send(bytes(str("Your cards: ").encode('utf-8') + str(hand[0]).encode('utf-8') + str(
                        " and ").encode(
                        'utf-8') + str(hand[1]).encode('utf-8')))
                    clients[1].send(bytes(str("Your chip pile: ").encode('utf-8') + str(player2.getChipPile()).encode('utf-8')))
                    for el in choiceList1:
                        clients[1].send(bytes(el.encode('UTF-8')))
                        time.sleep(0.1)
                    clients[1].send(bytes(str("Choose?").encode('utf-8')))
                    command = str(answer_from_client(clients[1])).replace("b'", "").replace("'", "").replace(" ", "")
                    print(command)

            if command == 'bet':
                if riverCards != None:
                    TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
                    clients[1].send(bytes(str("Bet 1/2/3 times?: ").encode('utf-8')))
                    multiplyPot = str(answer_from_client(clients[1])).replace("b'","").replace("'","").replace(" ","")
                    print("Multiply pot: " + multiplyPot)
                    TexasHoldEmPoker.getActionScreen('bet x', multiplyPot, player1, player2, player2, thePot,
                                                     riverCards)
                    while multiplyPot == -1:
                        TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
                        hand = player2.getHand()
                        clients[1].send(bytes(str("Your cards: ").encode('utf-8') + str(hand[0]).encode('utf-8') + str(
                            " and ").encode(
                            'utf-8') + str(hand[1]).encode('utf-8')))
                        clients[1].send(bytes(str("Bet 1/2/3 times?: ").encode('utf-8')))
                        multiplyPot = str(answer_from_client(clients[1])).replace("b'","").replace("'","").replace(" ","")
                        print("Multiply pot: " + multiplyPot)
                        TexasHoldEmPoker.getActionScreen(' bet x', multiplyPot, player1, player2, player2, thePot,
                                                         riverCards)
                else:
                    hand = player2.getHand()
                    clients[1].send(bytes(str("Your cards: ").encode('utf-8') + str(hand[0]).encode('utf-8') + str(
                        " and ").encode(
                        'utf-8') + str(hand[1]).encode('utf-8')))
                    clients[1].send(bytes(str("Bet 1/2/3 times?: ").encode('utf-8')))
                    multiplyPot = str(answer_from_client(clients[1])).replace("b'","").replace("'","").replace(" ","")
                    print("Multiply pot: " + multiplyPot)
                    while multiplyPot == -1:
                        hand = player2.getHand()
                        clients[1].send(bytes(str("Your cards: ").encode('utf-8') + str(hand[0]).encode('utf-8') + str(
                            " and ").encode(
                            'utf-8') + str(hand[1]).encode('utf-8')))
                        clients[1].send(bytes(str("Bet 1/2/3 times?: ").encode('utf-8')))
                        multiplyPot = str(answer_from_client(clients[1])).replace("b'","").replace("'","").replace(" ","")
                        print("Multiply pot: " + multiplyPot)
                        TexasHoldEmPoker.getActionScreen(' bet x', multiplyPot, player1, player2, player2, thePot,
                                                         riverCards)
                player2.bet(multiplyPot, thePot)
                print(thePot)
            elif command == 'call':
                TexasHoldEmPoker.getActionScreen(' called !', str(thePot), player1, player2, player2, thePot,
                                                 riverCards)
                player2.call(thePot)
            elif command == 'fold':
                TexasHoldEmPoker.getActionScreen(' fold', "", player1, player2, player2, thePot,
                                                 riverCards)
                player1.setAsWinner()
                break
            elif command == 'all-in':
                TexasHoldEmPoker.getActionScreen(' goes all-in', "", player1, player2, player2, thePot,
                                                 riverCards)
                player2.allIn(thePot, player1)
            else:
                raise ValueError

        optManager = BetManager[command]
        if optManager == 2:
            if riverCards != None:
                TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
                for el in choiceList2:
                    clients[0].send(bytes(el.encode('UTF-8')))
                    time.sleep(0.1)
                clients[0].send(bytes(str("Choose?").encode('utf-8')))
                command = str(answer_from_client(clients[0])).replace("b'", "").replace("'", "").replace(" ", "")
                print(command)
                TexasHoldEmPoker.getActionScreen(" " + command + " ", "", player1, player2, player1, thePot,
                                                 riverCards)
                while command == 'remind':
                    hand = player1.getHand()
                    clients[0].send(bytes(str("Your cards: ").encode('utf-8') + str(hand[0]).encode('utf-8') + str(
                        " and ").encode(
                        'utf-8') + str(hand[1]).encode('utf-8')))
                    clients[0].send(bytes(str("Your chip pile: ").encode('utf-8') + str(player1.getChipPile()).encode('utf-8')))
                    TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
                    for el in choiceList2:
                        clients[0].send(bytes(el.encode('UTF-8')))
                        time.sleep(0.1)
                    clients[0].send(bytes(str("Choose?").encode('utf-8')))
                    command = str(answer_from_client(clients[0])).replace("b'", "").replace("'", "").replace(" ", "")
                    print(command)
                    TexasHoldEmPoker.getActionScreen(" " + command + " ", "", player1, player2, player1, thePot,
                                                     riverCards)
            else:
                for el in choiceList2:
                    clients[0].send(bytes(el.encode('UTF-8')))
                    time.sleep(0.1)
                clients[0].send(bytes(str("Choose?").encode('utf-8')))
                command = str(answer_from_client(clients[0])).replace("b'", "").replace("'", "").replace(" ", "")
                print(command)
                TexasHoldEmPoker.getActionScreen(" " + command + " ", "", player1, player2, player1, thePot,
                                                 riverCards)
                while command == 'remind':
                    hand = player1.getHand()
                    clients[0].send(bytes(str("Your cards: ").encode('utf-8') + str(hand[0]).encode('utf-8') + str(
                        " and ").encode(
                        'utf-8') + str(hand[1]).encode('utf-8')))
                    clients[0].send(
                        bytes(str("Your chip pile: ").encode('utf-8') + str(player1.getChipPile()).encode('utf-8')))
                    for el in choiceList2:
                        clients[0].send(bytes(el.encode('UTF-8')))
                        time.sleep(0.1)
                    clients[0].send(bytes(str("Choose?").encode('utf-8')))
                    command = str(answer_from_client(clients[0])).replace("b'", "").replace("'", "").replace(" ", "")
                    print(command)
                    TexasHoldEmPoker.getActionScreen(" " + command + " ", "", player1, player2, player1, thePot,
                                                     riverCards)
        else:
            if riverCards != None:
                TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
                for el in choiceList1:
                    clients[0].send(bytes(el.encode('UTF-8')))
                    time.sleep(0.1)
                clients[0].send(bytes(str("Choose?").encode('utf-8')))
                command = str(answer_from_client(clients[0])).replace("b'", "").replace("'", "").replace(" ", "")
                print(command)
                TexasHoldEmPoker.getActionScreen(" " + command + " ", "", player1, player2, player1, thePot,
                                                 riverCards)
                while command == 'remind':
                    hand = player1.getHand()
                    clients[0].send(bytes(str("Your cards: ").encode('utf-8') + str(hand[0]).encode('utf-8') + str(
                        " and ").encode(
                        'utf-8') + str(hand[1]).encode('utf-8')))
                    clients[0].send(bytes(str("Your chip pile: ").encode('utf-8') + str(player1.getChipPile()).encode('utf-8')))
                    TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
                    for el in choiceList1:
                        clients[0].send(bytes(el.encode('UTF-8')))
                        time.sleep(0.1)
                    clients[0].send(bytes(str("Choose?").encode('utf-8')))
                    command = str(answer_from_client(clients[0])).replace("b'", "").replace("'", "").replace(" ", "")
                    print(command)
                    TexasHoldEmPoker.getActionScreen(" " + command + " ", "", player1, player2, player1, thePot,
                                                     riverCards)
            else:
                for el in choiceList1:
                    clients[0].send(bytes(el.encode('UTF-8')))
                    time.sleep(0.1)
                clients[0].send(bytes(str("Choose?").encode('utf-8')))
                command = str(answer_from_client(clients[0])).replace("b'", "").replace("'", "").replace(" ", "")
                print(command)
                TexasHoldEmPoker.getActionScreen(" " + command + " ", "", player1, player2, player1, thePot,
                                                 riverCards)
                while command == 'remind':
                    hand = player1.getHand()
                    clients[0].send(bytes(str("Your cards: ").encode('utf-8') + str(hand[0]).encode('utf-8') + str(
                        " and ").encode(
                        'utf-8') + str(hand[1]).encode('utf-8')))
                    clients[0].send(
                        bytes(str("Your chip pile: ").encode('utf-8') + str(player1.getChipPile()).encode('utf-8')))
                    for el in choiceList1:
                        clients[0].send(bytes(el.encode('UTF-8')))
                        time.sleep(0.1)
                    clients[0].send(bytes(str("Choose?").encode('utf-8')))
                    command = str(answer_from_client(clients[0])).replace("b'", "").replace("'", "").replace(" ", "")
                    print(command)
                    TexasHoldEmPoker.getActionScreen(" " + command + " ", "", player1, player2, player1, thePot,
                                                     riverCards)
        if command == 'bet':
            if optManager == 0:
                player1.call(thePot)
            if riverCards != None:
                TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
                clients[0].send(bytes(str("Bet 1/2/3 times?: ").encode('utf-8')))
                multiplyPot = str(answer_from_client(clients[0])).replace("b'","").replace("'","").replace(" ","")
                print("Multiply pot: " + multiplyPot)
                TexasHoldEmPoker.getActionScreen(' bet x', multiplyPot, player1, player2, player1, thePot,
                                                 riverCards)
                while multiplyPot == -1:
                    TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
                    hand = player1.getHand()
                    clients[0].send(bytes(str("Your cards: ").encode('utf-8') + str(hand[0]).encode('utf-8') + str(
                        " and ").encode(
                        'utf-8') + str(hand[1]).encode('utf-8')))
                    clients[0].send(bytes(str("Bet 1/2/3 times?: ").encode('utf-8')))
                    multiplyPot = str(answer_from_client(clients[0])).replace("b'","").replace("'","").replace(" ","")
                    print("Multiply pot: " + multiplyPot)
                    TexasHoldEmPoker.getActionScreen(' bet x', multiplyPot, player1, player2, player1, thePot,
                                                     riverCards)
            else:
                hand = player1.getHand()
                clients[0].send(bytes(str("Your cards: ").encode('utf-8') + str(hand[0]).encode('utf-8') + str(
                    " and ").encode(
                    'utf-8') + str(hand[1]).encode('utf-8')))
                clients[0].send(bytes(str("Bet 1/2/3 times?: ").encode('utf-8')))
                multiplyPot = str(answer_from_client(clients[0])).replace("b'","").replace("'","").replace(" ","")
                while multiplyPot == -1:
                    hand = player1.getHand()
                    clients[0].send(bytes(str("Your cards: ").encode('utf-8') + str(hand[0]).encode('utf-8') + str(
                        " and ").encode(
                        'utf-8') + str(hand[1]).encode('utf-8')))
                    clients[0].send(bytes(str("Bet 1/2/3 times?: ").encode('utf-8')))
                    multiplyPot = str(answer_from_client(clients[0])).replace("b'","").replace("'","").replace(" ","")
                    print("Multiply pot: " + multiplyPot)
                    TexasHoldEmPoker.getActionScreen(' bet x', multiplyPot, player1, player2, player1, thePot,
                                                     riverCards)
            player1.bet(multiplyPot, thePot)
        elif command == 'call':
            TexasHoldEmPoker.getActionScreen(' called !', str(thePot), player1, player2, player2, thePot,
                                             riverCards)
            player1.call(thePot)
            if optManager >= 0:
                break
        elif command == 'fold':
            TexasHoldEmPoker.getActionScreen(' fold', "", player1, player2, player1, thePot,
                                             riverCards)
            player2.setAsWinner()
            break
        elif command == 'all-in':
            TexasHoldEmPoker.getActionScreen(' goes all-in', "", player1, player2, player1, thePot,
                                             riverCards)
            if optManager == 0:
                player1.call(thePot)
            player1.allIn(thePot, player2)

        # player2's turn
        optManager = BetManager[command]
        if optManager == 2:
            if riverCards != None:
                TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
                for el in choiceList2:
                    clients[1].send(bytes(el.encode('UTF-8')))
                    time.sleep(0.1)
                clients[1].send(bytes(str("Choose?").encode('utf-8')))
                command = str(answer_from_client(clients[1])).replace("b'", "").replace("'", "").replace(" ", "")
                print(command)
                TexasHoldEmPoker.getActionScreen(" " + command + " ", "", player1, player2, player2, thePot,
                                                 riverCards)
                while command == 'remind':
                    hand = player2.getHand()
                    clients[1].send(bytes(str("Your cards: ").encode('utf-8') + str(hand[0]).encode('utf-8') + str(
                        " and ").encode(
                        'utf-8') + str(hand[1]).encode('utf-8')))
                    clients[1].send(
                        bytes(str("Your chip pile: ").encode('utf-8') + str(player2.getChipPile()).encode('utf-8')))
                    TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
                    for el in choiceList2:
                        clients[1].send(bytes(el.encode('UTF-8')))
                        time.sleep(0.1)
                    clients[1].send(bytes(str("Choose?").encode('utf-8')))
                    command = str(answer_from_client(clients[1])).replace("b'", "").replace("'", "").replace(" ", "")
                    print(command)
                    TexasHoldEmPoker.getActionScreen(" " + command + " ", "", player1, player2, player2, thePot,
                                                     riverCards)
            else:
                for el in choiceList2:
                    clients[1].send(bytes(el.encode('UTF-8')))
                    time.sleep(0.1)
                clients[1].send(bytes(str("Choose?").encode('utf-8')))
                command = str(answer_from_client(clients[1])).replace("b'", "").replace("'", "").replace(" ", "")
                print(command)
                TexasHoldEmPoker.getActionScreen(" " + command + " ", "", player1, player2, player2, thePot,
                                                 riverCards)
                while command == 'remind':
                    hand = player2.getHand()
                    clients[1].send(bytes(str("Your cards: ").encode('utf-8') + str(hand[0]).encode('utf-8') + str(
                        " and ").encode(
                        'utf-8') + str(hand[1]).encode('utf-8')))
                    clients[1].send(
                        bytes(str("Your chip pile: ").encode('utf-8') + str(player2.getChipPile()).encode('utf-8')))
                    for el in choiceList2:
                        clients[1].send(bytes(el.encode('UTF-8')))
                        time.sleep(0.1)
                    clients[1].send(bytes(str("Choose?").encode('utf-8')))
                    command = str(answer_from_client(clients[1])).replace("b'", "").replace("'", "").replace(" ", "")
                    print(command)
                    TexasHoldEmPoker.getActionScreen(" " + command + " ", "", player1, player2, player2, thePot,
                                                     riverCards)
        else:
            if riverCards != None:
                TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
                for el in choiceList1:
                    clients[1].send(bytes(el.encode('UTF-8')))
                    time.sleep(0.1)
                clients[1].send(bytes(str("Choose?").encode('utf-8')))
                command = str(answer_from_client(clients[1])).replace("b'", "").replace("'", "").replace(" ", "")
                print(command)
                TexasHoldEmPoker.getActionScreen(" " + command + " ", "", player1, player2, player2, thePot,
                                                 riverCards)
                while command == 'remind':
                    hand = player2.getHand()
                    clients[1].send(bytes(str("Your cards: ").encode('utf-8') + str(hand[0]).encode('utf-8') + str(
                        " and ").encode(
                        'utf-8') + str(hand[1]).encode('utf-8')))
                    clients[1].send(
                        bytes(str("Your chip pile: ").encode('utf-8') + str(player2.getChipPile()).encode('utf-8')))
                    TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
                    for el in choiceList1:
                        clients[1].send(bytes(el.encode('UTF-8')))
                        time.sleep(0.1)
                    clients[1].send(bytes(str("Choose?").encode('utf-8')))
                    command = str(answer_from_client(clients[1])).replace("b'", "").replace("'", "").replace(" ", "")
                    print(command)
                    TexasHoldEmPoker.getActionScreen(" " + command + " ", "", player1, player2, player2, thePot,
                                                     riverCards)
            else:
                for el in choiceList1:
                    clients[1].send(bytes(el.encode('UTF-8')))
                    time.sleep(0.1)
                clients[1].send(bytes(str("Choose?").encode('utf-8')))
                command = str(answer_from_client(clients[1])).replace("b'", "").replace("'", "").replace(" ", "")
                print(command)
                TexasHoldEmPoker.getActionScreen(" " + command + " ", "", player1, player2, player2, thePot,
                                                 riverCards)
                while command == 'remind':
                    hand = player2.getHand()
                    clients[1].send(bytes(str("Your cards: ").encode('utf-8') + str(hand[0]).encode('utf-8') + str(
                        " and ").encode(
                        'utf-8') + str(hand[1]).encode('utf-8')))
                    clients[1].send(
                        bytes(str("Your chip pile: ").encode('utf-8') + str(player2.getChipPile()).encode('utf-8')))
                    for el in choiceList1:
                        clients[1].send(bytes(el.encode('UTF-8')))
                        time.sleep(0.1)
                    clients[1].send(bytes(str("Choose?").encode('utf-8')))
                    command = str(answer_from_client(clients[1])).replace("b'", "").replace("'", "").replace(" ", "")
                    print(command)
                    TexasHoldEmPoker.getActionScreen(" " + command + " ", "", player1, player2, player2, thePot,
                                                     riverCards)
        if command == 'bet':
            if optManager == 0:
                player2.call(thePot)
            if riverCards != None:
                TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
                clients[1].send(bytes(str("Bet 1/2/3 times?: ").encode('utf-8')))
                multiplyPot = str(answer_from_client(clients[1])).replace("b'","").replace("'","").replace(" ","")
                print("Multiply pot: " + multiplyPot)
                while multiplyPot == -1:
                    TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
                    hand = player2.getHand()
                    clients[1].send(bytes(str("Your cards: ").encode('utf-8') + str(hand[0]).encode('utf-8') + str(
                        " and ").encode(
                        'utf-8') + str(hand[1]).encode('utf-8')))
                    clients[1].send(bytes(str("Bet 1/2/3 times?: ").encode('utf-8')))
                    multiplyPot = str(answer_from_client(clients[1])).replace("b'","").replace("'","").replace(" ","")
                    print("Multiply pot: " + multiplyPot)
                    TexasHoldEmPoker.getActionScreen(' bet x', multiplyPot, player1, player2, player2, thePot,
                                                     riverCards)
            else:
                hand = player2.getHand()
                clients[1].send(bytes(str("Your cards: ").encode('utf-8') + str(hand[0]).encode('utf-8') + str(
                    " and ").encode(
                    'utf-8') + str(hand[1]).encode('utf-8')))
                clients[1].send(bytes(str("Bet 1/2/3 times?: ").encode('utf-8')))
                multiplyPot = str(answer_from_client(clients[1])).replace("b'","").replace("'","").replace(" ","")
                print("Multiply pot: " + multiplyPot)
                TexasHoldEmPoker.getActionScreen(' bet x', multiplyPot, player1, player2, player2, thePot,
                                                 riverCards)
                while multiplyPot == -1:
                    hand = player2.getHand()
                    clients[1].send(bytes(str("Your cards: ").encode('utf-8') + str(hand[0]).encode('utf-8') + str(
                        " and ").encode(
                        'utf-8') + str(hand[1]).encode('utf-8')))
                    clients[1].send(bytes(str("Bet 1/2/3 times?: ").encode('utf-8')))
                    multiplyPot = str(answer_from_client(clients[1])).replace("b'","").replace("'","").replace(" ","")
                    print("Multiply pot: " + multiplyPot)
                    TexasHoldEmPoker.getActionScreen(' bet x', multiplyPot, player1, player2, player2, thePot,
                                                     riverCards)
            player2.bet(multiplyPot, thePot)
        elif command == 'call':
            TexasHoldEmPoker.getActionScreen(' called !', str(thePot), player1, player2, player2, thePot,
                                             riverCards)
            player2.call(thePot)

            if optManager >= 0:
                break
        elif command == 'fold':
            TexasHoldEmPoker.getActionScreen(' fold', "", player1, player2, player2, thePot,
                                             riverCards)
            player1.setAsWinner()
            break
        elif command == 'all-in':
            if optManager == 0:
                player2.call(thePot)
            TexasHoldEmPoker.getActionScreen(' goes all-in!', "", player1, player2, player2, thePot,
                                             riverCards)
            player2.allIn(thePot, player1)
    thePot.resetCallBet()


if __name__ == '__main__':
    main()
