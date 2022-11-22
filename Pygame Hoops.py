from colors import *
import pygame
import math
import numpy
from pygame.locals import *
import random
pygame.init()
screenWidth = 1500
screenHeight = 800
screen = pygame.display.set_mode((screenWidth, screenHeight))
#game_surf = pygame.surface.Surface((screenWidth, screenHeight))

clock = pygame.time.Clock()
pygame.display.set_caption("Hoops")
ball = pygame.image.load(r'C:\Users\gupta\OneDrive\Desktop\Coding\Hoops\\ball.png').convert()
hoop = pygame.image.load(r'C:\Users\gupta\OneDrive\Desktop\Coding\Hoops\\hoop.png').convert()
bx=100
by=425
hx=1405
hy=250
bounce=False
shoot=False

def draw_dashed_line(surf, color, start_pos, end_pos, width=1, dash_length=10):
    x1, y1 = start_pos
    x2, y2 = end_pos
    dl = dash_length

    if (x1 == x2):
        ycoords = [y for y in range(y1, y2, dl if y1 < y2 else -dl)]
        xcoords = [x1] * len(ycoords)
    elif (y1 == y2):
        xcoords = [x for x in range(x1, x2, dl if x1 < x2 else -dl)]
        ycoords = [y1] * len(xcoords)
    else:
        a = abs(x2 - x1)
        b = abs(y2 - y1)
        c = round(math.sqrt(a**2 + b**2))
        dx = dl * a / c
        dy = dl * b / c

        xcoords = [x for x in numpy.arange(x1, x2, dx if x1 < x2 else -dx)]
        ycoords = [y for y in numpy.arange(y1, y2, dy if y1 < y2 else -dy)]

    next_coords = list(zip(xcoords[1::2], ycoords[1::2]))
    last_coords = list(zip(xcoords[0::2], ycoords[0::2]))
    for (x1, y1), (x2, y2) in zip(next_coords, last_coords):
        start = (round(x1), round(y1))
        end = (round(x2), round(y2))
        pygame.draw.line(surf, color, start, end, width)

screen.fill(black)
screen.blit(hoop, (hx, hy))
screen.blit(ball, (bx, by))
pygame.draw.rect(screen,(0,200,0),Rect(0,780,1500,15))

lastPos=(0,0)
while True:
    #pygame.draw.line(screen, (white),(10,10), (50,50),width=5)
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                print("mouse down")
                if event.button==1:
                    shoot=True
                    lastPos=(event.pos[0],event.pos[1])
                    endPos=(bx+45,by+45)
                if shoot:
                    print("shoot", event.pos[0],event.pos[1])
                    draw_dashed_line(screen, (white), endPos, lastPos)
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button==1:
                    print("shoot done",event.pos[0],event.pos[1] )
                    draw_dashed_line(screen, (black),endPos, lastPos)
                    screen.blit(ball, (bx, by))
                    shoot=False
    pygame.display.flip()
