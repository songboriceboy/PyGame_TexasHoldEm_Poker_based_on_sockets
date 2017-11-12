from random import randint


class Card:
    NumToRanking = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                    '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14, }
    SuitToRanking = {'DIAMONDS': 1, 'CLUBS': 2, 'HEARTS': 3, 'SPADES': 4}

    def __init__(self, number, suit):
        self._number = number.upper()
        self._ranking = Card.NumToRanking[self._number]
        self._suit = suit.upper()
        self._suitRanking = Card.SuitToRanking[self._suit]

    def getNumber(self):
        return self._number

    def getSuit(self):
        return self._suit

    def getRanking(self):
        return self._ranking

    def __repr__(self):
        icon = ""
        if self._suit == "DIAMONDS":
            icon = "of DIAMONDS"
        elif self._suit == "CLUBS":
            icon = "of CLUBS"
        elif self._suit == "HEARTS":
            icon = "of HEARTS"
        elif self._suit == "SPADES":
            icon = "of SPADES"
        else:
            pass
        return self._number + " " + icon

    def __lt__(self, other):
        if self._number != other._number:
            return self._ranking < other._ranking
        else:
            return self._suitRanking < other._suitRanking

    def __gt__(self, other):
        if self._number != other._number:
            return self._ranking > other._ranking
        else:
            return self._suitRanking > other._suitRanking

    def __eq__(self, other):
        return self._number == other._number and self._suit == other._suit

    def __hash__(self):
        return hash((self._number, self._ranking, self._suit, self._suitRanking))


class Deck:
    numberRange = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suitRange = ['DIAMONDS', 'CLUBS', 'HEARTS', 'SPADES']

    def __init__(self):
        self._deck = []
        for numberIndex in range(len(Deck.numberRange)):
            for suitIndex in range(len(Deck.suitRange)):
                self._deck.append(Card(Deck.numberRange[numberIndex], Deck.suitRange[suitIndex]))
        self._count = 0

    def shuffle(self):
        temp = self._deck[:]
        for cardIndex in range(len(self._deck)):
            random = randint(0, cardIndex)
            if random != cardIndex:
                temp[cardIndex] = temp[random]
            temp[random] = self._deck[cardIndex]
        self._deck = temp[:]

    def draw(self):
        cardDrawn = self._deck[self._count]
        self._count += 1
        return cardDrawn

    def discard(self):
        self._count += 1

    def reset(self):
        Deck.shuffle(self)
        self._count = 0


class River:
    def __init__(self):
        self._river = []

    def step(self, stepNum, Deck):
        if stepNum == 1:
            for i in range(3):
                self._river.append(Deck.draw())
        elif stepNum == 2 or stepNum == 3:
            Deck.discard()
            self._river.append(Deck.draw())
        else:
            pass

    def showRiver(self):
        print("RIVER")
        for i in range(len(self._river)):
            print(str(i + 1) + ". "),
            print(self._river[i])

    def getRiver(self):
        return self._river


