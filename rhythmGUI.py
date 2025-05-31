#!/usr/bin/env python3
import pygame, sys
from pygame.locals import *
import matrixGen2
import pygame_menu as pm

#display init
pygame.init()
Display = pygame.display.set_mode((500, 400),0,32)
pygame.display.set_caption('The Rhythm Trainer')

#color setup
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

Display.fill((120,130,130))

#text
basicFont = pygame.font.SysFont('Serif', 48)
text = basicFont.render('Hello world!', True, RED)
# Display.blit(text, (0,0))
textRect = text.get_rect()
textRect.centerx = Display.get_rect().centerx
textRect.centery = Display.get_rect().centery



# function which takes a binary string and outputs a surface with visual rhythm
def rhythmSurface(rhythm):
    w = 20
    rhy_surf = pygame.Surface((w, 43))
    rhy_surf.fill(WHITE)
    for j in range(0,len(rhythm)):
        print(rhythm[j])
        if rhythm[j] == "1":
            w += 20
            temp = rhy_surf
            rhy_surf = pygame.Surface((w, 43))
            rhy_surf.fill(WHITE)
            rhy_surf.blit(temp, (0,0))
            pygame.draw.circle(rhy_surf, BLACK, (22*j+10,11), 10)
        elif rhythm[j] == "0":
            w += 20
            temp = rhy_surf
            rhy_surf = pygame.Surface((w, 43))
            rhy_surf.fill(WHITE)
            rhy_surf.blit(temp, (0,0))
            pygame.draw.circle(rhy_surf, BLACK, (22*j+10,32), 10, 2)
    return rhy_surf


Display.blit(rhythmSurface('100101000'), (10,10))



pygame.display.update()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    
    '''
    for x in range(0, len(data[n])):
        print(data[n][x])
    '''
