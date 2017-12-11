from random import randint


class Card:
    NUM_TO_RANKING = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                      '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14, }
    SUIT_TO_RANKING = {'DIAMONDS': 1, 'CLUBS': 2, 'HEARTS': 3, 'SPADES': 4}

    def __init__(self, number, suit):
        self.number = number.upper()
        self.ranking = Card.NUM_TO_RANKING[self.number]
        self.suit = suit.upper()
        self.suit_ranking = Card.SUIT_TO_RANKING[self.suit]

    def __repr__(self):
        icon = ""
        if self.suit == "DIAMONDS":
            icon = "of DIAMONDS"
        elif self.suit == "CLUBS":
            icon = "of CLUBS"
        elif self.suit == "HEARTS":
            icon = "of HEARTS"
        elif self.suit == "SPADES":
            icon = "of SPADES"
        else:
            pass
        return self.number + " " + icon

    def __lt__(self, other):
        if self.number != other.number:
            return self.ranking < other.ranking
        else:
            return self.suit_ranking < other.suit_ranking

    def __gt__(self, other):
        if self.number != other.number:
            return self.ranking > other.ranking
        else:
            return self.suit_ranking > other.suit_ranking

    def __eq__(self, other):
        return self.number == other.number and self.suit == other.suit

    def __hash__(self):
        return hash((self.number, self.ranking, self.suit, self.suit_ranking))


class Deck:
    NUMBERS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    SUITS = ['DIAMONDS', 'CLUBS', 'HEARTS', 'SPADES']

    def __init__(self):
        self.deck = []
        for num in range(len(Deck.NUMBERS)):
            for suit in range(len(Deck.SUITS)):
                self.deck.append(Card(Deck.NUMBERS[num], Deck.SUITS[suit]))
        self.count = 0

    def shuffle(self):
        temp = self.deck[:]
        for card in range(len(self.deck)):
            random = randint(0, card)
            if random != card:
                temp[card] = temp[random]
            temp[random] = self.deck[card]
        self.deck = temp[:]

    def draw(self):
        drawn_card = self.deck[self.count]
        self.count += 1
        return drawn_card

    def discard(self):
        self.count += 1

    def reset(self):
        Deck.shuffle(self)
        self.count = 0


class River:
    def __init__(self):
        self.river = []

    def step(self, step_num, deck):
        if step_num == 1:
            for i in range(3):
                self.river.append(deck.draw())
        elif step_num == 2 or step_num == 3:
            deck.discard()
            self.river.append(deck.draw())
        else:
            pass

    def show_river(self):
        print("RIVER")
        for i in range(len(self.river)):
            print(str(i + 1) + ". " + str(self.river[i]))


class Hand:
    RANKINGS = {"SINGLE": 0, "PAIR": 1, "TWOPAIR": 2, "THREE": 3, "STRAIGHT": 4, "FLUSH": 5,
                "FULLHOUSE": 6, "FOUR": 7, "STRAIGHTFLUSH": 8, "ROYALFLUSH": 9}

    def __init__(self):
        self.hand = []
        self.high = []

    def deal_hand(self, nCards, deck):
        for i in range(nCards):
            self.hand.append(deck.draw())

    def evaluate(self, riverCards):
        full_hand = self.hand + riverCards
        full_hand.sort(reverse=True)
        self.high.append(full_hand[0])
        straight_combo = Hand.check_straight(self, full_hand)
        flush_combo = Hand.check_flush(self, full_hand)
        if straight_combo is not None and flush_combo is not None:
            if Hand.check_royal(self, straight_combo, flush_combo):
                return straight_combo, Hand.RANKINGS["ROYALFLUSH"]
            elif straight_combo == flush_combo:
                return straight_combo, Hand.RANKINGS["STRAIGHTFLUSH"]
            else:
                return flush_combo, Hand.RANKINGS["FLUSH"]
        elif straight_combo is not None and flush_combo is None:
            return straight_combo, Hand.RANKINGS["STRAIGHT"]
        elif straight_combo is None and flush_combo is not None:
            return flush_combo, Hand.RANKINGS["FLUSH"]
        else:
            cards, freq_list = Hand.check_freq(self, full_hand)
            four_of_kind = Hand.check_four(self, full_hand, cards, freq_list)
            if four_of_kind is not None:
                return four_of_kind, Hand.RANKINGS["FOUR"]
            three_of_kind = Hand.check_three(self, full_hand, cards, freq_list)
            pair = Hand.check_pair(self, full_hand, cards, freq_list)
            if three_of_kind is not None and pair is not None:
                full_house = three_of_kind + pair
                return full_house, Hand.RANKINGS["FULLHOUSE"]
            elif three_of_kind is not None and pair is None:
                return three_of_kind, Hand.RANKINGS["THREE"]
            elif three_of_kind is None and pair is not None:
                Pairs = Hand.get_all_pairs(self, full_hand, cards, freq_list)
                if len(Pairs) > 2:
                    return Pairs, Hand.RANKINGS["TWOPAIR"]
                else:
                    return Pairs, Hand.RANKINGS["PAIR"]
            else:
                return self.high, Hand.RANKINGS["SINGLE"]

    def check_straight(self, cards):
        start, end = 0, 5
        while end <= len(cards):
            fail = False
            temp = cards[start:end]
            high = temp[start].ranking
            for i in range(1, 5):
                if high - 1 != temp[i].ranking:
                    fail = True
                    break
                else:
                    high = temp[i].ranking
            if fail:
                start += 1
                end += 1
                temp = []
            else:
                return temp

    def check_flush(self, card_list):
        nums_suits = {"DIAMONDS": 0, "CLUBS": 0, "HEARTS": 0, "SPADES": 0}
        for i in range(len(card_list)):
            suit = card_list[i].suit
            nums_suits[suit] += 1
        for tup in nums_suits.items():
            if tup[1] >= 5:
                flush_suit = tup[0]
                flush_hand = []
                count = 0
                while len(flush_hand) < 5:
                    if card_list[count].suit == flush_suit:
                        flush_hand.append(card_list[count])
                    count += 1
                return flush_hand

    def check_royal(self, straight, flush):
        if straight != flush or straight[0].ranking != 14:
            return False
        return True

    def check_freq(self, cards):
        cards, freq = [], []
        for i in range(len(cards)):
            if cards[i].number not in cards:
                cards.append(cards[i].number)
                freq.append(1)
            else:
                freq[len(freq) - 1] += 1
        return cards, freq

    def check_four(self, card_list, cards, freq):
        if 4 in freq:
            combo = []
            wanted_card_number = cards[freq.index(4)]
            for c in card_list:
                if c.number == wanted_card_number:
                    combo.append(c)
            return combo

    def check_three(self, card_list, cards, freq):
        if 3 in freq:
            combo = []
            wanted_card_number = cards[freq.index(3)]
            for c in card_list:
                if c.number == wanted_card_number:
                    combo.append(c)
            return combo

    def check_pair(self, card_list, cards, freq):
        if 2 in freq:
            combo = []
            wanted_card_number = cards[freq.index(2)]
            for c in card_list:
                if c.number == wanted_card_number:
                    combo.append(c)
            return combo

    def get_all_pairs(self, card_list, cards, freq):
        pairs = []
        for i in range(len(freq)):
            if freq[i] == 2:
                wanted_card_number = cards[i]
                for j in range(len(card_list)):
                    if card_list[j].number == wanted_card_number:
                        pairs.append(card_list[j])
                if len(pairs) == 4:
                    break
        return pairs


