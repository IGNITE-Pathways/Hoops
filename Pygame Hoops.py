from colors import *
import pygame
import math
import numpy
import time
from pygame.locals import *
import random
pygame.init()
screenWidth = 1400
screenHeight = 800
screen = pygame.display.set_mode((screenWidth, screenHeight))
#game_surf = pygame.surface.Surface((screenWidth, screenHeight))

clock = pygame.time.Clock()
pygame.display.set_caption("Hoops")
ball = pygame.image.load(r'ball.png').convert()
hoop = pygame.image.load(r'hoop.png').convert()
bx=400
by=425
hx=screenWidth-95
hy=250
ball_size=75
shoot=False

g=9.8

def calculate_trajectory(ball_pos,speed,angle):
    path=[]
    vx = speed * math.cos(angle)
    vy = speed * math.sin(angle)
    vfx = 0
    vfy = 0
    height_gained=0
    print("vx",vx,"vy",vy)
    t=0
    while True:
        x = vx * t
        y =  vy * t + (g * t * t * 0.5) + ball_pos[1]
        path.append((x+ball_pos[0],(y)))
        print(x,y)
        t+=0.3
        height_gained = y-ball_pos[1]
        if x + ball_pos[0] > screenWidth:
            #Hitting Right Wall
            vfx = -vx*0.9
            vertex_x = ball_pos[0] - vx*(vy/g)
            vertex_y = screenHeight-(screenHeight - ball_pos[1])-((0.5*vy*vy)/g)
            if x + ball_pos[0] > vertex_x:
                print("downward")
                vfy = math.sqrt((vy*vy)+(2*g*height_gained))
            else:
                print("upward")
                vfy = -math.sqrt((vy*vy)+(2*g*height_gained))
            print("vertex-x",vertex_x,"vertex-y",vertex_y)
            break
        elif x + ball_pos[0] < 0:
            #Hitting Left Wall
            vfx = -vx*0.9
            vertex_x = ball_pos[0] - vx*(vy/g)
            vertex_y = screenHeight-(screenHeight - ball_pos[1])-((0.5*vy*vy)/g)
            if x + ball_pos[0] < vertex_x:
                vfy = math.sqrt((vy*vy)+(2*g*height_gained))
                print("downward")
            else:
                vfy = -math.sqrt((vy*vy)+(2*g*height_gained))
                print("upward")
            print("vertex-x",vertex_x,"vertex-y",vertex_y)
            break
        elif y > screenHeight:
            #Hitting Floor 
            vfx = vx*0.9
            vfy = -math.sqrt((vy*vy)+(2*g*height_gained))
            if x  > 0:
                print("forward")
            else:
                print("backward")
            break
        elif y < 0:
            #Hitting Ceiling
            vfx = vx*0.9
            vfy = math.sqrt((vy*vy)+(2*g*height_gained))
            if x  > 0:
                print("forward")
            else:
                print("backward")
            break
    print("vfx",vfx,"vfy",vfy,"height_gained",-height_gained)
    return path

def calc_trajectory(pos):
    #calculate slope (y2-y1)/(x2-x1)
    if (bx+round(ball_size/2)-pos[0])!=0:
        slope=(by+round(ball_size/2)-pos[1])/(bx+round(ball_size/2)-pos[0])
    else:
        slope=99999
    angle=math.atan(slope)
    #Using distance as a proxy for speed
    speed = math.sqrt((by+round(ball_size/2)-pos[1])*(by+round(ball_size/2)-pos[1]) + (bx+round(ball_size/2)-pos[0])*(bx+round(ball_size/2)-pos[0]))
    if pos[0] > bx+round(ball_size/2):
         speed = -speed
    print("speed",speed, "angle", angle, "slope", slope)
    ball_pos=(bx+round(ball_size/2),by+round(ball_size/2))
    return calculate_trajectory(ball_pos,speed,angle)

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