class Hand:
    Rankings = {"SINGLE": 0, "PAIR": 1, "TWOPAIR": 2, "THREE": 3, "STRAIGHT": 4, "FLUSH": 5,
                "FULLHOUSE": 6, "FOUR": 7, "STRAIGHTFLUSH": 8, "ROYALFLUSH": 9}

    def __init__(self):
        self._hand = []
        self._High = []

    def dealHand(self, nCards, Deck):
        for i in range(nCards):
            self._hand.append(Deck.draw())

    def getHand(self):
        return self._hand

    def getHigh(self):
        return self._High

    def evaluate(self, riverCards):
        fullHand = self._hand + riverCards
        fullHand.sort(reverse=True)
        self._High.append(fullHand[0])
        StraightCombo = Hand.checkStraight(self, fullHand)
        FlushCombo = Hand.checkFlush(self, fullHand)
        if StraightCombo is not None and FlushCombo is not None:
            if Hand.checkRoyal(self, StraightCombo, FlushCombo):
                return StraightCombo, Hand.Rankings["ROYALFLUSH"]
            elif StraightCombo == FlushCombo:
                return StraightCombo, Hand.Rankings["STRAIGHTFLUSH"]
            else:
                return FlushCombo, Hand.Rankings["FLUSH"]
        elif StraightCombo is not None and FlushCombo is None:
            return StraightCombo, Hand.Rankings["STRAIGHT"]
        elif StraightCombo is None and FlushCombo is not None:
            return FlushCombo, Hand.Rankings["FLUSH"]
        else:
            cards, freqList = Hand.checkFreq(self, fullHand)
            FourOfKind = Hand.checkFour(self, fullHand, cards, freqList)
            if FourOfKind is not None:
                return FourOfKind, Hand.Rankings["FOUR"]
            ThreeOfKind = Hand.checkThree(self, fullHand, cards, freqList)
            Pair = Hand.checkPair(self, fullHand, cards, freqList)
            if ThreeOfKind is not None and Pair is not None:
                FullHouse = ThreeOfKind + Pair
                return FullHouse, Hand.Rankings["FULLHOUSE"]
            elif ThreeOfKind is not None and Pair is None:
                return ThreeOfKind, Hand.Rankings["THREE"]
            elif ThreeOfKind is None and Pair is not None:
                Pairs = Hand.getAllPairs(self, fullHand, cards, freqList)
                if len(Pairs) > 2:
                    return Pairs, Hand.Rankings["TWOPAIR"]
                else:
                    return Pairs, Hand.Rankings["PAIR"]
            else:
                return self._High, Hand.Rankings["SINGLE"]

    def checkStraight(self, CardList):
        start, end = 0, 5
        while end <= len(CardList):
            fail = False
            temp = CardList[start:end]
            high = temp[start].getRanking()
            for i in range(1, 5):
                if high - 1 != temp[i].getRanking():
                    fail = True
                    break
                else:
                    high = temp[i].getRanking()
            if fail:
                start += 1
                end += 1
                temp = []
            else:
                return (temp)

    def checkFlush(self, CardList):
        nSuit = {"DIAMONDS": 0, "CLUBS": 0, "HEARTS": 0, "SPADES": 0}
        for i in range(len(CardList)):
            suit = CardList[i].getSuit()
            nSuit[suit] += 1
        for tup in nSuit.items():
            if tup[1] >= 5:
                flushSuit = tup[0]
                flushHand = []
                count = 0
                while len(flushHand) < 5:
                    if CardList[count].getSuit() == flushSuit:
                        flushHand.append(CardList[count])
                    count += 1
                return flushHand

    def checkRoyal(self, StraightCombo, FlushCombo):
        if StraightCombo != FlushCombo or StraightCombo[0].getRanking() != 14:
            return False
        return True

    def checkFreq(self, CardList):
        cards, freq = [], []
        for i in range(len(CardList)):
            if CardList[i].getNumber() not in cards:
                cards.append(CardList[i].getNumber())
                freq.append(1)
            else:
                freq[len(freq) - 1] += 1
        return cards, freq

    def checkFour(self, CardList, cards, freq):
        if 4 in freq:
            combo = []
            wantedCardNumber = cards[freq.index(4)]
            for c in CardList:
                if c.getNumber() == wantedCardNumber:
                    combo.append(c)
            return combo

    def checkThree(self, CardList, cards, freq):
        if 3 in freq:
            combo = []
            wantedCardNumber = cards[freq.index(3)]
            for c in CardList:
                if c.getNumber() == wantedCardNumber:
                    combo.append(c)
            return combo

    def checkPair(self, CardList, cards, freq):
        if 2 in freq:
            combo = []
            wantedCardNumber = cards[freq.index(2)]
            for c in CardList:
                if c.getNumber() == wantedCardNumber:
                    combo.append(c)
            return combo

    def getAllPairs(self, CardList, cards, freq):
        pairs = []
        for i in range(len(freq)):
            if freq[i] == 2:
                wantedCardNumber = cards[i]
                for j in range(len(CardList)):
                    if CardList[j].getNumber() == wantedCardNumber:
                        pairs.append(CardList[j])
                if len(pairs) == 4:
                    break
        return pairs


