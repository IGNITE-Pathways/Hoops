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
g=9.8

def calc_trajectory(pos):
    path=[]
    #calculate slope (y2-y1)/(x2-x1)
    slope=(by+45-pos[1])/(bx+45-pos[0])
    angle=math.atan(slope)
    print("slope",slope,"angle",angle)
    #Using distance as a proxy for speed
    speed = math.sqrt((by+45-pos[1])*(by+45-pos[1]) + (bx+45-pos[0])*(bx+45-pos[0]))
    if pos[0] > bx+45:
         speed = -speed
    print("speed",speed)
    vx = speed * math.cos(angle)
    vy = -speed * math.sin(angle)
    print("vx",vx,"vy",vy)
    t=0
    while True:
        x = vx * t
        y =  screenHeight-(screenHeight-by - 45 + vy * t - (g * t * t * 0.5))
        path.append((x+bx+45,(y)))
        t +=0.5
        if x > screenWidth or y > screenHeight or x < 0 or y < 0:
            break
    return path

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
                    draw_dashed_line(screen, (white), endPos, lastPos)                    
                if shoot:
                    print("shoot", event.pos[0],event.pos[1])
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button==1:
                    print("shoot done",event.pos[0],event.pos[1] )
                    draw_dashed_line(screen, (black),endPos, lastPos)
                    screen.blit(ball, (bx, by))
                    path = calc_trajectory(lastPos)
                    print("path",path)
                    for a in path:
                        pygame.draw.circle(screen,(white),(a[0],a[1]),2)
                    shoot=False
    pygame.display.flip()
