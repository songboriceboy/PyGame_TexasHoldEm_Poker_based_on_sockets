import socket
import jsonpickle
import time

import TexasHoldEmPoker
from Poker import PokerPlayer

PORTS = [8000, 8001]


def get_server_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('gmail.com', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def start_server():
    sockets = []
    host = "127.0.0.1"
    # host = get_server_ip()
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
    # Set up players
    global player1
    player1 = PokerPlayer(str(p1))
    global player2
    player2 = PokerPlayer(str(p2))
    # Show welcome screen
    TexasHoldEmPoker.getWelcomeScreen(player1, player2)
    # Set up pot
    thePot = TexasHoldEmPoker.Pot()
    # Set Blinds
    blinds = TexasHoldEmPoker.randint(0, 1)

    while not (player1.getChipPile() == 0 or player2.getChipPile() == 0):
        # Set up and shuffle the deck
        theDeck = TexasHoldEmPoker.Deck()
        theDeck.shuffle()

        # Set up blinds
        blinds += 1
        player1.setBlinds(blinds % 2 == 0)  # if blinds%2==0, then player1 will be the Big Blind
        player2.setBlinds(blinds % 2 == 1)  # else, then player2 will be Big Blind
        whoIsBigBlind = thePot.whoIsBigBlind(player1, player2)
        player1.betBlinds(thePot)
        player2.betBlinds(thePot)

        # Set up user interface
        TexasHoldEmPoker.getSetUpScreen(player1, player2, whoIsBigBlind)
        if player1.getChipPile() == 0 or player2.getChipPile() == 0:
            break

        # Deal Hands
        player1.dealHand(2, theDeck)
        player2.dealHand(2, theDeck)
        # Show Hands
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
        # Bet
        testBetMgr(clients, thePot, player1, player2)

        # Begin River
        step = 1
        riverCards = TexasHoldEmPoker.River()
        while not (player1.getWinStatus() or player2.getWinStatus()) and step <= 3:
            riverCards.step(step, theDeck)
            if not (player1.isAllIn() or player2.isAllIn()):
                testBetMgr(clients, thePot, player1, player2, riverCards)
            step += 1

        # Assess winner
        if player1.getWinStatus():  # if player2 already folded
            TexasHoldEmPoker.getWinPotScreen(player1, player2, player1, thePot, riverCards)
            thePot.awardPot(player1)
        elif player2.getWinStatus():  # if player1 already folded
            TexasHoldEmPoker.getWinPotScreen(player1, player2, player2, thePot, riverCards)
            thePot.awardPot(player2)
        else:
            GusCombo, GusRanking = player1.evaluate(riverCards.getRiver())
            TumCombo, TumRanking = player2.evaluate(riverCards.getRiver())
            if GusRanking > TumRanking:
                TexasHoldEmPoker.getWinPotScreen(player1, player2, player1, thePot, riverCards, GusCombo, TumCombo)
                thePot.awardPot(player1)
            elif GusRanking < TumRanking:
                TexasHoldEmPoker.getWinPotScreen(player1, player2, player2, thePot, riverCards, GusCombo, TumCombo)
                print(thePot)
                thePot.awardPot(player2)
            else:
                if GusCombo[0] > TumCombo[0]:
                    TexasHoldEmPoker.getWinPotScreen(player1, player2, player1, thePot, riverCards, GusCombo, TumCombo)
                    thePot.awardPot(player1)
                elif GusCombo[0] < TumCombo[0]:
                    TexasHoldEmPoker.getWinPotScreen(player1, player2, player2, thePot, riverCards, GusCombo, TumCombo)
                    thePot.awardPot(player2)
                else:
                    if GusRanking == 2 and TumRanking == 2 and GusCombo[0] == TumCombo[0]:
                        # If both have two pairs and the biggest pairs are the same, we need to compare the smaller pairs
                        if GusCombo[2] > TumCombo[2]:
                            TexasHoldEmPoker.getWinPotScreen(player1, player2, player1, thePot, riverCards, GusCombo, TumCombo)
                            thePot.awardPot(player1)
                        elif GusCombo[2] < TumCombo[2]:
                            TexasHoldEmPoker.getWinPotScreen(player1, player2, player2, thePot, riverCards, GusCombo, TumCombo)
                            thePot.awardPot(player2)
                    else:
                        if player1.getHigh()[0] > player2.getHigh()[0]:
                            TexasHoldEmPoker.getWinPotScreen(player1, player2, player1, thePot, riverCards, GusCombo, TumCombo)
                            thePot.awardPot(player1)
                        elif player1.getHigh()[0] < player2.getHigh()[0]:
                            TexasHoldEmPoker.getWinPotScreen(player1, player2, player2, thePot, riverCards, GusCombo, TumCombo)
                            thePot.awardPot(player2)
                        else:
                            TexasHoldEmPoker.getWinPotScreen(player1, player2, None, thePot, riverCards, GusCombo, TumCombo)
                            thePot.splitPot(player1, player2)
        # Reset all poker players' attributes for next round
        player1.resetAll()
        player2.resetAll()

    # See who has no more chips and declare the one with all chips to be the winner. Close game.
    if player1.getChipPile() == 0:
        TexasHoldEmPoker.declareChamp(player1, player2, player2)
        return True
    if player2.getChipPile() == 0:
        TexasHoldEmPoker.declareChamp(player1, player2, player1)
        return True


def testBetMgr(clients, thePot, player1, player2, riverCards=None):
    command = ''
    BetMgmt = {'': -1, 'bet': 0, 'call': 1, 'all-in': 2}

    choiceList1 = ['bet', 'call', 'all-in', 'fold']  # If opponent called or bet, the following options are available.
    choiceList2 = ['call', 'fold']  # If opponent went all-in, the following options are available.
    while True:
        # The player who is not big blind will go first for every betting round.
        if player1.getBigBlind() and len(command) == 0:
            if riverCards != None:
                clients[1].send(bytes(str("Choose from: ").encode('utf-8')))
                TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
                for el in choiceList1:
                    clients[1].send(bytes(el))
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
                    TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
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
                    while multiplyPot == -1:
                        TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
                        hand = player2.getHand()
                        clients[1].send(bytes(str("Your cards: ").encode('utf-8') + str(hand[0]).encode('utf-8') + str(
                            " and ").encode(
                            'utf-8') + str(hand[1]).encode('utf-8')))
                        clients[1].send(bytes(str("Bet 1/2/3 times?: ").encode('utf-8')))
                        multiplyPot = str(answer_from_client(clients[1])).replace("b'","").replace("'","").replace(" ","")
                        print("Multiply pot: " + multiplyPot)
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
                player2.bet(multiplyPot, thePot)
                print(thePot)
            elif command == 'call':
                player2.call(thePot)
            elif command == 'fold':
                player1.setAsWinner()
                break
            elif command == 'all-in':
                player2.allIn(thePot, player1)
            else:
                raise ValueError

        # player1's Turn
        optMgmt = BetMgmt[command]
        if optMgmt == 2:
            if riverCards != None:
                TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
                for el in choiceList2:
                    clients[0].send(bytes(el.encode('UTF-8')))
                    time.sleep(0.1)
                clients[0].send(bytes(str("Choose?").encode('utf-8')))
                command = str(answer_from_client(clients[0])).replace("b'", "").replace("'", "").replace(" ", "")
                print(command)
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
            else:
                for el in choiceList2:
                    clients[0].send(bytes(el.encode('UTF-8')))
                    time.sleep(0.1)
                clients[0].send(bytes(str("Choose?").encode('utf-8')))
                command = str(answer_from_client(clients[0])).replace("b'", "").replace("'", "").replace(" ", "")
                print(command)
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
        else:
            if riverCards != None:
                TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
                for el in choiceList1:
                    clients[0].send(bytes(el.encode('UTF-8')))
                    time.sleep(0.1)
                clients[0].send(bytes(str("Choose?").encode('utf-8')))
                command = str(answer_from_client(clients[0])).replace("b'", "").replace("'", "").replace(" ", "")
                print(command)
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
            else:
                for el in choiceList1:
                    clients[0].send(bytes(el.encode('UTF-8')))
                    time.sleep(0.1)
                clients[0].send(bytes(str("Choose?").encode('utf-8')))
                command = str(answer_from_client(clients[0])).replace("b'", "").replace("'", "").replace(" ", "")
                print(command)
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
        if command == 'bet':
            if optMgmt == 0:
                player1.call(thePot)
            if riverCards != None:
                TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
                clients[0].send(bytes(str("Bet 1/2/3 times?: ").encode('utf-8')))
                multiplyPot = str(answer_from_client(clients[0])).replace("b'","").replace("'","").replace(" ","")
                print("Multiply pot: " + multiplyPot)
                while multiplyPot == -1:
                    TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
                    hand = player1.getHand()
                    clients[0].send(bytes(str("Your cards: ").encode('utf-8') + str(hand[0]).encode('utf-8') + str(
                        " and ").encode(
                        'utf-8') + str(hand[1]).encode('utf-8')))
                    clients[0].send(bytes(str("Bet 1/2/3 times?: ").encode('utf-8')))
                    multiplyPot = str(answer_from_client(clients[0])).replace("b'","").replace("'","").replace(" ","")
                    print("Multiply pot: " + multiplyPot)
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
            player1.bet(multiplyPot, thePot)
        elif command == 'call':
            player1.call(thePot)
            if optMgmt >= 0:
                break
        elif command == 'fold':
            player2.setAsWinner()
            break
        elif command == 'all-in':
            if optMgmt == 0:  # Opponent opted for bet, so must call bet first and then go all-in with remaining chips
                player1.call(thePot)
            player1.allIn(thePot, player2)

        # player2's turn
        optMgmt = BetMgmt[command]
        if optMgmt == 2:
            if riverCards != None:
                TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
                for el in choiceList2:
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
                    clients[1].send(
                        bytes(str("Your chip pile: ").encode('utf-8') + str(player2.getChipPile()).encode('utf-8')))
                    TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
                    for el in choiceList2:
                        clients[1].send(bytes(el.encode('UTF-8')))
                        time.sleep(0.1)
                    clients[1].send(bytes(str("Choose?").encode('utf-8')))
                    command = str(answer_from_client(clients[1])).replace("b'", "").replace("'", "").replace(" ", "")
                    print(command)
            else:
                for el in choiceList2:
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
                    clients[1].send(
                        bytes(str("Your chip pile: ").encode('utf-8') + str(player2.getChipPile()).encode('utf-8')))
                    for el in choiceList2:
                        clients[1].send(bytes(el.encode('UTF-8')))
                        time.sleep(0.1)
                    clients[1].send(bytes(str("Choose?").encode('utf-8')))
                    command = str(answer_from_client(clients[1])).replace("b'", "").replace("'", "").replace(" ", "")
                    print(command)
        else:
            if riverCards != None:
                TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
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
                    clients[1].send(
                        bytes(str("Your chip pile: ").encode('utf-8') + str(player2.getChipPile()).encode('utf-8')))
                    TexasHoldEmPoker.getRiverScreen(player1, player2, thePot, riverCards)
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
                    clients[1].send(
                        bytes(str("Your chip pile: ").encode('utf-8') + str(player2.getChipPile()).encode('utf-8')))
                    for el in choiceList1:
                        clients[1].send(bytes(el.encode('UTF-8')))
                        time.sleep(0.1)
                    clients[1].send(bytes(str("Choose?").encode('utf-8')))
                    command = str(answer_from_client(clients[1])).replace("b'", "").replace("'", "").replace(" ", "")
                    print(command)
        if command == 'bet':
            if optMgmt == 0:
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
            else:
                hand = player2.getHand()
                clients[1].send(bytes(str("Your cards: ").encode('utf-8') + str(hand[0]).encode('utf-8') + str(
                    " and ").encode(
                    'utf-8') + str(hand[1]).encode('utf-8')))
                clients[1].send(bytes(str("Bet 1/2/3 times?: ").encode('utf-8')))
                multiplyPot = str(answer_from_client(clients[1])).replace("b'","").replace("'","").replace(" ","")
                while multiplyPot == -1:
                    hand = player2.getHand()
                    clients[1].send(bytes(str("Your cards: ").encode('utf-8') + str(hand[0]).encode('utf-8') + str(
                        " and ").encode(
                        'utf-8') + str(hand[1]).encode('utf-8')))
                    clients[1].send(bytes(str("Bet 1/2/3 times?: ").encode('utf-8')))
                    multiplyPot = str(answer_from_client(clients[1])).replace("b'","").replace("'","").replace(" ","")
                    print("Multiply pot: " + multiplyPot)
            player2.bet(multiplyPot, thePot)
        elif command == 'call':
            player2.call(thePot)
            if optMgmt >= 0:
                break
        elif command == 'fold':
            player1.setAsWinner()
            break
        elif command == 'all-in':
            if optMgmt == 0:  # Opponent opted for bet, so must call bet first and then go all-in with remaining chips
                player2.call(thePot)
            player2.allIn(thePot, player1)
    thePot.resetCallBet()


if __name__ == '__main__':
    main()
