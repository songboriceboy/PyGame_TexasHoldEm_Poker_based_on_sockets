# Stanley Chen
# This program simulates a 2-player game of Texas Hold Em Poker using Pygame 1.9 graphics
# CS3C Final Project
import Server
from Poker import *
from CardSheet import *
import pygame
import sys
from pygame.locals import *
from random import randint

pygame.init()

white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 215, 0)  # WILL APPEAR MORE LIKE GOLD TO ACCOMODATE WHITE TEXT
cyan = (0, 255, 255)
purple = (255, 0, 255)

FPS = 30
DISPWIDTH = 1000
DISPHEIGHT = 700

setDisplay = pygame.display.set_mode((DISPWIDTH, DISPHEIGHT))
pygame.display.set_caption("2-Player Texas Hold'em Poker")

backgroundImage = pygame.image.load("pokerbackground1000by1000.png")
backgroundImage = pygame.transform.scale(backgroundImage, (DISPWIDTH, DISPHEIGHT))
winnerImage = pygame.image.load("DogsPlayinPoker.png")
winnerImage = pygame.transform.scale(winnerImage, (DISPWIDTH, DISPHEIGHT))

CARDWIDTH = 80
CARDHEIGHT = 100
cardBack = pygame.image.load('playingcardback755by1057.png')
cardBack = pygame.transform.scale(cardBack, (CARDWIDTH, CARDHEIGHT))

cardSheet = Sheet("playercards950by320.png")

# Build up the card dictionary where the Card objects are keys and their images are values
# 1. Extract each card image into a list from extract sheet using the CardSheet class
cardImgList = []
indivX, indivY = 0, 0
indivWidth, indivHeight = 73, 99
for i in range(4):
    if i != 0:
        indivX, indivY = 0, (indivY + indivHeight)
    for j in range(13):
        indiv = cardSheet.get_image(indivX, indivY, indivWidth, indivHeight)
        indiv = pygame.transform.scale(indiv, (CARDWIDTH, CARDHEIGHT))
        cardImgList.append(indiv)
        indivX += indivWidth
# 2. Make a list of card objects that follows the order of the card image list
theCardList = []
numberRange = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']  # As seen in picture of card sheet
suitRange = ['CLUBS', 'SPADES', 'HEARTS', 'DIAMONDS']  # As seen in picture of card sheet
for suitIndex in range(len(suitRange)):
    for numberIndex in range(len(numberRange)):
        theCardList.append(Card(numberRange[numberIndex], suitRange[suitIndex]))
# 3. Create dictionary using the previous two lists
theCardDict = dict()
for i in range(len(theCardList)):
    theCardDict[theCardList[i]] = cardImgList[i]


# 1. The following two functions are for printing text to the screen

def makeTxtObjs(text, font, clr):
    textSurface = font.render(text, True, clr)
    return textSurface, textSurface.get_rect()


def msgSurface(text, textClr, CenterXY):
    txtFont = pygame.font.Font('freesansbold.ttf', 20)

    titleTxtSurf, titleTxtRect = makeTxtObjs(text, txtFont, textClr)
    titleTxtRect.center = CenterXY
    setDisplay.blit(titleTxtSurf, titleTxtRect)

    pygame.display.update()


# 2. The following functions are for managing screen output depending on user situation.

