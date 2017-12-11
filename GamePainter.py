import Server
import time
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
DISPHEIGHT = 400

set_display = pygame.display.set_mode((DISPWIDTH, DISPHEIGHT))
pygame.display.set_caption("Texas Holdem Poker")

background_image = pygame.image.load("background.png")
background_image = pygame.transform.scale(background_image, (DISPWIDTH, DISPHEIGHT))
winnerImage = pygame.image.load("winner.png")
winnerImage = pygame.transform.scale(winnerImage, (DISPWIDTH, DISPHEIGHT))

CARDWIDTH = 80
CARDHEIGHT = 100
card_back = pygame.image.load('playingcardback.png')
card_back = pygame.transform.scale(card_back, (CARDWIDTH, CARDHEIGHT))

card_sheet = Sheet("playercards.png")

card_img_list = []
indivX, indivY = 0, 0
indivWidth, indivHeight = 73, 99
for i in range(4):
    if i != 0:
        indivX, indivY = 0, (indivY + indivHeight)
    for j in range(13):
        indiv = card_sheet.get_image(indivX, indivY, indivWidth, indivHeight)
        indiv = pygame.transform.scale(indiv, (CARDWIDTH, CARDHEIGHT))
        card_img_list.append(indiv)
        indivX += indivWidth

card_list = []
num_range = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
suit_range = ['CLUBS', 'SPADES', 'HEARTS', 'DIAMONDS']
for suit in range(len(suit_range)):
    for num in range(len(num_range)):
        card_list.append(Card(num_range[num], suit_range[suit]))

card_dict = dict()
for i in range(len(card_list)):
    card_dict[card_list[i]] = card_img_list[i]


def make_text_objs(text, font, clr):
    text_surface = font.render(text, True, clr)
    return text_surface, text_surface.get_rect()


def msg_surface(text, textClr, CenterXY):
    txt_font = pygame.font.Font('freesansbold.ttf', 20)

    title_txt_surf, title_txt_rect = make_text_objs(text, txt_font, textClr)
    title_txt_rect.center = CenterXY
    set_display.blit(title_txt_surf, title_txt_rect)

    pygame.display.update()


