import random
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)
magenta = (255, 0, 255)
cyan = (5, 255, 234)
white = (255, 255, 255)
black  = (0, 0, 0)
DG = (45, 45, 45)
LG = (70, 70, 70)
murkybrownorange = (163, 104, 20)
def randcol():
    R = random.randint(0, 255)
    G = random.randint(0, 255)
    B = random.randint(0, 255)
    RGB = (R, G, B)
    return RGB