def getSetUpScreen(p1, p2, pBigBlind):
    ready = False
    p1Name = p1.getName()
    p1Chips = p1.getChipPile()
    p2Name = p2.getName()
    p2Chips = p2.getChipPile()

    setDisplay.blit(backgroundImage, (0, 0))
    pygame.draw.line(setDisplay, white, (0, 400), (DISPWIDTH, 400), 4)

    setDisplay.blit(cardBack, (50, 250))
    setDisplay.blit(cardBack, (150, 250))

    setDisplay.blit(cardBack, (DISPWIDTH - 150, 250))
    setDisplay.blit(cardBack, (DISPWIDTH - 250, 250))

    msgSurface("RIVER", white, (DISPWIDTH // 2, 50))
    msgSurface(p1Name + ": " + str(p1Chips) + " chips", white, (150, 375))
    msgSurface(p2Name + ": " + str(p2Chips) + " chips", white, (DISPWIDTH - 150, 375))

    if p1 == pBigBlind:
        msgSurface(p1Name + " is Big Blind. Pay 40 chips", white, (DISPWIDTH // 2, 450))
        msgSurface(p2Name + " is Small Blind. Pay 20 chips", white, (DISPWIDTH // 2, 500))
    elif p2 == pBigBlind:
        msgSurface(p2Name + " is Big Blind. Pay 40 chips", white, (DISPWIDTH // 2, 450))
        msgSurface(p1Name + " is Small Blind. Pay 20 chips", white, (DISPWIDTH // 2, 500))

    msgSurface("Click mouse anywhere on screen to continue.", white, (DISPWIDTH // 2, 550))

    while not ready:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                ready = True
            pygame.display.update()


def getShowHandsScreen(p1, p2, pWhoIsLooking, riverCards=None):
    ready = False
    Hide = True
    p1Name = p1.getName()
    p1Chips = p1.getChipPile()
    p2Name = p2.getName()
    p2Chips = p2.getChipPile()

    # get images p's hand
    pHand = pWhoIsLooking.getHand()
    cardImgLHS = theCardDict[pHand[0]]
    cardImgRHS = theCardDict[pHand[1]]

    # Prompt user to be ready to see cards
    setDisplay.blit(backgroundImage, (0, 0))
    pygame.draw.line(setDisplay, white, (0, 400), (DISPWIDTH, 400), 4)
    msgSurface(pWhoIsLooking.getName(), white, (DISPWIDTH // 2, 450))
    msgSurface("Have opponent look away from screen ", white, (DISPWIDTH // 2, 500))
    msgSurface("and then click mouse anywhere on screen to see your cards.", white, (DISPWIDTH // 2, 550))
    while Hide:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                Hide = False
            pygame.display.update()

    setDisplay.blit(backgroundImage, (0, 0))
    pygame.draw.line(setDisplay, white, (0, 400), (DISPWIDTH, 400), 4)

    if p1 == pWhoIsLooking:
        setDisplay.blit(cardImgLHS, (50, 250))
        setDisplay.blit(cardImgRHS, (150, 250))
        setDisplay.blit(cardBack, (DISPWIDTH - 150, 250))
        setDisplay.blit(cardBack, (DISPWIDTH - 250, 250))
    elif p2 == pWhoIsLooking:
        setDisplay.blit(cardImgLHS, (DISPWIDTH - 150, 250))
        setDisplay.blit(cardImgRHS, (DISPWIDTH - 250, 250))
        setDisplay.blit(cardBack, (50, 250))
        setDisplay.blit(cardBack, (150, 250))

    # get images of river
    rCardCoordIncrement = 125
    if riverCards != None:
        rCards = riverCards.getRiver()
        for i in range(len(rCards)):
            rCardImg = theCardDict[rCards[i]]
            setDisplay.blit(rCardImg, (DISPWIDTH // 2 - CARDWIDTH // 2 - 250 + i * rCardCoordIncrement, 100))

    msgSurface("RIVER", white, (DISPWIDTH // 2, 50))
    msgSurface(p1Name + ": " + str(p1Chips) + " chips", white, (150, 375))
    msgSurface(p2Name + ": " + str(p2Chips) + " chips", white, (DISPWIDTH - 150, 375))
    msgSurface("Click mouse anywhere on screen to continue.", white, (DISPWIDTH // 2, 550))

    while not ready:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                ready = True
            pygame.display.update()


def getRiverScreen(p1, p2, thePot, riverCards):
    p1Name = p1.getName()
    p1Chips = p1.getChipPile()
    p2Name = p2.getName()
    p2Chips = p2.getChipPile()


    setDisplay.blit(backgroundImage, (0, 0))
    pygame.draw.line(setDisplay, white, (0, 400), (DISPWIDTH, 400), 4)

    setDisplay.blit(cardBack, (50, 250))
    setDisplay.blit(cardBack, (150, 250))

    setDisplay.blit(cardBack, (DISPWIDTH - 150, 250))
    setDisplay.blit(cardBack, (DISPWIDTH - 250, 250))

    # get images of river
    rCardCoordIncrement = 125
    if riverCards != None:
        rCards = riverCards.getRiver()
        for i in range(len(rCards)):
            rCardImg = theCardDict[rCards[i]]
            setDisplay.blit(rCardImg, (DISPWIDTH // 2 - CARDWIDTH // 2 - 250 + i * rCardCoordIncrement, 100))

    msgSurface("RIVER", white, (DISPWIDTH // 2, 50))
    msgSurface(p1Name + ": " + str(p1Chips) + " chips", white, (150, 375))
    msgSurface(p2Name + ": " + str(p2Chips) + " chips", white, (DISPWIDTH - 150, 375))

    msgSurface("Pot at " + str(thePot.getPot()), white, (DISPWIDTH // 2, 250))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        pygame.display.update()


def getBetScreen(p1, p2, pTurn, thePot, riverCards=None):
    opt = None
    p1Name = p1.getName()
    p1Chips = p1.getChipPile()
    p2Name = p2.getName()
    p2Chips = p2.getChipPile()
    pTurnName = pTurn.getName()

    setDisplay.blit(backgroundImage, (0, 0))
    pygame.draw.line(setDisplay, white, (0, 400), (DISPWIDTH, 400), 4)

    setDisplay.blit(cardBack, (50, 250))
    setDisplay.blit(cardBack, (150, 250))

    setDisplay.blit(cardBack, (DISPWIDTH - 150, 250))
    setDisplay.blit(cardBack, (DISPWIDTH - 250, 250))

    # get images of river
    rCardCoordIncrement = 125
    if riverCards != None:
        rCards = riverCards.getRiver()
        for i in range(len(rCards)):
            rCardImg = theCardDict[rCards[i]]
            setDisplay.blit(rCardImg, (DISPWIDTH // 2 - CARDWIDTH // 2 - 250 + i * rCardCoordIncrement, 100))

    msgSurface("RIVER", white, (DISPWIDTH // 2, 50))
    msgSurface(p1Name + ": " + str(p1Chips) + " chips", white, (150, 375))
    msgSurface(p2Name + ": " + str(p2Chips) + " chips", white, (DISPWIDTH - 150, 375))

    msgSurface("Pot at " + str(thePot.getPot()), white, (DISPWIDTH // 2, 250))
    msgSurface(pTurnName + "'s turn!", white, (DISPWIDTH // 2, 300))

    pygame.draw.rect(setDisplay, yellow, (0, 403, DISPWIDTH // 2, (DISPHEIGHT - 403) // 2))
    msgSurface("1 times the pot?", white, (DISPWIDTH // 4, (403 + (DISPHEIGHT + 403) // 2) // 2))
    pygame.draw.rect(setDisplay, green, (DISPWIDTH // 2, 403, DISPWIDTH // 2, (DISPHEIGHT - 403) // 2))
    msgSurface("2 times the pot?", white, ((DISPWIDTH // 2 + DISPWIDTH) // 2, (403 + (DISPHEIGHT + 403) // 2) // 2))
    pygame.draw.rect(setDisplay, blue, (0, (DISPHEIGHT + 403) // 2, DISPWIDTH, (DISPHEIGHT - 403) // 2))
    msgSurface("3 times the pot?", white, (DISPWIDTH // 2, ((DISPHEIGHT + 403) // 2 + DISPHEIGHT) // 2))

    pygame.draw.rect(setDisplay, cyan, (0, 0, 50, 50))
    pygame.draw.rect(setDisplay, cyan, (DISPWIDTH - 50, 0, 50, 50))

    while opt == None:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouseX, mouseY = event.pos
                if 0 < mouseX < (DISPWIDTH // 2) and 403 < mouseY < ((DISPHEIGHT + 403) // 2):
                    opt = 1
                elif (DISPWIDTH // 2) < mouseX < DISPWIDTH and 403 < mouseY < ((DISPHEIGHT + 403) // 2):
                    opt = 2
                elif 0 < mouseX < DISPWIDTH and ((DISPHEIGHT + 403) // 2) < mouseY < DISPHEIGHT:
                    opt = 3
                elif 0 < mouseX < 50 and 0 < mouseY < 50 or (DISPWIDTH - 50) < mouseX < DISPWIDTH and 0 < mouseY < 50:
                    opt = -1
            pygame.display.update()
            if opt != None:
                break
    return opt


# This function is the bet manager. It handles the bets between the players and calls the previous two functions
# which manages the screen output for betting.



def getWinPotScreen(p1, p2, pWinner, thePot, riverCards=None, p1Combo=None, p2Combo=None):
    ready = False
    p1Name = p1.getName()
    p1Chips = p1.getChipPile()
    p2Name = p2.getName()
    p2Chips = p2.getChipPile()

    setDisplay.blit(backgroundImage, (0, 0))
    pygame.draw.line(setDisplay, white, (0, 400), (DISPWIDTH, 400), 4)

    if p1Combo == None and p2Combo == None:
        setDisplay.blit(cardBack, (50, 250))
        setDisplay.blit(cardBack, (150, 250))

        setDisplay.blit(cardBack, (DISPWIDTH - 150, 250))
        setDisplay.blit(cardBack, (DISPWIDTH - 250, 250))
    else:
        # get images p1's hand
        p1Hand = p1.getHand()
        p1cardImgLHS = theCardDict[p1Hand[0]]
        p1cardImgRHS = theCardDict[p1Hand[1]]

        # get images p2's hand
        p2Hand = p2.getHand()
        p2cardImgLHS = theCardDict[p2Hand[0]]
        p2cardImgRHS = theCardDict[p2Hand[1]]

        setDisplay.blit(p1cardImgLHS, (50, 250))
        setDisplay.blit(p1cardImgRHS, (150, 250))

        setDisplay.blit(p2cardImgLHS, (DISPWIDTH - 150, 250))
        setDisplay.blit(p2cardImgRHS, (DISPWIDTH - 250, 250))

        CCIncrement = 125
        # get images of winning hand
        msgSurface(p1.getName() + " : ", white, (DISPWIDTH // 2 - CARDWIDTH // 2 - 250 + -1 * CCIncrement, 415 + 50))
        for i in range(len(p1Combo)):
            p1CCImg = theCardDict[p1Combo[i]]
            setDisplay.blit(p1CCImg, (DISPWIDTH // 2 - CARDWIDTH // 2 - 250 + i * CCIncrement, 415))

        msgSurface(p2.getName() + " : ", white, (DISPWIDTH // 2 - CARDWIDTH // 2 - 250 + -1 * CCIncrement, 520 + 50))
        for i in range(len(p2Combo)):
            p2CCImg = theCardDict[p2Combo[i]]
            setDisplay.blit(p2CCImg, (DISPWIDTH // 2 - CARDWIDTH // 2 - 250 + i * CCIncrement, 520))

    # get images of river
    rCardCoordIncrement = 125
    if riverCards != None:
        rCards = riverCards.getRiver()
        for i in range(len(rCards)):
            rCardImg = theCardDict[rCards[i]]
            setDisplay.blit(rCardImg, (DISPWIDTH // 2 - CARDWIDTH // 2 - 250 + i * rCardCoordIncrement, 100))

    msgSurface("RIVER", white, (DISPWIDTH // 2, 50))
    msgSurface(p1Name + ": " + str(p1Chips) + " chips", white, (150, 375))
    msgSurface(p2Name + ": " + str(p2Chips) + " chips", white, (DISPWIDTH - 150, 375))
    msgSurface("Pot at " + str(thePot.getPot()), white, (DISPWIDTH // 2, 250))
    if pWinner != None:
        msgSurface(pWinner.getName() + " wins " + str(thePot.getPot()), white, (DISPWIDTH // 2, 650))
    else:
        msgSurface("Split the pot!", white, (DISPWIDTH // 2, 650))
    msgSurface("Click mouse anywhere on screen to continue.", white, (DISPWIDTH // 2, 675))

    while not ready:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                ready = True
            pygame.display.update()


def getWelcomeScreen(p1, p2):
    ready = False
    p1Name = p1.getName()
    p1Chips = p1.getChipPile()
    p2Name = p2.getName()
    p2Chips = p2.getChipPile()

    setDisplay.blit(backgroundImage, (0, 0))

    msgSurface(p1Name + ": " + str(p1Chips) + " chips", white, (150, 150))
    msgSurface(p2Name + ": " + str(p2Chips) + " chips", white, (DISPWIDTH - 150, 150))

    msgSurface("Texas Hold'em Poker!", white, (DISPWIDTH // 2, DISPHEIGHT // 3))
    msgSurface(p1.getName() + " vs " + p2.getName(), white, (DISPWIDTH // 2, DISPHEIGHT // 3 + 50))
    msgSurface("Decide who will be " + p1.getName() + " and who will be " + p2.getName(), white,
               (DISPWIDTH // 2, DISPHEIGHT * 2 // 3))
    msgSurface("and then click the mouse anywhere to start the game.", white,
               (DISPWIDTH // 2, DISPHEIGHT * 2 // 3 + 50))

    while not ready:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                ready = True
            pygame.display.update()


def declareChamp(p1, p2, pWinner):
    ready = False
    p1Name = p1.getName()
    p1Chips = p1.getChipPile()
    p2Name = p2.getName()
    p2Chips = p2.getChipPile()

    setDisplay.blit(winnerImage, (0, 0))

    msgSurface(p1Name + ": " + str(p1Chips) + " chips", white, (150, 150))
    msgSurface(p2Name + ": " + str(p2Chips) + " chips", white, (DISPWIDTH - 150, 150))

    msgSurface(pWinner.getName() + ", POKER CHAMPION!", white, (DISPWIDTH // 2, 650))
    msgSurface("Click mouse anywhere to close screen.", white, (DISPWIDTH // 2, 675))

    while not ready:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                pygame.quit()
                sys.exit()
            pygame.display.update()


def getPlayerHand(p):
    player = PokerPlayer(p)
    return player.getHand()


def hands_to_list():
    hands = list()
    hands.append(Gus.getHand())
    hands.append(Tum.getHand())
    return hands

# 3. The primary function for game play is the one below. It will return once someone loses, not after every round.
