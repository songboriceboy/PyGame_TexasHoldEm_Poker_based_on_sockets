import time

import ConvertString
import GamePainter
from Poker import PokerPlayer
from Server import message_to_client, answer_from_client


def runGame(p1, p2, clients):
    global player1
    player1 = PokerPlayer(str(p1))
    global player2
    player2 = PokerPlayer(str(p2))
    GamePainter.get_welcome_screen(player1, player2)
    pot = GamePainter.Pot()
    blinds = GamePainter.randint(0, 1)

    while not (player1.chip_pile == 0 or player2.chip_pile == 0):
        deck = GamePainter.Deck()
        deck.shuffle()

        blinds += 1
        player1.set_blinds(blinds % 2 == 0)
        player2.set_blinds(blinds % 2 == 1)
        who_is_big_blind = pot.who_is_big_blind(player1, player2)
        player1.bet_blinds(pot)
        player2.bet_blinds(pot)

        GamePainter.get_setup_screen(player1, player2, who_is_big_blind)
        if player1.chip_pile == 0 or player2.chip_pile == 0:
            break

        player1.deal_hand(2, deck)
        player2.deal_hand(2, deck)
        hands = list()
        hands.append(player1.hand)
        hands.append(player2.hand)
        ct = 0
        for c in clients:
            message_to_client(str("Your cards: ") + str(hands[ct][0]) + str(" and ") + str(hands[ct][1]), c)
            ct += 1
        hands[0] = player1.chip_pile
        hands[1] = player2.chip_pile
        print(hands)
        ct = 0
        for c in clients:
            message_to_client(str("Your chip pile: ") + str(hands[ct]), c)
            ct += 1

        step = 1
        river = GamePainter.River()
        bet_manager(clients, pot, player1, player2, river=river)
        while not (player1.is_winner or player2.is_winner) and step <= 3:
            river.step(step, deck)
            if not (player1.all_in or player2.all_in):
                bet_manager(clients, pot, player1, player2, river)
            step += 1

        if player1.is_winner:
            GamePainter.get_win_pot_screen(player1, player2, player1, pot, river)
            pot.award_pot(player1)
        elif player2.is_winner:
            GamePainter.get_win_pot_screen(player1, player2, player2, pot, river)
            pot.award_pot(player2)
        else:
            p1combo, p1ranking = player1.evaluate(river.river)
            p2combo, p2ranking = player2.evaluate(river.river)
            if p1ranking > p2ranking:
                GamePainter.get_win_pot_screen(player1, player2, player1, pot, river, p1combo, p2combo)
                pot.award_pot(player1)
            elif p1ranking < p2ranking:
                GamePainter.get_win_pot_screen(player1, player2, player2, pot, river, p1combo, p2combo)
                pot.award_pot(player2)
            else:
                if p1combo[0] > p2combo[0]:
                    GamePainter.get_win_pot_screen(player1, player2, player1, pot, river, p1combo, p2combo)
                    pot.award_pot(player1)
                elif p1combo[0] < p2combo[0]:
                    GamePainter.get_win_pot_screen(player1, player2, player2, pot, river, p1combo, p2combo)
                    pot.award_pot(player2)
                else:
                    if p1ranking == 2 and p2ranking == 2 and p1combo[0] == p2combo[0]:
                        if p1combo[2] > p2combo[2]:
                            GamePainter.get_win_pot_screen(player1, player2, player1, pot, river, p1combo,
                                                           p2combo)
                            pot.award_pot(player1)
                        elif p1combo[2] < p2combo[2]:
                            GamePainter.get_win_pot_screen(player1, player2, player2, pot, river, p1combo,
                                                           p2combo)
                            pot.award_pot(player2)
                    else:
                        if player1.high[0] > player2.high[0]:
                            GamePainter.get_win_pot_screen(player1, player2, player1, pot, river, p1combo,
                                                           p2combo)
                            pot.award_pot(player1)
                        elif player1.high[0] < player2.high[0]:
                            GamePainter.get_win_pot_screen(player1, player2, player2, pot, river, p1combo,
                                                           p2combo)
                            pot.award_pot(player2)
                        else:
                            GamePainter.get_win_pot_screen(player1, player2, None, pot, river, p1combo,
                                                           p2combo)
                            pot.split_pot(player1, player2)
        player1.reset_all()
        player2.reset_all()

    if player1.chip_pile == 0:
        GamePainter.declare_сhamp(player1, player2, player2)
        time.sleep(2)
        return True
    if player2.chip_pile == 0:
        GamePainter.declare_сhamp(player1, player2, player1)
        time.sleep(2)
        return True


