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
yellow = (255, 215, 0)
cyan = (0, 255, 255)
purple = (255, 0, 255)

FPS = 30
DISPWIDTH = 1000
DISPHEIGHT = 700

setDisplay = pygame.display.set_mode((DISPWIDTH, DISPHEIGHT))
pygame.display.set_caption("Texas Holdem Poker")

backgroundImage = pygame.image.load("background.png")
backgroundImage = pygame.transform.scale(backgroundImage, (DISPWIDTH, DISPHEIGHT))
winnerImage = pygame.image.load("winner.png")
winnerImage = pygame.transform.scale(winnerImage, (DISPWIDTH, DISPHEIGHT))

CARDWIDTH = 80
CARDHEIGHT = 100
cardBack = pygame.image.load('playingcardback.png')
cardBack = pygame.transform.scale(cardBack, (CARDWIDTH, CARDHEIGHT))

cardSheet = Sheet("playercards.png")

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

theCardList = []
numberRange = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
suitRange = ['CLUBS', 'SPADES', 'HEARTS', 'DIAMONDS']
for suitIndex in range(len(suitRange)):
    for numberIndex in range(len(numberRange)):
        theCardList.append(Card(numberRange[numberIndex], suitRange[suitIndex]))

theCardDictionary = dict()
for i in range(len(theCardList)):
    theCardDictionary[theCardList[i]] = cardImgList[i]


def makeTxtObjs(text, font, clr):
    textSurface = font.render(text, True, clr)
    return textSurface, textSurface.get_rect()


def msgSurface(text, textClr, CenterXY):
    txtFont = pygame.font.Font('freesansbold.ttf', 20)

    titleTxtSurf, titleTxtRect = makeTxtObjs(text, txtFont, textClr)
    titleTxtRect.center = CenterXY
    setDisplay.blit(titleTxtSurf, titleTxtRect)

    pygame.display.update()


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

    rCardCoordIncrement = 125
    if riverCards != None:
        rCards = riverCards.getRiver()
        for i in range(len(rCards)):
            rCardImg = theCardDictionary[rCards[i]]
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


def getActionScreen(action, count, p1, p2, pTurn, thePot, riverCards=None):
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

    rCardCoordIncrement = 125
    if riverCards != None:
        rCards = riverCards.getRiver()
        for i in range(len(rCards)):
            rCardImg = theCardDictionary[rCards[i]]
            setDisplay.blit(rCardImg, (DISPWIDTH // 2 - CARDWIDTH // 2 - 250 + i * rCardCoordIncrement, 100))

    msgSurface("RIVER", white, (DISPWIDTH // 2, 50))
    msgSurface(p1Name + ": " + str(p1Chips) + " chips", white, (150, 375))
    msgSurface(p2Name + ": " + str(p2Chips) + " chips", white, (DISPWIDTH - 150, 375))

    msgSurface("Pot at " + str(thePot.getPot()), white, (DISPWIDTH // 2, 250))
    msgSurface(pTurnName + action + count, white, (DISPWIDTH // 2, 300))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        pygame.display.update()


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
        p1Hand = p1.getHand()
        p1cardImgLHS = theCardDictionary[p1Hand[0]]
        p1cardImgRHS = theCardDictionary[p1Hand[1]]

        p2Hand = p2.getHand()
        p2cardImgLHS = theCardDictionary[p2Hand[0]]
        p2cardImgRHS = theCardDictionary[p2Hand[1]]

        setDisplay.blit(p1cardImgLHS, (50, 250))
        setDisplay.blit(p1cardImgRHS, (150, 250))

        setDisplay.blit(p2cardImgLHS, (DISPWIDTH - 150, 250))
        setDisplay.blit(p2cardImgRHS, (DISPWIDTH - 250, 250))

        CardPositionIncrement = 125
        msgSurface(p1.getName() + " : ", white, (DISPWIDTH // 2 - CARDWIDTH // 2 - 250 + -1 * CardPositionIncrement, 415 + 50))
        for i in range(len(p1Combo)):
            p1CCImg = theCardDictionary[p1Combo[i]]
            setDisplay.blit(p1CCImg, (DISPWIDTH // 2 - CARDWIDTH // 2 - 250 + i * CardPositionIncrement, 415))

        msgSurface(p2.getName() + " : ", white, (DISPWIDTH // 2 - CARDWIDTH // 2 - 250 + -1 * CardPositionIncrement, 520 + 50))
        for i in range(len(p2Combo)):
            p2CCImg = theCardDictionary[p2Combo[i]]
            setDisplay.blit(p2CCImg, (DISPWIDTH // 2 - CARDWIDTH // 2 - 250 + i * CardPositionIncrement, 520))

    rCardCoordIncrement = 125
    if riverCards != None:
        rCards = riverCards.getRiver()
        for i in range(len(rCards)):
            rCardImg = theCardDictionary[rCards[i]]
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

