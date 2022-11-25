from colors import *
import pygame, math, numpy, time, random
from pygame.locals import *

pygame.init()

# Initialize Global Variables 
screenWidth = 1400
screenHeight = 800
screen = pygame.display.set_mode((screenWidth, screenHeight))

pygame.display.set_caption("Hoops")
hoop_back = pygame.image.load(r'hoop_back.png').convert_alpha()
hoop_front = pygame.image.load(r'hoop_front.png').convert_alpha()
background = pygame.image.load(r'bg.png').convert_alpha()

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
score=0
skip_next_rim_check=False
skip_next_goal_check=False

# Starting ball position
starting_ball_pos=(bx+round(ball_size/2),by+round(ball_size/2))

for i in range(1,36):
    balls.append(pygame.image.load(r'balls/ball_'+str(i)+'.png').convert_alpha())

def show_text(msg, x, y, color, size):
    fontobj = pygame.font.SysFont('freesans', size)
    msgobj = fontobj.render(msg, False, color)
    screen.blit(msgobj, (x, y))

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
        #print("vy", vy, "x", x + ball_pos[0], "\t", "y", y, "\t", "t", t, "\t")
        t+=0.3
        height_gained = y-ball_pos[1]
        vertex_x = ball_pos[0] - vx*(vy/g)
        vertex_y = ball_pos[1]-((0.5*vy*vy)/g)
        vfx = vx
        vfy = math.sqrt((vy*vy)+(2*g*height_gained)) * (vy/abs(vy))
        if vy < 0:
            #Ball moving upward so will go through vertex
            if (x + ball_pos[0])*(vx/abs(vx)) > vertex_x*(vx/abs(vx)):
                vfy = -vfy

        path.append((x+ball_pos[0],y))
        velocity.append((vfx,vfy))
        if abs(vx)<0.2 or abs(vy)<1:
            print("slowball")
            break
        elif (x + ball_pos[0] + ball_size/2 >= screenWidth) and vx>=0:
            #Hitting Right Wall
            vfx = -vx*highdamp
            if x + ball_pos[0] > vertex_x:
                vfy = math.sqrt((vy*vy)+(2*g*height_gained))*lowdamp
            else:
                vfy = -math.sqrt((vy*vy)+(2*g*height_gained))*lowdamp
            break
        elif (x + ball_pos[0] - ball_size/2 <= 0) and vx<0:
            #Hitting Left Wall
            vfx = -vx*highdamp
            if x + ball_pos[0] < vertex_x:
                vfy = math.sqrt((vy*vy)+(2*g*height_gained))*lowdamp
            else:
                vfy = -math.sqrt((vy*vy)+(2*g*height_gained))*lowdamp
            break
        elif (y + ball_size/2 >= screenHeight - floor_height):
            #Hitting Floor 
            vfx = vx*lowdamp
            vfy = -math.sqrt((vy*vy)+(2*g*height_gained))*highdamp
            break
        elif (y <= ball_size/2) and vy<0:
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
    #screen.fill(black)
    screen.blit(background, (0,0))
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
    #pygame.draw.rect(screen,(0,180,0),Rect(10,screenHeight - floor_height,screenWidth-20,15))
    # Score
    show_text("Score: "+str(score),screenWidth/2-50,25,blue,30)
    # Rim Front edge
    pygame.draw.rect(screen,(green),Rect(hx-2,hy+5,5,10))
    # Rim Back Edge 
    pygame.draw.rect(screen,(green),Rect(screenWidth-10,hy+18,5,20))
    # Rim
    pygame.draw.rect(screen, (blue),Rect(hx+5,hy+10,70,50))

# Render path
def process_path(path, velocity, collision_point, vx, vy):
    global skip_next_rim_check, skip_next_goal_check, score
    #print("process_path", "\t", collision_point, "\t", vx, "\t", vy)
    for i in range(len(path)):
        time.sleep(.02)
        #point p on the path
        p = path[i]
        #velocity at point p
        v = velocity[i]
        #print("p", p,"\t", "v", v)
        degree=round(round(p[0]%(34*3))/3)
        reset_field((p[0]-round(ball_size/2),p[1]-round(ball_size/2)),degree=degree)
        pygame.display.update() 
        rim = pygame.Rect(hx,hy+10,95,50)
        rim_front_edge= pygame.Rect(hx-2,hy+5,5,10)
        rim_back_edge= pygame.Rect(screenWidth-10,hy+18,5,20)
        ball_rect=pygame.Rect(p[0] - round(ball_size/2) + 10, p[1] - round(ball_size/2) + 10, ball_size - 20, ball_size - 20)
        if p == collision_point:
            #bounce the ball off the walls
            skip_next_rim_check=False
            skip_next_goal_check=False
            bounce_ball(collision_point, vx, vy)
        elif rim_front_edge.colliderect(ball_rect) and not skip_next_rim_check:
            #bounce off the rim edge
            print("Rim Front Edge", "\t", (p[0], p[1]), "\t", -v[0]*1.1, "\t", v[1]*1.1)
            skip_next_rim_check=True
            bounce_ball((p[0], p[1]), -v[0]*1.1, v[1]*1.1)
            break
        elif rim_back_edge.colliderect(ball_rect) and not skip_next_rim_check:
            #bounce off the rim edge
            print("Rim Back Edge", "\t", (p[0], p[1]), "\t", -v[0]*1.1, "\t", v[1]*1.1)
            skip_next_rim_check=True
            bounce_ball((p[0], p[1]), -v[0]*1.1, v[1]*1.1)
            break
        elif rim.collidepoint((p[0],p[1])) and not skip_next_goal_check:
            print("Goal!!")
            score+=1
            time.sleep(0.1)
            # Make the ball fall down after hitting the goal
            skip_next_goal_check=True
            bounce_ball((p[0], p[1]), v[0]/abs(v[0]), abs(v[1]*highdamp))
            break

# Recursive function that bounces the ball off the walls
def bounce_ball(start_pos, vx, vy):
    #print("bounce_ball", "\t", start_pos, "\t", vx, "\t", vy)
    global bounces, starting_ball_pos
    bounces+=1
    path, velocity, collision_point, vx, vy  = get_path(start_pos, vx, vy)
    if abs(vx)<0.2 or abs(vy)<1:
        print("speed is 0")
        starting_ball_pos=collision_point
        return
    else:
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
                    for p in path:
                        pygame.draw.circle(screen,(white),(p[0],p[1]),2)
                        pygame.display.update()
            elif event.type == pygame.MOUSEMOTION:
                if shoot:
                    degree=round(round(starting_ball_pos[0]%(34*3))/3)
                    reset_field((starting_ball_pos[0]-round(ball_size/2),starting_ball_pos[1]-round(ball_size/2)),degree=degree)
                    lastPos=(event.pos[0],event.pos[1])
                    path, velocity, collision_point, vx, vy = calc_trajectory(lastPos)
                    for p in path:
                        pygame.draw.circle(screen,(white),(p[0],p[1]),2)
                        pygame.display.update()
            elif event.type == pygame.MOUSEBUTTONUP:
                degree=round(round(starting_ball_pos[0]%(34*3))/3)
                reset_field((starting_ball_pos[0]-round(ball_size/2),starting_ball_pos[1]-round(ball_size/2)),degree=degree)
                if event.button==1:
                    path, velocity, collision_point, vx, vy  = calc_trajectory(lastPos)
                    process_path(path, velocity, collision_point, vx, vy)
                    shoot=False
    pygame.display.flip()