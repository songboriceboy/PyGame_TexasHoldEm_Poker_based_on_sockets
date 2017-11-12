def testBetMgr(thePot, Gus, Tum, riverCards=None):
    opt = ''
    BetMgmt = {'': -1, 'bet': 0, 'call': 1, 'all-in': 2}

    choiceList1 = ['BET', 'CALL', 'ALL IN', 'FOLD']  # If opponent called or bet, the following options are available.
    choiceList2 = ['CALL', 'FOLD']  # If opponent went all-in, the following options are available.
    while True:
        # The player who is not big blind will go first for every betting round.
        if Gus.getBigBlind() and len(opt) == 0:
            if riverCards != None:
                opt = getOptScreen(Gus, Tum, Tum, thePot, choiceList1, riverCards)
                while opt == 'remind':
                    getShowHandsScreen(Gus, Tum, Tum, riverCards)
                    opt = getOptScreen(Gus, Tum, Tum, thePot, choiceList1, riverCards)
            else:
                opt = getOptScreen(Gus, Tum, Tum, thePot, choiceList1)
                while opt == 'remind':
                    getShowHandsScreen(Gus, Tum, Tum)
                    opt = getOptScreen(Gus, Tum, Tum, thePot, choiceList1)

            if opt == 'bet':
                if riverCards != None:
                    multiplyPot = getBetScreen(Gus, Tum, Tum, thePot, riverCards)
                    while multiplyPot == -1:
                        getShowHandsScreen(Gus, Tum, Tum, riverCards)
                        multiplyPot = getBetScreen(Gus, Tum, Tum, thePot, riverCards)
                else:
                    multiplyPot = getBetScreen(Gus, Tum, Tum, thePot)
                    while multiplyPot == -1:
                        getShowHandsScreen(Gus, Tum, Tum)
                        multiplyPot = getBetScreen(Gus, Tum, Tum, thePot)
                Tum.bet(multiplyPot, thePot)
                print(thePot)
            elif opt == 'call':
                Tum.call(thePot)
            elif opt == 'fold':
                Gus.setAsWinner()
                break
            elif opt == 'all-in':
                Tum.allIn(thePot, Gus)
            else:
                raise ValueError

        # player1's Turn
        optMgmt = BetMgmt[opt]
        if optMgmt == 2:
            if riverCards != None:
                opt = getOptScreen(Gus, Tum, Gus, thePot, choiceList2, riverCards)
                while opt == 'remind':
                    getShowHandsScreen(Gus, Tum, Gus, riverCards)
                    opt = getOptScreen(Gus, Tum, Gus, thePot, choiceList2, riverCards)
            else:
                opt = getOptScreen(Gus, Tum, Gus, thePot, choiceList2)
                while opt == 'remind':
                    getShowHandsScreen(Gus, Tum, Gus, riverCards)
                    opt = getOptScreen(Gus, Tum, Gus, thePot, choiceList2)
        else:
            if riverCards != None:
                opt = getOptScreen(Gus, Tum, Gus, thePot, choiceList1, riverCards)
                while opt == 'remind':
                    getShowHandsScreen(Gus, Tum, Gus, riverCards)
                    opt = getOptScreen(Gus, Tum, Gus, thePot, choiceList1, riverCards)
            else:
                opt = getOptScreen(Gus, Tum, Gus, thePot, choiceList1)
                while opt == 'remind':
                    getShowHandsScreen(Gus, Tum, Gus)
                    opt = getOptScreen(Gus, Tum, Gus, thePot, choiceList1)

        if opt == 'bet':
            if optMgmt == 0:
                Gus.call(thePot)
            if riverCards != None:
                multiplyPot = getBetScreen(Gus, Tum, Gus, thePot, riverCards)
                while multiplyPot == -1:
                    getShowHandsScreen(Gus, Tum, Gus, riverCards)
                    multiplyPot = getBetScreen(Gus, Tum, Gus, thePot, riverCards)
            else:
                multiplyPot = getBetScreen(Gus, Tum, Gus, thePot)
                while multiplyPot == -1:
                    getShowHandsScreen(Gus, Tum, Gus)
                    multiplyPot = getBetScreen(Gus, Tum, Gus, thePot)
            Gus.bet(multiplyPot, thePot)
        elif opt == 'call':
            Gus.call(thePot)
            if optMgmt >= 0:
                break
        elif opt == 'fold':
            Tum.setAsWinner()
            break
        elif opt == 'all-in':
            if optMgmt == 0:  # Opponent opted for bet, so must call bet first and then go all-in with remaining chips
                Gus.call(thePot)
            Gus.allIn(thePot, Tum)

        # player2's turn
        optMgmt = BetMgmt[opt]
        if optMgmt == 2:
            if riverCards != None:
                opt = getOptScreen(Gus, Tum, Tum, thePot, choiceList2, riverCards)
                while opt == 'remind':
                    getShowHandsScreen(Gus, Tum, Tum, riverCards)
                    opt = getOptScreen(Gus, Tum, Tum, thePot, choiceList2, riverCards)
            else:
                opt = getOptScreen(Gus, Tum, Tum, thePot, choiceList2)
                while opt == 'remind':
                    getShowHandsScreen(Gus, Tum, Tum)
                    opt = getOptScreen(Gus, Tum, Tum, thePot, choiceList2)
        else:
            if riverCards != None:
                opt = getOptScreen(Gus, Tum, Tum, thePot, choiceList1, riverCards)
                while opt == 'remind':
                    getShowHandsScreen(Gus, Tum, Tum, riverCards)
                    opt = getOptScreen(Gus, Tum, Tum, thePot, choiceList1, riverCards)

            else:
                opt = getOptScreen(Gus, Tum, Tum, thePot, choiceList1)
                while opt == 'remind':
                    getShowHandsScreen(Gus, Tum, Tum)
                    opt = getOptScreen(Gus, Tum, Tum, thePot, choiceList1)

        if opt == 'bet':
            if optMgmt == 0:
                Tum.call(thePot)
            if riverCards != None:
                multiplyPot = getBetScreen(Gus, Tum, Tum, thePot, riverCards)
                while multiplyPot == -1:
                    getShowHandsScreen(Gus, Tum, Tum, riverCards)
                    multiplyPot = getBetScreen(Gus, Tum, Tum, thePot, riverCards)
            else:
                multiplyPot = getBetScreen(Gus, Tum, Tum, thePot)
                while multiplyPot == -1:
                    getShowHandsScreen(Gus, Tum, Tum)
                    multiplyPot = getBetScreen(Gus, Tum, Tum, thePot)
            Tum.bet(multiplyPot, thePot)
        elif opt == 'call':
            Tum.call(thePot)
            if optMgmt >= 0:
                break
        elif opt == 'fold':
            Gus.setAsWinner()
            break
        elif opt == 'all-in':
            if optMgmt == 0:  # Opponent opted for bet, so must call bet first and then go all-in with remaining chips
                Tum.call(thePot)
            Tum.allIn(thePot, Gus)
    thePot.resetCallBet()