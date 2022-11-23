from colors import *
import pygame, math, numpy, time, random
from pygame.locals import *

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
damp=0.8

g=9.8
def get_path(ball_pos,vx,vy):
    path=[]
    vfx = 0
    vfy = 0
    height_gained=0
    print("x",ball_pos[0],"y",ball_pos[1],"vx",vx,"vy",vy)
    t=0
    while True:
        x = vx * t
        y = vy * t + (g * t * t * 0.5) + ball_pos[1]
        path.append((x+ball_pos[0],(y)))
        #print(x + ball_pos[0],y)
        t+=0.3
        height_gained = y-ball_pos[1]
        if (x + ball_pos[0] > screenWidth - ball_size/2) and vx>=0:
            #Hitting Right Wall
            vfx = -vx*damp
            vertex_x = ball_pos[0] - vx*(vy/g)
            vertex_y = screenHeight-(screenHeight - ball_pos[1])-((0.5*vy*vy)/g)
            if x + ball_pos[0] > vertex_x:
                #print("Hitting Right Wall: downward")
                vfy = math.sqrt((vy*vy)+(2*g*height_gained))*damp
            else:
                #print("Hitting Right Wall: upward")
                vfy = -math.sqrt((vy*vy)+(2*g*height_gained))*damp
            #print("vertex-x",vertex_x,"vertex-y",vertex_y)
            break
        elif (x + ball_pos[0] < ball_size/2) and vx<0:
            #Hitting Left Wall
            vfx = -vx*damp
            vertex_x = ball_pos[0] - vx*(vy/g)
            vertex_y = screenHeight-(screenHeight - ball_pos[1])-((0.5*vy*vy)/g)
            if x + ball_pos[0] < vertex_x:
                vfy = math.sqrt((vy*vy)+(2*g*height_gained))*damp
               #print("Hitting Left Wall: downward")
            else:
                vfy = -math.sqrt((vy*vy)+(2*g*height_gained))*damp
                #print("Hitting Left Wall: upward")
            #print("vertex-x",vertex_x,"vertex-y",vertex_y)
            break
        elif (y > screenHeight - ball_size/2 - 15) and vy>0 and vx>0:
            #Hitting Floor 
            vfx = vx*damp
            vfy = -math.sqrt((vy*vy)+(2*g*height_gained))*damp
            #if x + ball_pos[0] > 0:
            print("Hitting Floor: forward")
            #else:
                #print("Hitting Floor: backward")
            break
        elif (y > screenHeight - ball_size/2 - 15) and vy>0 and vx<0:
            #Hitting Floor 
            vfx = vx*damp
            vfy = -math.sqrt((vy*vy)+(2*g*height_gained))*damp
            print("Hitting Floor: backward")
            break
        elif (y < ball_size/2) and vy<0:
            #Hitting Ceiling
            vfx = vx*damp
            vfy = math.sqrt((vy*vy)+(2*g*height_gained))*damp
            #if x + ball_pos[0] > 0:
                #print("Hitting Ceiling: forward")
            #else:
                #print("Hitting Ceiling: backward")
            break
        elif abs(vx)<5 or abs(vy)<5:
            print("slowball")
            break
        else:
            print("vfx",vfx,"vfy",vfy,"height_gained",-height_gained)
            print("x",x+ball_pos[0],"y",y,"vx",vx,"vy",vy)
    return path, (x + ball_pos[0], y), vfx, vfy

def calc_trajectory(pos):
    # calculate slope (y2-y1)/(x2-x1)
    if (bx+round(ball_size/2)-pos[0])!=0:
        slope=(by+round(ball_size/2)-pos[1])/(bx+round(ball_size/2)-pos[0])
    else:
        slope=9999999999 #proxy for infinity 
    angle=math.atan(slope)
    # Using distance as a proxy for speed
    speed = math.sqrt((by+round(ball_size/2)-pos[1])*(by+round(ball_size/2)-pos[1]) + (bx+round(ball_size/2)-pos[0])*(bx+round(ball_size/2)-pos[0]))
    if pos[0] > bx+round(ball_size/2):
         speed = -speed
    #print("speed",speed, "angle", angle, "slope", slope)
    ball_pos=(bx+round(ball_size/2),by+round(ball_size/2))
    return get_path(ball_pos,speed * math.cos(angle),speed * math.sin(angle))

lastPos=(0,0)
def reset_field():
    screen.fill(black)
    screen.blit(hoop, (hx, hy))
    pygame.Surface.set_colorkey (ball, [0,0,0])
    screen.blit(ball, (bx, by))
    pygame.draw.rect(screen,(0,200,0),Rect(0,screenHeight - 20,screenWidth,15))
    # pygame.draw.rect(screen,(white),Rect(hx+10,hy+10,80,20))
    pygame.draw.rect(screen,(green),Rect(hx-2,hy+8,10,20))

def bounce_ball(start_pos, vx, vy):
     path, collision_point, vx, vy  = get_path(start_pos, vx, vy)
     if vx==0 or vy==0:
         print("speed is 0")
         return
     for a in path:
        time.sleep(.03)
        screen.fill(black)
        screen.blit(hoop, (hx, hy))
        pygame.Surface.set_colorkey (ball, [0,0,0])
        screen.blit(ball, (a[0]-round(ball_size/2),a[1]-round(ball_size/2)))
        pygame.draw.rect(screen,(0,200,0),Rect(0,screenHeight - 20,screenWidth,15))
        pygame.display.update() 
        rim = pygame.Rect(hx,hy+10,95,20)
        if a == collision_point:
            print("bounce again")
            bounce_ball(collision_point, vx, vy)
        if rim.collidepoint((a[0],a[1])):
            print("Goal!!")

reset_field()
while True:
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                #print("mouse down")
                if event.button==1:
                    print("pos",event.pos[0],event.pos[1])
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
                    reset_field()
                    lastPos=(event.pos[0],event.pos[1])
                    path, collision_point, vx, vy = calc_trajectory(lastPos)
                    for a in path:
                        pygame.draw.circle(screen,(white),(a[0],a[1]),2)
                        pygame.display.update()
            elif event.type == pygame.MOUSEBUTTONUP:
                reset_field()
                if event.button==1:
                    #print("shoot done",event.pos[0],event.pos[1] )
                    screen.blit(ball, (bx, by))
                    path, collision_point, vx, vy  = calc_trajectory(lastPos)
                    for a in path:
                        time.sleep(.03)
                        screen.fill(black)
                        screen.blit(hoop, (hx, hy))
                        pygame.Surface.set_colorkey (ball, [0,0,0])
                        screen.blit(ball, (a[0]-round(ball_size/2),a[1]-round(ball_size/2)))
                        pygame.draw.rect(screen,(0,200,0),Rect(0,780,1500,15))
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
                    reset_field()
    pygame.display.flip()
