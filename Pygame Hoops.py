from colors import *
import os, sys, pygame, math, numpy, time, random
from pygame.locals import *

# Initialize Global Variables 
WIDTH = 1500
HEIGHT = 900

#Global constants here
BLACK = (255,255,255)
BLACK = (0,0,0)
GREY  = (50,50,50)
RED  = (207,0,0)

class Control:
    def __init__(self):
        self.hoop_back = pygame.image.load(r'hoop_back.png').convert_alpha()
        self.hoop_front = pygame.image.load(r'hoop_front.png').convert_alpha()
        self.background = pygame.image.load(r'backgrounds/bg.png').convert_alpha()
        self.glassboard = pygame.image.load(r'glassboard.png').convert_alpha()
        self.player = pygame.image.load(r'players/player_'+str(random.randint(1,7))+'.png').convert_alpha()
        self.buffer = 100
        self.ball_size=70
        self.floor_height=80
        self.shoot=False
        self.highdamp=0.8
        self.lowdamp=0.95
        self.bounces=0
        self.g=9.8
        self.bx=400
        self.by=425
        self.balls=[]
        self.score=0
        self.font = pygame.font.Font('font/CoffeeTin.ttf',150)
        self.font2 = pygame.font.Font('font/IndianPoker.ttf', 75)
        self.font2.set_bold(True)

        self.startText = self.font2.render("Welcome to Hoops!", 1, (yellow))
        self.startSize = self.font2.size("Welcome to Hoops!")
        # Initialize last position on grid user clicked
        self.lastPos=(0,0)

        for i in range(1,36):
            self.balls.append(pygame.image.load(r'balls/ball_'+str(i)+'.png').convert_alpha())
        self.start_up_init()

    def start_up_init(self):
        self.background = pygame.transform.scale(self.background, (WIDTH,HEIGHT))

        #intitialize items for the startup section of the game
        self.hx=WIDTH-140
        self.hy=250
        self.skip_next_rim_check=False
        self.skip_next_goal_check=False
        self.front_rim=Rect(self.hx-2,self.hy+5,10,20)
        self.back_glassboard=Rect(WIDTH-55,self.hy-60,10,100)
        self.swish=True
        self.shootpoint=(self.bx,self.by)

        self.startLoc = (WIDTH/2 - self.startSize[0]/2, self.buffer)

        self.startButton = self.font2.render(" Start ", 1, BLACK)
        self.buttonSize = self.font2.size(" Start ")
        self.buttonLoc = (WIDTH/2 - self.buttonSize[0]/2, HEIGHT/3 - self.buttonSize[1]/2)

        self.buttonRect = pygame.Rect(self.buttonLoc, self.buttonSize)
        self.buttonRectOutline = pygame.Rect(self.buttonLoc, self.buttonSize)

        # Starting ball position
        self.starting_ball_pos=(self.bx+round(self.ball_size/2),self.by+round(self.ball_size/2))

        self.state = 0

    def main(self):
        if self.state == 0:
            self.show_splash_screen()
        elif self.state == 1:
            self.play()
        # elif self.state == 2:
        #     self.results()
        # elif self.state == 3:
        #     self.new_game()

    def show_score(self, msg, x, y, color, size):
        tin = pygame.font.Font('font/IndianPoker.ttf', size)
        msgobj = tin.render(msg, False, color)
        SCREEN.blit(msgobj, (x, y))

    def get_path(self, ball_pos,vx,vy):
        path=[]
        velocity=[]
        vfx = 0
        vfy = 0
        height_gained=0
        t=.3
        while True:
            x = vx * t
            y = vy * t + (self.g * t * t * 0.5) + ball_pos[1]
            #print("vy", vy, "x", x + ball_pos[0], "\t", "y", y, "\t", "t", t, "\t")
            t+=0.3
            height_gained = y-ball_pos[1]
            vertex_x = ball_pos[0] - vx*(vy/self.g)
            vertex_y = ball_pos[1]-((0.5*vy*vy)/self.g)
            vfx = vx
            vfy = math.sqrt((vy*vy)+(2*self.g*height_gained)) * (vy/abs(vy))
            if vy < 0:
                #Ball moving upward so will go through vertex
                if (x + ball_pos[0])*(vx/abs(vx)) > vertex_x*(vx/abs(vx)):
                    vfy = -vfy

            path.append((x+ball_pos[0],y))
            velocity.append((vfx,vfy))
            if abs(vx)<0.2 or abs(vy)<1:
                print("slowball")
                break
            elif (x + ball_pos[0] + self.ball_size/2 >= WIDTH) and vx>=0:
                #Hitting Right Wall
                vfx = -vx*self.highdamp
                if x + ball_pos[0] > vertex_x:
                    vfy = math.sqrt((vy*vy)+(2*self.g*height_gained))*self.lowdamp
                else:
                    vfy = -math.sqrt((vy*vy)+(2*self.g*height_gained))*self.lowdamp
                break
            elif (x + ball_pos[0] - self.ball_size/2 <= 0) and vx<0:
                #Hitting Left Wall
                vfx = -vx*self.highdamp
                if x + ball_pos[0] < vertex_x:
                    vfy = math.sqrt((vy*vy)+(2*self.g*height_gained))*self.lowdamp
                else:
                    vfy = -math.sqrt((vy*vy)+(2*self.g*height_gained))*self.lowdamp
                break
            elif (y + self.ball_size/2 >= HEIGHT - self.floor_height):
                #Hitting Floor 
                vfx = vx*self.lowdamp
                vfy = -math.sqrt((vy*vy)+(2*self.g*height_gained))*self.highdamp
                break
            elif (y <= self.ball_size/2) and vy<0:
                #Hitting Ceiling
                vfx = vx*self.lowdamp
                vfy = math.sqrt((vy*vy)+(2*self.g*height_gained))*self.highdamp
                break
        return path, velocity, (x + ball_pos[0], y), vfx, vfy

    def calc_trajectory(self, pos):
        # calculate slope 
        if (self.starting_ball_pos[0]-pos[0])!=0:
            slope=(self.starting_ball_pos[1]-pos[1])/(self.starting_ball_pos[0]-pos[0])
        else:
            slope=math.inf 

        # Using distance as a proxy for speed
        speed = math.sqrt((self.starting_ball_pos[1]-pos[1])*(self.starting_ball_pos[1]-pos[1]) + (self.starting_ball_pos[0]-pos[0])*(self.starting_ball_pos[0]-pos[0]))

        # tan(θ) = slope, atan returns arc tangent of slope as a numeric value between -PI/2 and PI/2 radians (i.e. ±1.57)
        angle=math.atan(slope) 

        # adjust angle for right two quadrants
        if pos[0] > self.starting_ball_pos[0] and pos[1] >= self.starting_ball_pos[1]:
            #clicking in bottom right quadrant
            angle = angle + (math.pi)
        elif pos[0] > self.starting_ball_pos[0] and pos[1] < self.starting_ball_pos[1]:
            #clicking in top right quadrant
            angle = angle - (math.pi)

        return self.get_path(self.starting_ball_pos,speed * math.cos(angle),speed * math.sin(angle))


    # Rsets the field given the ball position
    def reset_field(self, ball_pos,degree=0, splash=False):
        if degree<0 or degree>35:
            degree=0
        #SCREEN.fill(black)
        SCREEN.blit(self.background, (0,0))
        pygame.Surface.set_colorkey (self.glassboard, [0,0,0])
        SCREEN.blit(self.glassboard, (self.hx+50, self.hy-100))
        # Back Side of Hoop
        pygame.Surface.set_colorkey (self.hoop_back, [0,0,0])
        SCREEN.blit(self.hoop_back, (self.hx+2, self.hy+12))
        # Ball itself
        if splash != True:
            pygame.Surface.set_colorkey (self.balls[degree], [0,0,0])
            SCREEN.blit(self.balls[degree], (ball_pos[0], ball_pos[1]))
        # Front of the Hoop
        pygame.Surface.set_colorkey (self.hoop_front, [0,0,0])
        SCREEN.blit(self.hoop_front, (self.hx, self.hy))

        # Score Bar 
        score_bar = pygame.Surface((WIDTH,40), pygame.SRCALPHA) 
        score_bar.fill((255,255,255,32))  
        SCREEN.blit(score_bar, (0,0))
        # pygame.draw.rect(SCREEN,(100,100,100,128),Rect(0,0,WIDTH,20))
        # Score
        self.show_score("Score: "+str(self.score),WIDTH/2-50,5,white,25)
        # Rim Front edge
        #pygame.draw.rect(SCREEN,(green),front_rim)
        # Rim Back Edge 
        #pygame.draw.rect(SCREEN,(green),back_glassboard)
        # Rim
        #pygame.draw.rect(SCREEN, (blue),Rect(hx+5,hy+10,70,50))

    # Render path
    def process_path(self, path, velocity, collision_point, vx, vy):
        #print("process_path", "\t", collision_point, "\t", vx, "\t", vy)
        for i in range(len(path)):
            time.sleep(.02)
            #point p on the path
            p = path[i]
            #velocity at point p
            v = velocity[i]
            #print("p", p,"\t", "v", v)
            degree=round(round(p[0]%(34*3))/3)
            self.reset_field((p[0]-round(self.ball_size/2),p[1]-round(self.ball_size/2)),degree=degree)
            pygame.display.update() 
            rim = pygame.Rect(self.hx,self.hy+4,95,40)
            rim1 = pygame.Rect(self.hx,self.hy+25,5,35)
            rim_front_edge= pygame.Rect(self.front_rim)
            #rim_back_edge= pygame.Rect(WIDTH-10,hy+18,5,20)
            rim_back_edge= pygame.Rect(self.back_glassboard)
            ball_rect=pygame.Rect(p[0] - round(self.ball_size/2) + 10, p[1] - round(self.ball_size/2) + 10, self.ball_size - 20, self.ball_size - 20)
            if p == collision_point:
                #bounce the ball off the walls
                self.skip_next_rim_check=False
                self.skip_next_goal_check=False
                self.swish=False
                self.bounce_ball(collision_point, vx, vy)
            elif rim_front_edge.colliderect(ball_rect) and not self.skip_next_rim_check:
                #bounce off the rim edge
                print("Rim Front Edge", "\t", (p[0], p[1]), "\t", -v[0]*1.1, "\t", v[1]*1.1)
                self.skip_next_rim_check=True
                self.swish=False
                self.bounce_ball((p[0], p[1]), -v[0]*1.1, v[1]*1.1)
                break
            elif rim_back_edge.colliderect(ball_rect) and not self.skip_next_rim_check:
                #bounce off the rim edge
                print("Rim Back Edge", "\t", (p[0], p[1]), "\t", -v[0]*1.1, "\t", v[1]*1.1)
                self.skip_next_rim_check=True
                self.swish=False
                self.bounce_ball((p[0], p[1]), -v[0]*0.8, v[1]*1.2)
                break
            elif rim1.colliderect(ball_rect):
                self.skip_next_goal_check = True
                self.swish=True #reset
                continue # skip goal check 
            elif rim.collidepoint((p[0],p[1])) and not self.skip_next_goal_check:
                if v[1] < 0:
                    print("Ball moving upward in goal")
                else:
                    if self.swish:
                        print("Swish !!")
                    else:
                        print("Goal !!")
                    #print("x",self.shootpoint[0])
                    if self.shootpoint[0]<240:
                        self.score+=3
                    else:
                        self.score+=2
                    self.swish=True #reset
                    time.sleep(0.1)
                    # Make the ball fall down after hitting the goal
                    self.skip_next_goal_check=True
                    self.bounce_ball((p[0], p[1]), v[0]/abs(v[0]), abs(v[1]*self.highdamp))
                    break
            else:
                self.swish=True #reset

    # Recursive function that bounces the ball off the walls
    def bounce_ball(self, start_pos, vx, vy):
        #print("bounce_ball", "\t", start_pos, "\t", vx, "\t", vy)
        self.bounces+=1
        path, velocity, collision_point, vx, vy  = self.get_path(start_pos, vx, vy)
        if abs(vx)<0.2 or abs(vy)<1:
            print("speed is 0")
            self.starting_ball_pos=collision_point
            return
        else:
            self.process_path(path, velocity, collision_point, vx, vy)

    def show_splash_screen(self):
        global SCREEN, WIDTH, HEIGHT
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.VIDEORESIZE:
                SCREEN = pygame.display.set_mode((event.w, event.h),pygame.RESIZABLE)
                WIDTH=event.w
                HEIGHT=event.h
                self.start_up_init()
            #when the user clicks the start button, change to the playing state
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouseRect = pygame.Rect(event.pos, (1,1))
                    if mouseRect.colliderect(self.buttonRect):
                        self.state += 1
                        self.play_init()
                        return

        # Main Program -- Start --- 
        self.reset_field((self.starting_ball_pos[0]-round(self.ball_size/2),self.starting_ball_pos[1]-round(self.ball_size/2)), splash=True)

        #draw welcome text
        SCREEN.blit(self.startText, self.startLoc)
        pygame.Surface.set_colorkey (self.player, [0,0,0])
        SCREEN.blit(self.player, (850, 220))

        #draw the start button
        pygame.draw.rect(SCREEN, RED, self.buttonRect)
        pygame.draw.rect(SCREEN, BLACK, self.buttonRectOutline, 2)
        SCREEN.blit(self.startButton, self.buttonLoc)
    
        pygame.display.flip()


    def play_init(self):
        #create the new variables
        self.round = 0
        self.reset_field((self.starting_ball_pos[0]-round(self.ball_size/2),self.starting_ball_pos[1]-round(self.ball_size/2)), splash=False)

    def play(self):
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    print(event.pos)
                    if event.button==1:
                        self.shoot=True
                        self.shootpoint=event.pos
                        self.lastPos=(event.pos[0],event.pos[1])
                        path, velocity, collision_point, vx, vy  = self.calc_trajectory(self.lastPos)
                        for p in path:
                            pygame.draw.circle(SCREEN,(white),(p[0],p[1]),2)
                            pygame.display.update()
                elif event.type == pygame.MOUSEMOTION:
                    if self.shoot:
                        degree=round(round(self.starting_ball_pos[0]%(34*3))/3)
                        self.reset_field((self.starting_ball_pos[0]-round(self.ball_size/2),self.starting_ball_pos[1]-round(self.ball_size/2)),degree=degree)
                        self.lastPos=(event.pos[0],event.pos[1])
                        path, velocity, collision_point, vx, vy = self.calc_trajectory(self.lastPos)
                        for p in path:
                            pygame.draw.circle(SCREEN,(white),(p[0],p[1]),2)
                            pygame.display.update()
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.shoot:
                        #print("Mouse Up")
                        degree=round(round(self.starting_ball_pos[0]%(34*3))/3)
                        self.reset_field((self.starting_ball_pos[0]-round(self.ball_size/2),self.starting_ball_pos[1]-round(self.ball_size/2)),degree=degree)
                        if event.button==1:
                            path, velocity, collision_point, vx, vy  = self.calc_trajectory(self.lastPos)
                            self.process_path(path, velocity, collision_point, vx, vy)
                            self.shoot=False
        pygame.display.flip()

#############################################################
if __name__ == "__main__":
	os.environ['SDL_VIDEO_CENTERED'] = '1' #center SCREEN
	pygame.init()
	pygame.display.set_caption("Hoops")
	SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
	Runit = Control()
	Myclock = pygame.time.Clock()
	while 1:
		Runit.main()
		Myclock.tick(64)