class chip_pile:
    BIG_BLIND = 40
    SMALL_BLIND = 20
    STARTING = 2000

    def __init__(self):
        self.chip_pile = chip_pile.STARTING
        self.big_blind = False

    def add_to_chip_pile(self, nChips):
        self.chip_pile += nChips

    def set_blinds(self, alternate):
        if alternate:
            self.big_blind = True

    def bet_blinds(self, pot):
        if self.big_blind:
            pot.add_to_pot(PokerPlayer.BIG_BLIND)
            self.chip_pile -= PokerPlayer.BIG_BLIND
        else:
            pot.add_to_pot(PokerPlayer.SMALL_BLIND)
            self.chip_pile -= PokerPlayer.SMALL_BLIND
        if self.chip_pile < 0:
            self.chip_pile = 0


class PokerPlayer(Hand, chip_pile):
    def __init__(self, name=""):
        Hand.__init__(self)
        chip_pile.__init__(self)
        self.name = name
        self.all_in = False
        self.is_winner = False

    def __repr__(self):
        return self.name + ", " + str(self.chip_pile) + " chips"

    def set_as_winner(self):
        self.is_winner = True

    def reset_all(self):
        self.all_in = False
        self.hand = []
        self.high = []
        self.is_winner = False

    def bet(self, multiply_pot_by, pot):
        old_pot = pot.pot
        new_pot = int(old_pot) + int(old_pot) * int(multiply_pot_by)
        self.chip_pile -= (new_pot - old_pot)
        if self.chip_pile <= 0:
            self.chip_pile += (new_pot - old_pot)
            self.allIn(pot)
        else:
            pot.set_call_bet(new_pot - old_pot)
            pot.set_pot(new_pot)
            print(self.name + " bets " + str(new_pot - old_pot) + "!")

    def call(self, pot):
        old_pot = pot.pot
        call_bet = pot.call_bet
        self.chip_pile -= call_bet
        if self.chip_pile > 0:
            new_pot = old_pot + call_bet
            pot.set_pot(new_pot)
            print(self.name + " calls " + str(call_bet) + "!")
        else:
            self.chip_pile += call_bet
            self.allIn(pot)

    def check(self, pot):
        pot.reset_call_bet()
        print(self.name + " checks!")

    def allIn(self, pot, other=None):
        self.all_in = True
        if other is None or self.chip_pile < other.chip_pile:
            old_pot = pot.pot
            new_pot = old_pot + self.chip_pile
            pot.set_call_bet(self.chip_pile)
            self.chip_pile = 0
            pot.set_pot(new_pot)
            print(self.name + " is all in! Bets " + str(new_pot - old_pot) + "! ")
        else:
            old_pot = pot.pot
            new_pot = old_pot + other.chip_pile
            pot.set_call_bet(other.chip_pile)
            self.chip_pile -= other.chip_pile
            pot.set_pot(new_pot)
            print(self.name + " is all in! Bets " + str(new_pot - old_pot) + "! ")


class Pot:
    def __init__(self):
        self.pot = 0
        self.call_bet = 0

    def __repr__(self):
        return "Pot at " + str(self.pot)

    def set_call_bet(self, chips):
        self.call_bet = chips

    def reset_call_bet(self):
        self.call_bet = 0

    def set_pot(self, new):
        self.pot = new

    def add_to_pot(self, chips):
        self.pot += chips

    def award_pot(self, who_won):
        who_won.add_to_chip_pile(self.pot)
        self.pot = 0
        self.call_bet = 0

    def split_pot(self, p1, p2):
        p1.add_to_chip_pile(self.pot // 2)
        p2.add_to_chip_pile(self.pot // 2)
        self.pot = 0
        self.call_bet = 0

    def who_is_big_blind(self, p1, p2):
        if p1.big_blind:
            return p1
        else:
            return p2

    def __str__(self):
        return str(self.pot)