def get_setup_screen(p1, p2, p_big_blind):
    p1_name = p1.name
    p1_chips = p1.chip_pile
    p2_name = p2.name
    p2_chips = p2.chip_pile

    set_display.blit(background_image, (0, 0))

    set_display.blit(card_back, (50, 250))
    set_display.blit(card_back, (150, 250))

    set_display.blit(card_back, (DISPWIDTH - 150, 250))
    set_display.blit(card_back, (DISPWIDTH - 250, 250))

    msg_surface("RIVER", white, (DISPWIDTH // 2, 50))
    msg_surface(p1_name + ": " + str(p1_chips) + " chips", white, (150, 375))
    msg_surface(p2_name + ": " + str(p2_chips) + " chips", white, (DISPWIDTH - 150, 375))

    if p1 == p_big_blind:
        msg_surface(p1_name + " is Big Blind. Pay 40 chips", white, (DISPWIDTH // 2, 450))
        msg_surface(p2_name + " is Small Blind. Pay 20 chips", white, (DISPWIDTH // 2, 500))
    elif p2 == p_big_blind:
        msg_surface(p2_name + " is Big Blind. Pay 40 chips", white, (DISPWIDTH // 2, 450))
        msg_surface(p1_name + " is Small Blind. Pay 20 chips", white, (DISPWIDTH // 2, 500))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
    pygame.time.delay(2500)


def get_river_screen(p1, p2, pot, river):
    p1_name = p1.name
    p1_chips = p1.chip_pile
    p2_name = p2.name
    p2_chips = p2.chip_pile

    set_display.blit(background_image, (0, 0))

    set_display.blit(card_back, (50, 250))
    set_display.blit(card_back, (150, 250))

    set_display.blit(card_back, (DISPWIDTH - 150, 250))
    set_display.blit(card_back, (DISPWIDTH - 250, 250))

    card_pos_inc = 125
    cards = river.river
    for i in range(len(cards)):
        card_img = card_dict[cards[i]]
        set_display.blit(card_img, (DISPWIDTH // 2 - CARDWIDTH // 2 - 250 + i * card_pos_inc, 100))

    msg_surface("RIVER", white, (DISPWIDTH // 2, 50))
    msg_surface(p1_name + ": " + str(p1_chips) + " chips", white, (150, 375))
    msg_surface(p2_name + ": " + str(p2_chips) + " chips", white, (DISPWIDTH - 150, 375))

    msg_surface("Pot is " + str(pot.pot), white, (DISPWIDTH // 2, 250))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
    pygame.time.delay(2500)


def get_action_screen(action, count, p1, p2, p_turn, pot, river=None):
    p1_name = p1.name
    p1_chips = p1.chip_pile
    p2_name = p2.name
    p2_chips = p2.chip_pile
    p_turn_name = p_turn.name

    set_display.blit(background_image, (0, 0))

    set_display.blit(card_back, (50, 250))
    set_display.blit(card_back, (150, 250))

    set_display.blit(card_back, (DISPWIDTH - 150, 250))
    set_display.blit(card_back, (DISPWIDTH - 250, 250))

    card_pos_inc = 125
    cards = river.river
    for i in range(len(cards)):
        rCardImg = card_dict[cards[i]]
        set_display.blit(rCardImg, (DISPWIDTH // 2 - CARDWIDTH // 2 - 250 + i * card_pos_inc, 100))

    msg_surface("RIVER", white, (DISPWIDTH // 2, 50))
    msg_surface(p1_name + ": " + str(p1_chips) + " chips", white, (150, 375))
    msg_surface(p2_name + ": " + str(p2_chips) + " chips", white, (DISPWIDTH - 150, 375))

    msg_surface("Pot is " + str(pot.pot), white, (DISPWIDTH // 2, 250))
    msg_surface(p_turn_name + action + count, white, (DISPWIDTH // 2, 300))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
    pygame.time.delay(2500)


def get_win_pot_screen(p1, p2, winner, pot, river=None, p1_combo=None, p2_combo=None):
    p1_name = p1.name
    p1_chips = p1.chip_pile
    p2_name = p2.name
    p2_chips = p2.chip_pile

    set_display.blit(background_image, (0, 0))

    if p1_combo is None and p2_combo is None:
        set_display.blit(card_back, (50, 250))
        set_display.blit(card_back, (150, 250))

        set_display.blit(card_back, (DISPWIDTH - 150, 250))
        set_display.blit(card_back, (DISPWIDTH - 250, 250))
    else:
        p1_hand = p1.hand
        p1card_img_left = card_dict[p1_hand[0]]
        p1card_img_right = card_dict[p1_hand[1]]

        p2_hand = p2.hand
        p2card_img_left = card_dict[p2_hand[0]]
        p2card_img_right = card_dict[p2_hand[1]]

        set_display.blit(p1card_img_left, (50, 250))
        set_display.blit(p1card_img_right, (150, 250))

        set_display.blit(p2card_img_left, (DISPWIDTH - 150, 250))
        set_display.blit(p2card_img_right, (DISPWIDTH - 250, 250))

        card_pos_inc = 125
        msg_surface(p1.name + " : ", white,
                    (DISPWIDTH // 2 - CARDWIDTH // 2 - 250 + -1 * card_pos_inc, 415 + 50))
        for i in range(len(p1_combo)):
            p1_img = card_dict[p1_combo[i]]
            set_display.blit(p1_img, (DISPWIDTH // 2 - CARDWIDTH // 2 - 250 + i * card_pos_inc, 415))

        msg_surface(p2.name + " : ", white,
                    (DISPWIDTH // 2 - CARDWIDTH // 2 - 250 + -1 * card_pos_inc, 520 + 50))
        for i in range(len(p2_combo)):
            p2_img = card_dict[p2_combo[i]]
            set_display.blit(p2_img, (DISPWIDTH // 2 - CARDWIDTH // 2 - 250 + i * card_pos_inc, 520))

    card_pos_inc = 125
    if river is not None:
        cards = river.river
        for i in range(len(cards)):
            card_img = card_dict[cards[i]]
            set_display.blit(card_img, (DISPWIDTH // 2 - CARDWIDTH // 2 - 250 + i * card_pos_inc, 100))

    msg_surface("RIVER", white, (DISPWIDTH // 2, 50))
    msg_surface(p1_name + ": " + str(p1_chips) + " chips", white, (150, 375))
    msg_surface(p2_name + ": " + str(p2_chips) + " chips", white, (DISPWIDTH - 150, 375))
    msg_surface("Pot is " + str(pot.pot), white, (DISPWIDTH // 2, 250))
    if winner is not None:
        msg_surface(winner.name + " wins " + str(pot.pot), white, (DISPWIDTH // 2, 650))
    else:
        msg_surface("Split the pot!", white, (DISPWIDTH // 2, 650))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        time.sleep(5)
    pygame.display.update()
    pygame.time.delay(2500)


def get_welcome_screen(p1, p2):
    p1_name = p1.name
    p1_chips = p1.chip_pile
    p2_name = p2.name
    p2_chips = p2.chip_pile

    set_display.blit(background_image, (0, 0))

    msg_surface(p1_name + ": " + str(p1_chips) + " chips", white, (150, 150))
    msg_surface(p2_name + ": " + str(p2_chips) + " chips", white, (DISPWIDTH - 150, 150))

    msg_surface("Texas Hold'em Poker!", white, (DISPWIDTH // 2, DISPHEIGHT // 3))
    msg_surface(p1.name + " vs " + p2.name, white, (DISPWIDTH // 2, DISPHEIGHT // 3 + 50))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
    pygame.time.delay(500)


def declare_сhamp(p1, p2, winner):
    p1_name = p1.name
    p1_chips = p1.chip_pile
    p2_name = p2.name
    p2_chips = p2.chip_pile

    set_display.blit(winnerImage, (0, 0))

    msg_surface(p1_name + ": " + str(p1_chips) + " chips", white, (150, DISPHEIGHT - 25))
    msg_surface(p2_name + ": " + str(p2_chips) + " chips", white, (DISPWIDTH - 150, DISPHEIGHT - 25))

    msg_surface(winner.name + " IS THE WINNER!", white, (DISPWIDTH // 2, DISPHEIGHT - 25))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
    pygame.time.delay(5000)
