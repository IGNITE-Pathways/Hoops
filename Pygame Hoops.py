from colors import *
import pygame
import math
import numpy
import time
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
ball_size=75
shoot=False

g=9.8

def calculate_trajectory(pos,speed,angle):
    path=[]
    vx = speed * math.cos(angle)
    vy = -speed * math.sin(angle)
    print("vx",vx,"vy",vy)
    t=0
    while True:
        x = vx * t
        y =  screenHeight-(screenHeight-by - round(ball_size/2) + vy * t - (g * t * t * 0.5))
        path.append((x+bx+round(ball_size/2),(y)))
        t +=0.3
        if x > screenWidth or y > screenHeight or x < 0 or y < 0:
            break
            #calc_trajectory(bx,by)
    return path

def calc_trajectory(pos):
    #calculate slope (y2-y1)/(x2-x1)
    slope=(by+round(ball_size/2)-pos[1])/(bx+round(ball_size/2)-pos[0])
    angle=math.atan(slope)
    #print("slope",slope,"angle",angle)
    #Using distance as a proxy for speed
    speed = math.sqrt((by+round(ball_size/2)-pos[1])*(by+round(ball_size/2)-pos[1]) + (bx+round(ball_size/2)-pos[0])*(bx+round(ball_size/2)-pos[0]))
    if pos[0] > bx+round(ball_size/2):
         speed = -speed
    #print("speed",speed)
    return calculate_trajectory(pos,speed,angle)

lastPos=(0,0)
def reset_field():
    screen.fill(black)
    screen.blit(hoop, (hx, hy))
    pygame.Surface.set_colorkey (ball, [0,0,0])
    screen.blit(ball, (bx, by))
    pygame.draw.rect(screen,(0,200,0),Rect(0,780,1500,15))
    
reset_field()
while True:
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                print("mouse down")
                if event.button==1:
                    shoot=True
                    lastPos=(event.pos[0],event.pos[1])
                    endPos=(bx+round(ball_size/2),by+round(ball_size/2))
                    path = calc_trajectory(lastPos)
                    for a in path:
                        pygame.draw.circle(screen,(white),(a[0],a[1]),2)
                        pygame.display.update()
                if shoot:
                    print("shoot", event.pos[0],event.pos[1])
            elif event.type == pygame.MOUSEMOTION:
                if shoot:
                    reset_field()
                    lastPos=(event.pos[0],event.pos[1])
                    path = calc_trajectory(lastPos)
                    for a in path:
                        pygame.draw.circle(screen,(white),(a[0],a[1]),2)
                        pygame.display.update()
            elif event.type == pygame.MOUSEBUTTONUP:
                reset_field()
                if event.button==1:
                    print("shoot done",event.pos[0],event.pos[1] )
                    screen.blit(ball, (bx, by))
                    path = calc_trajectory(lastPos)
                    for a in path:
                        time.sleep(.03)
                        screen.fill(black)
                        screen.blit(hoop, (hx, hy))
                        pygame.Surface.set_colorkey (ball, [0,0,0])
                        screen.blit(ball, (a[0]-round(ball_size/2),a[1]-round(ball_size/2)))
                        pygame.draw.rect(screen,(0,200,0),Rect(0,780,1500,15))
                        pygame.display.update() 
                    shoot=False
                    reset_field()
    pygame.display.flip()