def bet_manager(clients, pot, player1, player2, river=None):
    command = ''
    BET_MANAGER = {'': -1, 'bet': 0, 'call': 1, 'all-in': 2}

    choice_list1 = ['bet', 'call', 'all-in', 'fold', 'remind']
    choice_list2 = ['call', 'fold', 'remind']
    while True:
        command = ""
        if player1.big_blind and len(command) == 0:
            if river is not None:
                message_to_client("Choose from: ", clients[1])
                GamePainter.get_river_screen(player1, player2, pot, river)
                time.sleep(0.1)
                for el in choice_list1:
                    message_to_client(el, clients[1])
                    time.sleep(0.1)
                message_to_client("Choose?", clients[1])

                command = ConvertString.from_bytes_to_string(answer_from_client(clients[1]))
                print(command)
                while command == 'remind':
                    hand = player2.hand
                    message_to_client(str("Your cards: ") + str(hand[0]) + str(" and ") + str(hand[1]), clients[1])
                    time.sleep(0.1)
                    message_to_client(str("Your chip pile: ") + str(player2.chip_pile), clients[1])
                    time.sleep(0.1)
                    for el in choice_list1:
                        message_to_client(el, clients[1])
                        time.sleep(0.1)
                    message_to_client("Choose?", clients[1])
                    command = ConvertString.from_bytes_to_string(answer_from_client(clients[1]))
                    print(command)
            else:
                for el in choice_list1:
                    message_to_client(el, clients[1])
                    time.sleep(0.1)
                message_to_client("Choose?", clients[1])
                command = ConvertString.from_bytes_to_string(answer_from_client(clients[1]))
                print(command)
                while command == 'remind':
                    hand = player2.hand
                    message_to_client(str("Your cards: ") + str(hand[0]) + str(" and ") + str(hand[1]), clients[1])
                    clients[1].send(
                        bytes(str("Your chip pile: ") + str(player2.chip_pile)))
                    for el in choice_list1:
                        message_to_client(el, clients[1])
                        time.sleep(0.1)
                    message_to_client("Choose?", clients[1])
                    command = ConvertString.from_bytes_to_string(answer_from_client(clients[1]))
                    print(command)

            if command == 'bet':
                if river is not None:
                    GamePainter.get_river_screen(player1, player2, pot, river)
                    message_to_client("Bet 1/2/3 times?: ", clients[1])
                    multiply_pot = str(answer_from_client(clients[1])).replace("b'", "").replace("'", "").replace(" ",
                                                                                                                  "")
                    print("Multiply pot: " + multiply_pot)
                    GamePainter.get_action_screen('bet x', multiply_pot, player1, player2, player2, pot, river)
                else:
                    hand = player2.hand
                    message_to_client(str("Your cards: ") + str(hand[0]) + str(" and ") + str(hand[1]), clients[1])
                    message_to_client("Bet 1/2/3 times?: ", clients[1])
                    multiply_pot = str(answer_from_client(clients[1])).replace("b'", "").replace("'", "").replace(" ",
                                                                                                                  "")
                    print("Multiply pot: " + multiply_pot)
                player2.bet(multiply_pot, pot)
                print(pot)
            elif command == 'call':
                GamePainter.get_action_screen(' called ', str(pot), player1, player2, player2, pot, river)
                player2.call(pot)
            elif command == 'fold':
                GamePainter.get_action_screen(' fold', "", player1, player2, player2, pot, river)
                player1.set_as_winner()
                break
            elif command == 'all-in':
                GamePainter.get_action_screen(' goes all-in', "", player1, player2, player2, pot, river)
                player2.allIn(pot, player1)
            else:
                pass

        option = BET_MANAGER[command]
        if option == 2:
            if river is not None:
                GamePainter.get_river_screen(player1, player2, pot, river)
                for el in choice_list2:
                    message_to_client(el, clients[0])
                    time.sleep(0.1)
                message_to_client("Choose?", clients[0])
                command = ConvertString.from_bytes_to_string(answer_from_client(clients[0]))
                print(command)
                GamePainter.get_action_screen(" " + command + " ", "", player1, player2, player1, pot, river)
                while command == 'remind':
                    hand = player1.hand
                    message_to_client(str("Your cards: ") + str(hand[0]) + str(" and ") + str(hand[1]), clients[0])
                    message_to_client(str("Your chip pile: ") + str(player1.chip_pile), clients[0])
                    GamePainter.get_river_screen(player1, player2, pot, river)
                    for el in choice_list2:
                        message_to_client(el, clients[0])
                        time.sleep(0.1)
                    message_to_client("Choose?", clients[0])
                    command = ConvertString.from_bytes_to_string(answer_from_client(clients[0]))
                    print(command)
                    GamePainter.get_action_screen(" " + command + " ", "", player1, player2, player1, pot,river)
            else:
                for el in choice_list2:
                    message_to_client(el, clients[0])
                    time.sleep(0.1)
                message_to_client("Choose?", clients[0])
                command = ConvertString.from_bytes_to_string(answer_from_client(clients[0]))
                print(command)
                GamePainter.get_action_screen(" " + command + " ", "", player1, player2, player1, pot,river)
                while command == 'remind':
                    hand = player1.hand
                    message_to_client(str("Your cards: ") + str(hand[0]) + str(" and ") + str(hand[1]), clients[0])
                    message_to_client(str("Your chip pile: ") + str(player1.chip_pile), clients[0])
                    for el in choice_list2:
                        message_to_client(el, clients[0])
                        time.sleep(0.1)
                    message_to_client("Choose?", clients[0])
                    command = ConvertString.from_bytes_to_string(answer_from_client(clients[0]))
                    print(command)
                    GamePainter.get_action_screen(" " + command + " ", "", player1, player2, player1, pot,river)
        else:
            if river is not None:
                GamePainter.get_river_screen(player1, player2, pot, river)
                for el in choice_list1:
                    message_to_client(el, clients[0])
                    time.sleep(0.1)
                message_to_client("Choose?", clients[0])
                command = ConvertString.from_bytes_to_string(answer_from_client(clients[0]))
                print(command)
                GamePainter.get_action_screen(" " + command + " ", "", player1, player2, player1, pot,river)
                while command == 'remind':
                    hand = player1.hand
                    message_to_client(str("Your cards: ") + str(hand[0]) + str(" and ") + str(hand[1]), clients[0])
                    message_to_client(str("Your chip pile: ") + str(player1.chip_pile), clients[0])
                    GamePainter.get_river_screen(player1, player2, pot, river)
                    for el in choice_list1:
                        message_to_client(el, clients[0])
                        time.sleep(0.1)
                    message_to_client("Choose?", clients[0])
                    command = ConvertString.from_bytes_to_string(answer_from_client(clients[0]))
                    print(command)
                    GamePainter.get_action_screen(" " + command + " ", "", player1, player2, player1, pot,river)
            else:
                for el in choice_list1:
                    message_to_client(el, clients[0])
                    time.sleep(0.1)
                message_to_client("Choose?", clients[0])
                command = ConvertString.from_bytes_to_string(answer_from_client(clients[0]))
                print(command)
                GamePainter.get_action_screen(" " + command + " ", "", player1, player2, player1, pot,river)
                while command == 'remind':
                    hand = player1.hand
                    message_to_client(str("Your cards: ") + str(hand[0]) + str(" and ") + str(hand[1]), clients[0])
                    clients[0].send(
                        bytes(str("Your chip pile: ") + str(player1.chip_pile)))
                    for el in choice_list1:
                        message_to_client(el, clients[0])
                        time.sleep(0.1)
                    message_to_client("Choose?", clients[0])
                    command = ConvertString.from_bytes_to_string(answer_from_client(clients[0]))
                    print(command)
                    GamePainter.get_action_screen(" " + command + " ", "", player1, player2, player1, pot,river)
        if command == 'bet':
            if option == 0:
                player1.call(pot)
            if river is not None:
                GamePainter.get_river_screen(player1, player2, pot, river)
                message_to_client("Bet 1/2/3 times?: ", clients[0])
                multiply_pot = ConvertString.from_bytes_to_string(answer_from_client(clients[0]))
                print("Multiply pot: " + multiply_pot)
                GamePainter.get_action_screen(' bet x', multiply_pot, player1, player2, player1, pot,river)
            else:
                hand = player1.hand
                message_to_client(str("Your cards: ") + str(hand[0]) + str(" and ") + str(hand[1]), clients[0])
                message_to_client("Bet 1/2/3 times?: ", clients[0])
                multiply_pot = ConvertString.from_bytes_to_string(answer_from_client(clients[0]))
            player1.bet(multiply_pot, pot)
        elif command == 'call':
            GamePainter.get_action_screen(' called ', str(pot), player1, player2, player2, pot,river)
            player1.call(pot)
            if option >= 0:
                break
        elif command == 'fold':
            GamePainter.get_action_screen(' fold', "", player1, player2, player1, pot,river)
            player2.set_as_winner()
            break
        elif command == 'all-in':
            GamePainter.get_action_screen(' goes all-in', "", player1, player2, player1, pot,river)
            if option == 0:
                player1.call(pot)
            player1.allIn(pot, player2)

        # Player2's turn
        option = BET_MANAGER[command]
        if option == 2:
            if river is not None:
                GamePainter.get_river_screen(player1, player2, pot, river)
                for el in choice_list2:
                    message_to_client(el, clients[1])
                    time.sleep(0.1)
                message_to_client("Choose?", clients[1])
                command = ConvertString.from_bytes_to_string(answer_from_client(clients[1]))
                print(command)
                GamePainter.get_action_screen(" " + command + " ", "", player1, player2, player2, pot,river)
                while command == 'remind':
                    hand = player2.hand
                    message_to_client(str("Your cards: ") + str(hand[0]) + str(" and ") + str(hand[1]), clients[1])
                    message_to_client(str("Your chip pile: ") + str(player2.chip_pile), clients[1])
                    GamePainter.get_river_screen(player1, player2, pot, river)
                    for el in choice_list2:
                        message_to_client(el, clients[1])
                        time.sleep(0.1)
                    message_to_client("Choose?", clients[1])
                    command = ConvertString.from_bytes_to_string(answer_from_client(clients[1]))
                    print(command)
                    GamePainter.get_action_screen(" " + command + " ", "", player1, player2, player2, pot,river)
            else:
                for el in choice_list2:
                    message_to_client(el, clients[1])
                    time.sleep(0.1)
                message_to_client("Choose?", clients[1])
                command = ConvertString.from_bytes_to_string(answer_from_client(clients[1]))
                print(command)
                GamePainter.get_action_screen(" " + command + " ", "", player1, player2, player2, pot,river)
                while command == 'remind':
                    hand = player2.hand
                    message_to_client(str("Your cards: ") + str(hand[0]) + str(" and ") + str(hand[1]), clients[1])
                    message_to_client(str("Your chip pile: ") + str(player2.chip_pile), clients[1])
                    for el in choice_list2:
                        message_to_client(el, clients[1])
                        time.sleep(0.1)
                    message_to_client("Choose?", clients[1])
                    command = ConvertString.from_bytes_to_string(answer_from_client(clients[1]))
                    print(command)
                    GamePainter.get_action_screen(" " + command + " ", "", player1, player2, player2, pot,river)
        else:
            if river is not None:
                GamePainter.get_river_screen(player1, player2, pot, river)
                for el in choice_list1:
                    message_to_client(el, clients[1])
                    time.sleep(0.1)
                message_to_client("Choose?", clients[1])
                command = ConvertString.from_bytes_to_string(answer_from_client(clients[1]))
                print(command)
                GamePainter.get_action_screen(" " + command + " ", "", player1, player2, player2, pot,river)
                while command == 'remind':
                    hand = player2.hand
                    message_to_client(str("Your cards: ") + str(hand[0]) + str(" and ") + str(hand[1]), clients[1])
                    message_to_client(str("Your chip pile: ") + str(player2.chip_pile), clients[1])
                    GamePainter.get_river_screen(player1, player2, pot, river)
                    for el in choice_list1:
                        message_to_client(el, clients[1])
                        time.sleep(0.1)
                    message_to_client("Choose?", clients[1])
                    command = ConvertString.from_bytes_to_string(answer_from_client(clients[1]))
                    print(command)
                    GamePainter.get_action_screen(" " + command + " ", "", player1, player2, player2, pot,river)
            else:
                for el in choice_list1:
                    message_to_client(el, clients[1])
                    time.sleep(0.1)
                message_to_client("Choose?", clients[1])
                command = ConvertString.from_bytes_to_string(answer_from_client(clients[1]))
                print(command)
                GamePainter.get_action_screen(" " + command + " ", "", player1, player2, player2, pot,river)
                while command == 'remind':
                    hand = player2.hand
                    message_to_client(str("Your cards: ") + str(hand[0]) + str(" and ") + str(hand[1]), clients[1])
                    clients[1].send(
                        bytes(str("Your chip pile: ") + str(player2.chip_pile)))
                    for el in choice_list1:
                        message_to_client(el, clients[1])
                        time.sleep(0.1)
                    message_to_client("Choose?", clients[1])
                    command = ConvertString.from_bytes_to_string(answer_from_client(clients[1]))
                    print(command)
                    GamePainter.get_action_screen(" " + command + " ", "", player1, player2, player2, pot,river)
        if command == 'bet':
            if option == 0:
                player2.call(pot)
            if river is not None:
                GamePainter.get_river_screen(player1, player2, pot, river)
                message_to_client("Bet 1/2/3 times?: ", clients[1])
                multiply_pot = ConvertString.from_bytes_to_string(answer_from_client(clients[1]))
                print("Multiply pot: " + multiply_pot)
            else:
                hand = player2.hand
                message_to_client(str("Your cards: ") + str(hand[0]) + str(" and ") + str(hand[1]), clients[1])
                message_to_client("Bet 1/2/3 times?: ", clients[1])
                multiply_pot = ConvertString.from_bytes_to_string(answer_from_client(clients[1]))
                print("Multiply pot: " + multiply_pot)
                GamePainter.get_action_screen(' bet x', multiply_pot, player1, player2, player2, pot,river)
            player2.bet(multiply_pot, pot)
        elif command == 'call':
            GamePainter.get_action_screen(' called ', str(pot), player1, player2, player2, pot,river)
            player2.call(pot)

            if option >= 0:
                break
        elif command == 'fold':
            GamePainter.get_action_screen(' fold', "", player1, player2, player2, pot,river)
            player1.set_as_winner()
            break
        elif command == 'all-in':
            if option == 0:
                player2.call(pot)
            GamePainter.get_action_screen(' goes all-in with ', "", player1, player2, player2, pot,river)
            player2.allIn(pot, player1)
    pot.reset_call_bet()
