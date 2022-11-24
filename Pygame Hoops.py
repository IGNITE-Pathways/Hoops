from colors import *
import pygame, math, numpy, time, random
from pygame.locals import *

pygame.init()
screenWidth = 1400
screenHeight = 800
screen = pygame.display.set_mode((screenWidth, screenHeight))

clock = pygame.time.Clock()
pygame.display.set_caption("Hoops")
hoop_back = pygame.image.load(r'hoop_back.png').convert_alpha()
hoop_front = pygame.image.load(r'hoop_front.png').convert_alpha()
bx=400
by=425
hx=screenWidth-95
hy=250
ball_size=70
floor_height=100
shoot=False
highdamp=0.8
lowdamp=0.95
bounces=0
g=9.8
balls=[]

# Starting ball position
starting_ball_pos=(bx+round(ball_size/2),by+round(ball_size/2))

for i in range(1,36):
    balls.append(pygame.image.load(r'balls/ball_'+str(i)+'.png').convert_alpha())

def get_path(ball_pos,vx,vy):
    path=[]
    velocity=[]
    vfx = 0
    vfy = 0
    height_gained=0
    t=.3
    while True:
        x = vx * t
        y = vy * t + (g * t * t * 0.5) + ball_pos[1]
        #print(x + ball_pos[0],y)
        t+=0.3
        height_gained = y-ball_pos[1]
        vfx = vx
        vfy = math.sqrt((vy*vy)+(2*g*height_gained))
        path.append((x+ball_pos[0],(y)))
        velocity.append((vx,vy))
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
        elif (y + ball_size/2 > screenHeight - floor_height + 5):
            #Hitting Floor 
            vfx = vx*lowdamp
            vfy = -math.sqrt((vy*vy)+(2*g*height_gained))*highdamp
            break
        elif (y < ball_size/2) and vy<0:
            #Hitting Ceiling
            vfx = vx*lowdamp
            vfy = math.sqrt((vy*vy)+(2*g*height_gained))*highdamp
            break
    return path, velocity, (x + ball_pos[0], y), vfx, vfy

def calc_trajectory(pos):
    # calculate slope 
    if (starting_ball_pos[0]-pos[0])!=0:
        slope=(starting_ball_pos[1]-pos[1])/(starting_ball_pos[0]-pos[0])
    else:
        slope=math.inf 

    # Using distance as a proxy for speed
    speed = math.sqrt((starting_ball_pos[1]-pos[1])*(starting_ball_pos[1]-pos[1]) + (starting_ball_pos[0]-pos[0])*(starting_ball_pos[0]-pos[0]))

    # tan(θ) = slope, atan returns arc tangent of slope as a numeric value between -PI/2 and PI/2 radians (i.e. ±1.57)
    angle=math.atan(slope) 

    # adjust angle for right two quadrants
    if pos[0] > starting_ball_pos[0] and pos[1] >= starting_ball_pos[1]:
        #clicking in bottom right quadrant
        angle = angle + (math.pi)
    elif pos[0] > starting_ball_pos[0] and pos[1] < starting_ball_pos[1]:
        #clicking in top right quadrant
        angle = angle - (math.pi)

    return get_path(starting_ball_pos,speed * math.cos(angle),speed * math.sin(angle))

# Initialize last position on grid user clicked
lastPos=(0,0)

# Rsets the field given the ball position
def reset_field(ball_pos,degree=0):
    if degree<0 or degree>35:
        degree=0
    screen.fill(black)
    # Back Side of Hoop
    pygame.Surface.set_colorkey (hoop_back, [0,0,0])
    screen.blit(hoop_back, (hx+2, hy+12))
    # Ball itself
    pygame.Surface.set_colorkey (balls[degree], [0,0,0])
    screen.blit(balls[degree], (ball_pos[0], ball_pos[1]))
    # Front of the Hoop
    pygame.Surface.set_colorkey (hoop_front, [0,0,0])
    screen.blit(hoop_front, (hx, hy))
    # Floor 
    pygame.draw.rect(screen,(0,180,0),Rect(10,screenHeight - floor_height,screenWidth-20,15))
    pygame.draw.rect(screen,(green),Rect(hx-2,hy+8,10,20))

def process_path(path, velocity, collision_point, vx, vy):
    for a in path:
        time.sleep(.02)
        degree=round(round(a[0]%(34*3))/3)
        reset_field((a[0]-round(ball_size/2),a[1]-round(ball_size/2)),degree=degree)
        pygame.display.update() 
        rim = pygame.Rect(hx,hy+10,95,20)
        if a == collision_point:
            bounce_ball(collision_point, vx, vy)
        if rim.collidepoint((a[0],a[1])):
            print("Goal!!")
            break

# Recursive function that bounces the ball off the walls
def bounce_ball(start_pos, vx, vy):
    global bounces, starting_ball_pos
    bounces+=1
    path, velocity, collision_point, vx, vy  = get_path(start_pos, vx, vy)
    if abs(vx)<0.2 or abs(vy)<1:
        print("speed is 0")
        starting_ball_pos=collision_point
        return
    process_path(path, velocity, collision_point, vx, vy)

# Main Program -- Start --- 
reset_field((starting_ball_pos[0]-round(ball_size/2),starting_ball_pos[1]-round(ball_size/2)))

while True:
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button==1:
                    shoot=True
                    lastPos=(event.pos[0],event.pos[1])
                    endPos=(starting_ball_pos[0],starting_ball_pos[1])
                    path, velocity, collision_point, vx, vy  = calc_trajectory(lastPos)
                    for a in path:
                        pygame.draw.circle(screen,(white),(a[0],a[1]),2)
                        pygame.display.update()
            elif event.type == pygame.MOUSEMOTION:
                if shoot:
                    reset_field((starting_ball_pos[0]-round(ball_size/2),starting_ball_pos[1]-round(ball_size/2)))
                    lastPos=(event.pos[0],event.pos[1])
                    path, velocity, collision_point, vx, vy = calc_trajectory(lastPos)
                    for a in path:
                        pygame.draw.circle(screen,(white),(a[0],a[1]),2)
                        pygame.display.update()
            elif event.type == pygame.MOUSEBUTTONUP:
                reset_field((starting_ball_pos[0]-round(ball_size/2),starting_ball_pos[1]-round(ball_size/2)))
                if event.button==1:
                    path, velocity, collision_point, vx, vy  = calc_trajectory(lastPos)
                    process_path(path, velocity, collision_point, vx, vy)
                    shoot=False
    pygame.display.flip()