class ChipPile():
    BIG_BLIND = 40
    SMALL_BLIND = 20
    STARTING = 2000

    def __init__(self):
        self._chipPile = ChipPile.STARTING
        self._BigBlind = False

    def getChipPile(self):
        return (self._chipPile)

    def addToChipPile(self, nChips):
        self._chipPile += nChips

    def setBlinds(self, alternate):
        if alternate:
            self._BigBlind = True

    def betBlinds(self, Pot):
        if self._BigBlind:
            Pot.addToPot(PokerPlayer.BIG_BLIND)
            self._chipPile -= PokerPlayer.BIG_BLIND
        else:
            Pot.addToPot(PokerPlayer.SMALL_BLIND)
            self._chipPile -= PokerPlayer.SMALL_BLIND
        if self._chipPile < 0:
            self._chipPile = 0

    def getBigBlind(self):
        return self._BigBlind


class PokerPlayer(Hand, ChipPile):
    def __init__(self, name=""):
        Hand.__init__(self)
        ChipPile.__init__(self)
        self._name = name
        self._AllIn = False
        self._isWinner = False

    def __repr__(self):
        prompt = self._name + ", " + str(self._chipPile) + " chips"
        return prompt

    def getName(self):
        return self._name

    def getWinStatus(self):
        return self._isWinner

    def isAllIn(self):
        return self._AllIn

    def setAsWinner(self):
        self._isWinner = True

    def resetAll(self):
        self._AllIn = False
        self._BigBlind = False
        self._hand = []
        self._High = []
        self._isWinner = False

    def bet(self, multiplyPotBy, pokerPot):
        oldPot = pokerPot.getPot()
        newPot = int(oldPot) + int(oldPot) * int(multiplyPotBy)
        self._chipPile -= (newPot - oldPot)
        if self._chipPile <= 0:
            self._chipPile += (newPot - oldPot)
            PokerPlayer.allIn(self, pokerPot)
        else:
            pokerPot.setCallBet(newPot - oldPot)
            pokerPot.setPot(newPot)
            print(self.getName() + " bets " + str(newPot - oldPot) + "!")

    def call(self, pokerPot):
        oldPot = pokerPot.getPot()
        callBet = pokerPot.getCallBet()
        self._chipPile -= callBet
        if self._chipPile > 0:
            newPot = oldPot + callBet
            pokerPot.setPot(newPot)
            print(self.getName() + " calls " + str(callBet) + "!")
        else:
            self._chipPile += callBet
            PokerPlayer.allIn(self, pokerPot)

    def check(self, pokerPot):
        pokerPot.resetCallBet()
        print(self.getName() + " checks!")

    def allIn(self, pokerPot, other=None):
        self._AllIn = True
        if other == None or self._chipPile < other.getChipPile():
            oldPot = pokerPot.getPot()
            newPot = oldPot + self._chipPile
            pokerPot.setCallBet(self._chipPile)
            self._chipPile = 0
            pokerPot.setPot(newPot)
            print(self.getName() + " is all in! Bets " + str(newPot - oldPot) + "! ")
        else:
            oldPot = pokerPot.getPot()
            newPot = oldPot + other.getChipPile()
            pokerPot.setCallBet(other.getChipPile())
            self._chipPile -= other.getChipPile()
            pokerPot.setPot(newPot)
            print(self.getName() + " is all in! Bets " + str(newPot - oldPot) + "! ")


class Pot:
    def __init__(self):
        self._pot = 0
        self._callBet = 0

    def __repr__(self):
        prompt = "Pot at " + str(self._pot)
        return prompt

    def getPot(self):
        return self._pot

    def getCallBet(self):
        return self._callBet

    def setCallBet(self, nChips):
        self._callBet = nChips

    def resetCallBet(self):
        self._callBet = 0

    def setPot(self, new):
        self._pot = new

    def addToPot(self, nChips):
        self._pot += nChips

    def awardPot(self, whoWon):
        whoWon.addToChipPile(self._pot)
        self._pot = 0
        self._callBet = 0

    def splitPot(self, p1, p2):
        p1.addToChipPile(self._pot // 2)
        p2.addToChipPile(self._pot // 2)
        self._pot = 0
        self._callBet = 0

    def whoIsBigBlind(self, p1, p2):
        if p1.getBigBlind():
            return p1
        else:
            return p2

    def __str__(self):
        return str(self._pot)
