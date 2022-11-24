from colors import *
import pygame, math, numpy, time, random
from pygame.locals import *

pygame.init()
screenWidth = 1400
screenHeight = 800
screen = pygame.display.set_mode((screenWidth, screenHeight))

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
highdamp=0.8
lowdamp=0.95
bounces=0
g=9.8
def spin_ball(degree):
    global ball
    ball=pygame.transform.rotate(ball, degree)
def get_path(ball_pos,vx,vy):
    path=[]
    vfx = 0
    vfy = 0
    height_gained=0
    #print("x",ball_pos[0],"y",ball_pos[1],"vx",vx,"vy",vy)
    t=.3
    while True:
        x = vx * t
        y = vy * t + (g * t * t * 0.5) + ball_pos[1]
        path.append((x+ball_pos[0],(y)))
        #print(x + ball_pos[0],y)
        t+=0.3
        height_gained = y-ball_pos[1]
        if abs(vx)<0.2 or abs(vy)<1:
            print("slowball")
            break
        elif (x + ball_pos[0] > screenWidth - ball_size/2) and vx>=0:
            #Hitting Right Wall
            vfx = -vx*highdamp
            vertex_x = ball_pos[0] - vx*(vy/g)
            vertex_y = screenHeight-(screenHeight - ball_pos[1])-((0.5*vy*vy)/g)
            if x + ball_pos[0] > vertex_x:
                vfy = math.sqrt((vy*vy)+(2*g*height_gained))*lowdamp
            else:
                vfy = -math.sqrt((vy*vy)+(2*g*height_gained))*lowdamp
            break
        elif (x + ball_pos[0] < ball_size/2) and vx<0:
            #Hitting Left Wall
            vfx = -vx*highdamp
            vertex_x = ball_pos[0] - vx*(vy/g)
            vertex_y = screenHeight-(screenHeight - ball_pos[1])-((0.5*vy*vy)/g)
            if x + ball_pos[0] < vertex_x:
                vfy = math.sqrt((vy*vy)+(2*g*height_gained))*lowdamp
            else:
                vfy = -math.sqrt((vy*vy)+(2*g*height_gained))*lowdamp
            break
        elif (y > screenHeight - ball_size/2 - 15):
            #Hitting Floor 
            vfx = vx*lowdamp
            vfy = -math.sqrt((vy*vy)+(2*g*height_gained))*highdamp
            break
        elif (y < ball_size/2) and vy<0:
            #Hitting Ceiling
            vfx = vx*lowdamp
            vfy = math.sqrt((vy*vy)+(2*g*height_gained))*highdamp
            break
    #print("vfx",vfx,"vfy",vfy,"height_gained",-height_gained)
    #print("x",x+ball_pos[0],"y",y,"vx",vx,"vy",vy)
    return path, (x + ball_pos[0], y), vfx, vfy

def calc_trajectory(pos):
    # current ball position
    ball_pos=(bx+round(ball_size/2),by+round(ball_size/2))

    # calculate slope 
    if (ball_pos[0]-pos[0])!=0:
        slope=(ball_pos[1]-pos[1])/(ball_pos[0]-pos[0])
    else:
        slope=math.inf 

    # Using distance as a proxy for speed
    speed = math.sqrt((ball_pos[1]-pos[1])*(ball_pos[1]-pos[1]) + (ball_pos[0]-pos[0])*(ball_pos[0]-pos[0]))

    # tan(θ) = slope, atan returns arc tangent of slope as a numeric value between -PI/2 and PI/2 radians (i.e. ±1.57)
    angle=math.atan(slope) 

    # adjust angle for right two quadrants
    if pos[0] > ball_pos[0] and pos[1] >= ball_pos[1]:
        #clicking in bottom right quadrant
        angle = angle + (math.pi)
    elif pos[0] > ball_pos[0] and pos[1] < ball_pos[1]:
        #clicking in top right quadrant
        angle = angle - (math.pi)

    return get_path(ball_pos,speed * math.cos(angle),speed * math.sin(angle))

# Initialize last position on grid user clicked
lastPos=(0,0)

# Rsets the field given the ball position
def reset_field(ball_pos,degree=0):
    screen.fill(black)
    pygame.Surface.set_colorkey (ball, [0,0,0])
    spin_ball(degree)
    screen.blit(ball, (ball_pos[0], ball_pos[1]))
    pygame.Surface.set_colorkey (hoop, [0,0,0])
    screen.blit(hoop, (hx, hy))
    pygame.draw.rect(screen,(0,200,0),Rect(0,screenHeight - 20,screenWidth,15))
    # pygame.draw.rect(screen,(white),Rect(hx+10,hy+10,80,20))
    pygame.draw.rect(screen,(green),Rect(hx-2,hy+8,10,20))

# Recursive function that bounces the ball off the walls
def bounce_ball(start_pos, vx, vy):
     global bounces
     bounces+=1
     path, collision_point, vx, vy  = get_path(start_pos, vx, vy)
     if vx==0 or vy==0:
         print("speed is 0")
         return
     for a in path:
        time.sleep(.02)
        reset_field((a[0]-round(ball_size/2),a[1]-round(ball_size/2)))
        pygame.display.update() 
        rim = pygame.Rect(hx,hy+10,95,20)
        if a == collision_point:
            bounce_ball(collision_point, vx, vy)
        if rim.collidepoint((a[0],a[1])):
            print("Goal!!")
            break

reset_field((bx,by))
while True:
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button==1:
                    #print("pos",event.pos[0],event.pos[1])
                    shoot=True
                    lastPos=(event.pos[0],event.pos[1])
                    endPos=(bx+round(ball_size/2),by+round(ball_size/2))
                    path, collision_point, vx, vy  = calc_trajectory(lastPos)
                    for a in path:
                        pygame.draw.circle(screen,(white),(a[0],a[1]),2)
                        pygame.display.update()
                if shoot:
                    print("shoot", event.pos[0],event.pos[1])
            elif event.type == pygame.MOUSEMOTION:
                if shoot:
                    reset_field((bx,by))
                    lastPos=(event.pos[0],event.pos[1])
                    path, collision_point, vx, vy = calc_trajectory(lastPos)
                    for a in path:
                        pygame.draw.circle(screen,(white),(a[0],a[1]),2)
                        pygame.display.update()
            elif event.type == pygame.MOUSEBUTTONUP:
                reset_field((bx,by))
                if event.button==1:
                    #print("shoot done",event.pos[0],event.pos[1] )
                    screen.blit(ball, (bx, by))
                    path, collision_point, vx, vy  = calc_trajectory(lastPos)
                    for a in path:
                        time.sleep(.02)
                        reset_field((a[0]-round(ball_size/2),a[1]-round(ball_size/2)))
                        pygame.display.update() 
                        rim = pygame.Rect(hx,hy+10,95,20)
                        if a == collision_point:
                            print("Bounce baby")
                            bounce_ball(collision_point, vx, vy)
                            break
                        if rim.collidepoint((a[0],a[1])):
                            print("Goal!!")
                            break
                    shoot=False
    pygame.display.flip()
