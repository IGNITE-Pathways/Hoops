from colors import *
import os, sys, pygame, math, numpy, time, random
from pygame.locals import *
from enum import Enum
import pygame_menu
from typing import Tuple, Any, Optional, List

# Initialize Global Variables 
WIDTH = 1500
HEIGHT = 900

#Global constants here
BLACK = (255,255,255)
BLACK = (0,0,0)
GREY  = (50,50,50)
RED  = (207,0,0)

class Display(Enum):
    SPLASH = 1
    PLAY = 2
    RESULTS = 3

#Gravity in m/s²
class Celestial(Enum):
    MERCURY = 3.7
    VENUS = 8.87
    EARTH = 9.807
    MARS = 3.721
    JUPITER = 24.79
    SATURN = 11.44
    NEPTUNE = 11.15
    MOON = 1.62
    SUN = 274

class Hoops:
    def __init__(self):
        self.buffer = 100
        self.ball_size=70
        self.highdamp=0.8
        self.lowdamp=0.95

        self.hoop_back = pygame.image.load(r'hoop_back.png').convert_alpha()
        self.hoop_front = pygame.image.load(r'hoop_front.png').convert_alpha()
        self.glassboard = pygame.image.load(r'glassboard.png').convert_alpha()
        self.gear = pygame.image.load(r'gear.png').convert_alpha()
        self.debug = pygame.image.load(r'debug.png').convert_alpha()
        
        self.player = pygame.image.load(r'players/player_'+str(random.randint(1,7))+'.png').convert_alpha()
        self.font = pygame.font.Font('font/CoffeeTin.ttf',150)
        self.font2 = pygame.font.Font('font/IndianPoker.ttf', 75)
        self.font2.set_bold(True)
        self.balls=[]
        for i in range(1,36):
            self.balls.append(pygame.image.load(r'balls/ball_'+str(i)+'.png').convert_alpha())

        self.shoot=False
        self.bounces=0
        self.celestialBody: Celestial = Celestial.EARTH
        self.score=0
        # self.settingsOverlay = False
        self.debugEnabled = False

        self.startText = self.font2.render("Welcome to Hoops!", 1, (yellow))
        self.startSize = self.font2.size("Welcome to Hoops!")
        # Initialize last position on grid user clicked
        self.lastPos=(0,0)
        # self.settings_pane = pygame.Surface((WIDTH/2,HEIGHT/2), pygame.SRCALPHA) 

        self.menu = pygame_menu.Menu(
            height=HEIGHT * 0.6,
            theme=pygame_menu.themes.THEME_DEFAULT.copy(),
            title='Select Celestial Body',
            width=WIDTH * 0.6
        )

        self.menu.add.selector('',[('MERCURY', 'MERCURY')], onchange=self.change_celestial_body, selector_id='MERCURY')
        self.menu.add.selector('',[('VENUS', 'VENUS')], onchange=self.change_celestial_body, selector_id='VENUS')
        self.menu.add.selector('',[('EARTH', 'EARTH')], onchange=self.change_celestial_body, selector_id='EARTH')
        self.menu.add.selector('',[('MARS', 'MARS')], onchange=self.change_celestial_body, selector_id='MARS')
        self.menu.add.selector('',[('JUPITER', 'JUPITER')], onchange=self.change_celestial_body, selector_id='JUPITER')
        self.menu.add.selector('',[('SATURN', 'SATURN')], onchange=self.change_celestial_body, selector_id='SATURN')
        self.menu.add.selector('',[('NEPTUNE', 'NEPTUNE')], onchange=self.change_celestial_body, selector_id='NEPTUNE')
        self.menu.add.selector('',[('MOON', 'MOON')], onchange=self.change_celestial_body, selector_id='MOON')
        self.menu.add.selector('',[('SUN', 'SUN')], onchange=self.change_celestial_body, selector_id='SUN')
        
        self.menu.disable()
        self.menu.full_reset()
        self.start_up_init()

    def change_celestial_body(self, value: Tuple[Any, int], body: str) -> None:
        selected, index = value
        print(f'Selected body: {body} at index {index}')
        # Set the body
        if body == Celestial.MERCURY.name:
            self.celestialBody = Celestial.MERCURY
        elif body == Celestial.VENUS.name:
            self.celestialBody = Celestial.VENUS
        elif body == Celestial.EARTH.name:
            self.celestialBody = Celestial.EARTH
        elif body == Celestial.MARS.name:
            self.celestialBody = Celestial.MARS
        elif body == Celestial.JUPITER.name:
            self.celestialBody = Celestial.JUPITER
        elif body == Celestial.SATURN.name:
            self.celestialBody = Celestial.SATURN
        elif body == Celestial.NEPTUNE.name:
            self.celestialBody = Celestial.NEPTUNE
        elif body == Celestial.MOON.name:
            self.celestialBody = Celestial.MOON
        elif body == Celestial.SUN.name:
            self.celestialBody = Celestial.SUN
        self.menu.disable()
        self.menu.full_reset()
        self.start_up_init()
        self.reset_field(ball_pos=self.starting_ball_pos)

    def start_up_init(self):
        self.bx=(400/1400)*WIDTH
        self.by=HEIGHT-400
        self.floor_height=(80/800)*HEIGHT
        self.gravity = self.celestialBody.value
        print("Setting Celestial Body to",self.celestialBody.name, "Gtavity", self.celestialBody.value)
        # Starting ball position
        self.starting_ball_pos=(self.bx+round(self.ball_size/2),self.by+round(self.ball_size/2))
        self.background = pygame.image.load(r'backgrounds/'+self.celestialBody.name+'.png').convert_alpha()
        self.background = pygame.transform.scale(self.background, (WIDTH,HEIGHT))

        #intitialize items for the startup section of the game
        self.hx=WIDTH-140
        self.hy=250
        self.skip_next_rim_check=False
        self.skip_next_goal_check=False
        self.front_rim=Rect(self.hx-2,self.hy,10,25)
        self.back_glassboard=Rect(WIDTH-55,self.hy-60,10,120)
        self.swish=True

        self.startLoc = (WIDTH/2 - self.startSize[0]/2, self.buffer)

        self.startButton = self.font2.render(" Start ", 1, BLACK)
        self.startButtonSize = self.font2.size(" Start ")
        self.startButtonLoc = (WIDTH/2 - self.startButtonSize[0]/2, HEIGHT/3 - self.startButtonSize[1]/2)
        self.startButtonRect = pygame.Rect(self.startButtonLoc, self.startButtonSize)
        self.startButtonRectOutline = pygame.Rect(self.startButtonLoc, self.startButtonSize)

        self.gearButtonSize = (self.gear.get_width(), self.gear.get_height())
        self.gearButtonLoc = (WIDTH - 40, 5)
        self.gearButtonRect = pygame.Rect(self.gearButtonLoc, self.gearButtonSize)

        self.debugButtonSize = (self.debug.get_width(), self.debug.get_height())
        self.debugButtonLoc = (WIDTH - 80, 5)
        self.debugButtonRect = pygame.Rect(self.debugButtonLoc, self.debugButtonSize)

        self.state = 0

    def main(self):
        if self.state == 0:
            self.show_splash_screen()
        elif self.state == 1:
            self.play()
        # elif self.state == 2:
        #      self.results()
        # elif self.state == 3:
        #     self.new_game()


    # Resets the field given the ball position
    def reset_field(self, ball_pos=(0,0),degree=0, display=Display.SPLASH):
        if degree<0 or degree>35:
            degree=0
        #SCREEN.fill(black)
        SCREEN.blit(self.background, (0,0))
        pygame.Surface.set_colorkey (self.glassboard, [0,0,0])
        SCREEN.blit(self.glassboard, (self.hx+50, self.hy-100))
        # Back Side of Hoop
        pygame.Surface.set_colorkey (self.hoop_back, [0,0,0])
        SCREEN.blit(self.hoop_back, (self.hx+2, self.hy+12))
        # Ball Itself
        if display==Display.PLAY:
            pygame.Surface.set_colorkey (self.balls[degree], [0,0,0])
            SCREEN.blit(self.balls[degree], (ball_pos[0], ball_pos[1]))
        # Front of the Hoop
        pygame.Surface.set_colorkey (self.hoop_front, [0,0,0])
        SCREEN.blit(self.hoop_front, (self.hx, self.hy))

        # Score Bar 
        score_bar = pygame.Surface((WIDTH,40), pygame.SRCALPHA) 
        score_bar.fill((255,255,255,32))  
        # self.show_score(score_bar, "Score: "+str(self.score),WIDTH/2-50,5,white,25)
        tin = pygame.font.Font('font/IndianPoker.ttf', 25)
        score_bar.blit(tin.render(self.celestialBody.name, False, white), (10, 5))
        score_bar.blit(tin.render("g:"+ str(self.celestialBody.value), False, white), (200, 5))
        
        score_bar.blit(tin.render("Score: "+str(self.score), False, white), (WIDTH/2-50, 5))
        score_bar.blit(self.gear, self.gearButtonLoc)
        score_bar.blit(self.debug, self.debugButtonLoc)
        SCREEN.blit(score_bar, (0,0))
        # Score

        if display==Display.SPLASH:
            #draw welcome text
            SCREEN.blit(self.startText, self.startLoc)
            pygame.Surface.set_colorkey (self.player, [0,0,0])
            SCREEN.blit(self.player, ((850/1400)*WIDTH, HEIGHT-580))

            #draw the start button
            pygame.draw.rect(SCREEN, RED, self.startButtonRect)
            pygame.draw.rect(SCREEN, BLACK, self.startButtonRectOutline, 2)
            SCREEN.blit(self.startButton, self.startButtonLoc)

        if self.debugEnabled:
            # Rim Front edge
            pygame.draw.rect(SCREEN,(green),self.front_rim)
            # Rim Back Edge 
            pygame.draw.rect(SCREEN,(green),self.back_glassboard)
            # Rim
            pygame.draw.rect(SCREEN, (blue),Rect(self.hx+5,self.hy+10,70,50))
            # Rim1
            pygame.draw.rect(SCREEN, (yellow),Rect(self.hx,self.hy+25,5,35))

        # if self.settingsOverlay:
        #     self.settings_pane.fill((0,0,0,200))  
        #     self.settings_pane.blit(tin.render("Celestial Body: ", False, white), (20, 40))
        #     SCREEN.blit(self.settings_pane, (WIDTH/4,HEIGHT/4))


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
            y = vy * t + (self.gravity * t * t * 0.5) + ball_pos[1]
            #print("vy", vy, "x", x + ball_pos[0], "\t", "y", y, "\t", "t", t, "\t")
            t+=0.3
            height_gained = y-ball_pos[1]
            vertex_x = ball_pos[0] - vx*(vy/self.gravity)
            vertex_y = ball_pos[1]-((0.5*vy*vy)/self.gravity)
            vfx = vx
            if vy==0:
                vfy = math.sqrt(abs((vy*vy)+(2*self.gravity*height_gained)))
            else:
                vfy = math.sqrt(abs((vy*vy)+(2*self.gravity*height_gained))) * (vy/abs(vy))
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
                    vfy = math.sqrt((vy*vy)+(2*self.gravity*height_gained))*self.lowdamp
                else:
                    vfy = -math.sqrt((vy*vy)+(2*self.gravity*height_gained))*self.lowdamp
                break
            elif (x + ball_pos[0] - self.ball_size/2 <= 0) and vx<0:
                #Hitting Left Wall
                vfx = -vx*self.highdamp
                if x + ball_pos[0] < vertex_x:
                    vfy = math.sqrt((vy*vy)+(2*self.gravity*height_gained))*self.lowdamp
                else:
                    vfy = -math.sqrt((vy*vy)+(2*self.gravity*height_gained))*self.lowdamp
                break
            elif (y + self.ball_size/2 >= HEIGHT - self.floor_height):
                #Hitting Floor 
                vfx = vx*self.lowdamp
                vfy = -math.sqrt((vy*vy)+(2*self.gravity*height_gained))*self.highdamp
                break
            elif (y <= self.ball_size/2) and vy<0:
                #Hitting Ceiling
                vfx = vx*self.lowdamp
                vfy = math.sqrt((vy*vy)+(2*self.gravity*height_gained))*self.highdamp
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


    # Render path
    def process_path(self, path, velocity, collision_point, vx, vy):
        #print("process_path", "\t", collision_point, "\t", vx, "\t", vy)
        for i in range(len(path)):
            time.sleep(.02)
            #point p on the path
            p = path[i]
            #velocity at point p
            v = velocity[i]
            if self.debugEnabled:
                print("p", p,"\t", "v", v)
            degree=round(round(p[0]%(34*3))/3)
            self.reset_field((p[0]-round(self.ball_size/2),p[1]-round(self.ball_size/2)),degree=degree, display=Display.PLAY)
            pygame.display.update() 
            rim = pygame.Rect(self.hx,self.hy+4,95,40)
            rim1 = pygame.Rect(self.hx,self.hy+25,5,35)
            rim_front_edge= pygame.Rect(self.front_rim)
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
                if self.debugEnabled:
                    print("Rim Front Edge", "\t", (p[0], p[1]), "\t", -v[0]*1.1, "\t", v[1]*1.1)
                self.skip_next_rim_check=True
                self.swish=False
                self.bounce_ball((p[0], p[1]), -v[0]*1.1, v[1]*1.1)
                break
            elif rim_back_edge.colliderect(ball_rect) and not self.skip_next_rim_check:
                #bounce off the rim edge
                if self.debugEnabled:
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
                    #print("x",self.starting_ball_pos[0])
                    if self.starting_ball_pos[0]<240:
                        self.score+=3
                    else:
                        self.score+=2
                    self.skip_next_goal_check=True
                    # Make the ball fall down after hitting the goal
                    if self.swish:
                        self.bounce_ball((p[0], p[1]), v[0]/abs(v[0]), abs(v[1]*0.8))
                    else:
                        self.bounce_ball((p[0], p[1]), v[0]/abs(v[0]), abs(v[1]*0.7))
                    self.swish=True #reset
                    time.sleep(0.1)
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
            events = pygame.event.get()
            for event in events:
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
                        if mouseRect.colliderect(self.startButtonRect):
                            self.state = 1
                            self.play_init()
                            return
                        elif mouseRect.colliderect(self.gearButtonRect):
                            if self.menu.is_enabled():
                                self.menu.disable()
                                self.menu.full_reset()
                            else:
                                self.menu.enable()
                            return
                        elif mouseRect.colliderect(self.debugButtonRect):
                            self.debugEnabled = not self.debugEnabled
                            return

            # Pass events to main_menu
            if self.menu.is_enabled():
                self.menu.mainloop(SCREEN, self.reset_field, disable_loop=False, fps_limit=60)
                #self.menu.update(events)

            # Main Program -- Start --- 
            self.reset_field((self.starting_ball_pos[0]-round(self.ball_size/2),self.starting_ball_pos[1]-round(self.ball_size/2)), display=Display.SPLASH)
            pygame.display.flip()

    def play_init(self):
        #create the new variables
        self.round = 0
        degree=round(round(self.starting_ball_pos[0]%(34*3))/3)
        self.reset_field((self.starting_ball_pos[0]-round(self.ball_size/2),self.starting_ball_pos[1]-round(self.ball_size/2)),degree=degree, display=Display.PLAY)

    def play(self):
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.debugEnabled:
                        print("MOUSEBUTTONDOWN",event.pos)
                    if event.button==1:
                        if self.gearButtonRect.collidepoint(event.pos):
                            if self.menu.is_enabled():
                                self.menu.disable()
                                self.menu.full_reset()
                            else:
                                self.menu.enable()
                        elif self.debugButtonRect.collidepoint(event.pos):
                            self.debugEnabled = not self.debugEnabled
                        else:
                            self.shoot=True
                            self.lastPos=(event.pos[0],event.pos[1])
                            path, velocity, collision_point, vx, vy  = self.calc_trajectory(self.lastPos)
                            for p in path:
                                pygame.draw.circle(SCREEN,(white),(p[0],p[1]),2)
                                pygame.display.update()
                    elif event.button==3:
                        self.shoot=False
                        self.starting_ball_pos=event.pos
                    degree=round(round(self.starting_ball_pos[0]%(34*3))/3)
                    self.reset_field((self.starting_ball_pos[0]-round(self.ball_size/2),self.starting_ball_pos[1]-round(self.ball_size/2)),degree=degree, display=Display.PLAY)
                elif event.type == pygame.MOUSEMOTION:
                    if self.shoot:
                        degree=round(round(self.starting_ball_pos[0]%(34*3))/3)
                        self.reset_field((self.starting_ball_pos[0]-round(self.ball_size/2),self.starting_ball_pos[1]-round(self.ball_size/2)),degree=degree, display=Display.PLAY)
                        self.lastPos=(event.pos[0],event.pos[1])
                        path, velocity, collision_point, vx, vy = self.calc_trajectory(self.lastPos)
                        for p in path:
                            pygame.draw.circle(SCREEN,(white),(p[0],p[1]),2)
                            pygame.display.update()
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.shoot:
                        #print("Mouse Up")
                        degree=round(round(self.starting_ball_pos[0]%(34*3))/3)
                        self.reset_field((self.starting_ball_pos[0]-round(self.ball_size/2),self.starting_ball_pos[1]-round(self.ball_size/2)),degree=degree, display=Display.PLAY)
                        if event.button==1:
                            path, velocity, collision_point, vx, vy  = self.calc_trajectory(self.lastPos)
                            self.process_path(path, velocity, collision_point, vx, vy)
                            self.shoot=False

        if self.menu.is_enabled():
            self.menu.mainloop(SCREEN, self.reset_field, disable_loop=False, fps_limit=60)

        pygame.display.flip()

#############################################################
if __name__ == "__main__":
	os.environ['SDL_VIDEO_CENTERED'] = '1' #center SCREEN
	pygame.init()
	pygame.display.set_caption("Hoops")
	SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
	Runit = Hoops()
	Myclock = pygame.time.Clock()
	while 1:
		Runit.main()
		Myclock.tick(64)