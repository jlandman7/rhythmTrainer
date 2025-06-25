#!/usr/bin/env python3
import pygame, sys
from pygame.locals import *
import matrixGen3
from matrixGen3 import data, cores, trivials

# display init
pygame.init()
disp_width = 1300
disp_height = 800
Display = pygame.display.set_mode((disp_width, disp_height),0,32)
pygame.display.set_caption('The Rhythm Trainer')

workingDisplay = pygame.Surface((disp_width,disp_height))
workingDisplay.fill((120,130,130))

sandboxBackdrop = pygame.Surface((disp_width,disp_height))

# vars init
mode = 0

activeRhythms = []
rhythmInstances = []
rhyDotLen = 22

upAndDownButtons = []
upDownClick = False
lastUpDownClicked = 0

pageCounter = []

rhythmIterator = 0
ghostIterator = [0]
coreAndTrivialButtons = []
    # 0 is core, 1 is trivial
coreVsTrivialMode = 0
coresAndTrivials = [cores,trivials]

# colors init
BLACK = (0,0,0)
WHITE = (255,255,255)
AQUA = (0,200,155)
ORANGE = (180,70,30)

# Fonts init
homeFont = pygame.font.SysFont('Serif', 48)
headerFont = pygame.font.SysFont('Serif',28)
subHeaderFont = pygame.font.SysFont('Serif',22)
miniFont = pygame.font.SysFont('Serif',16)

# Top menu text + line
homeText = homeFont.render(' Rhythm Trainer ', True, AQUA)
homeRect = homeText.get_rect(center = (disp_width/2, 35))
workingDisplay.blit(homeText, homeRect)

sandboxText = headerFont.render(' Sandbox ', True, AQUA)
sandboxRect = sandboxText.get_rect(center = (disp_width/10, 35))
workingDisplay.blit(sandboxText, sandboxRect)

practiceText = headerFont.render(' Practice ', True, AQUA)
practiceRect = practiceText.get_rect(center = (disp_width/4 , 35))
workingDisplay.blit(practiceText, practiceRect)

guideText = headerFont.render(' Guide ', True, AQUA)
guideRect = guideText.get_rect(center = (3*disp_width/4 , 35))
workingDisplay.blit(guideText, guideRect)

settingsText = headerFont.render(' Settings ', True, AQUA)
settingsRect = settingsText.get_rect(center = (9*disp_width/10 , 35))
workingDisplay.blit(settingsText, settingsRect)

pygame.draw.line(workingDisplay, BLACK,(0,70),(disp_width,70))


                     # graphics: [unpressed, pressed]
class Button:
    def __init__(self, graphics: list, pos: tuple) -> None:
        self.status = 0
        self.graphics = graphics
        self.surf = pygame.image.load(self.graphics[self.status]).convert_alpha()
        self.rect = self.surf.get_rect(topleft = pos)
        Display.blit(self.surf, self.rect)

    def click(self) -> None:   #toggle on/off, update display
        if self.status == 0:
            self.status = 1
            self.surf = pygame.image.load(self.graphics[self.status]).convert_alpha()
        else:
            self.status = 0
            self.surf = pygame.image.load(self.graphics[self.status]).convert_alpha()

        Display.blit(self.surf, self.rect)
        return self.status

    def update() -> None:
        self.surf = pygame.image.load(self.graphics[self.status]).convert_alpha()
        Display.blit(self.surf, self.rect)


class PageCounter:
    def __init__(self, pos: tuple) -> None:
        self.page = 1
        self.surf = pygame.Surface((22,22))
        self.surf.fill(WHITE)
        self.rect = self.surf.get_rect(topleft = pos)
        self.text = miniFont.render(str(self.page), True, BLACK)
        Display.blit(self.surf, self.rect)
        Display.blit(self.text, self.rect)

                          # Press: 0 - when up/down is pressed, Reset: 1 - when core/trivial is pressed
                                        # direction: 0 is up, 1 is down
    def page_change(self, pressVsReset, direction = 0) -> None:
        if pressVsReset == 0:
            if not direction:
                if self.page < 5 and coreVsTrivialMode == 0:
                    self.page += 1
            else:
                if self.page != 1:
                    self.page -= 1
        else:
            self.page = 1

        self.text = miniFont.render(str(self.page), True, BLACK)
        Display.blit(self.surf, self.rect)
        Display.blit(self.text, self.rect)
    

class Rhythm:
    def __init__(self, ctState, rhythmIterator, rowCount, rowLength) -> None:
        self.surface = rhythm_surface(coresAndTrivials[ctState][rhythmIterator])
        self.pos = (rowLength, rowCount*50+102)
        self.rect = self.surface.get_rect(topright = self.pos)
        self.binary = coresAndTrivials[ctState][rhythmIterator]
        
        Display.blit(self.surface, self.rect)

    def move(rel: tuple) -> None:
        self.pos = (self.pos[0]+rel[0], self.pos[1]+rel[1])
        self.rect = self.surface.get_rect(topright = self.pos)
        
        Display.blit(self.surface, self.rect)
    
    

# I : binary string / O : surface with visual rhythm
def rhythm_surface(rhythm) -> 'surface':
    w = 0
    rhy_surf = pygame.Surface((w, 2*rhyDotLen-1))
    rhy_surf.fill(WHITE)
    for j in range(0,len(rhythm)):
        if rhythm[j] == "1":
            w += rhyDotLen
            temp = rhy_surf
            rhy_surf = pygame.Surface((w, 2*rhyDotLen-1))
            rhy_surf.fill(WHITE)
            rhy_surf.blit(temp, (0,0))
            pygame.draw.circle(rhy_surf, BLACK, (rhyDotLen*j+11,11), 10)
        elif rhythm[j] == "0":
            w += rhyDotLen
            temp = rhy_surf
            rhy_surf = pygame.Surface((w, 2*rhyDotLen-1))
            rhy_surf.fill(WHITE)
            rhy_surf.blit(temp, (0,0))
            pygame.draw.circle(rhy_surf, BLACK, (rhyDotLen*j+11,32), 10, 2)
    return rhy_surf 
    

def rhythm_pop(ctState, rhythmPage) -> None:
    rhythmInstances = []
    rowCount = 0
    global ghostIterator
    rhythmIterator = ghostIterator[rhythmPage-1]-1

    if rhythmPage < len(ghostIterator):
        ghostIterator.pop()

    # while height isn't filled: reset row length, fill row, increment rowCount
    while rowCount*50 + 2 < disp_height-100:
        rowLength = 10

        # while row isn't filled: increment to next rhythm, update length, fill in rhythm
        while rowLength + rhyDotLen*len(coresAndTrivials[ctState][rhythmIterator]) < disp_width/3 - 22:
            if rhythmIterator+1 < len(coresAndTrivials[ctState]):
                rhythmIterator += 1
                rowLength += rhyDotLen*len(coresAndTrivials[ctState][rhythmIterator]) + 5
                rhythmInstances.append(Rhythm(ctState, rhythmIterator, rowCount, rowLength))
            else:
                break

        rowCount += 1

    ghostIterator.append(rhythmIterator)


def sandbox_init() -> None:
    global mode
    mode = 'sandbox'
    
    # toolkit/workspace  background/text/lines  onto workingDisplay
    toolkit_surf = pygame.Surface((disp_width/3,Display.get_height()-71))
    toolkit_surf.fill((60,60,60))
    toolkit_rect = toolkit_surf.get_rect(topleft = (0,70))
    workingDisplay.blit(toolkit_surf, toolkit_rect)
    toolkit_text = headerFont.render(' Toolkit ', True, ORANGE)
    toolkit_text_rect = toolkit_text.get_rect(center = (disp_width/6,85))
    workingDisplay.blit(toolkit_text,toolkit_text_rect)
    workspace_surf = pygame.Surface((disp_width*2/3-2,disp_height-71))
    workspace_surf.fill((220,220,220))
    workspace_rect = workspace_surf.get_rect(topleft = (disp_width/3+2,70))
    workingDisplay.blit(workspace_surf, workspace_rect)
    workspace_text = headerFont.render(' Workspace ',True, (120, 30, 180))
    workspace_rect = workspace_text.get_rect(center = (2*disp_width/3+1,85))
    workingDisplay.blit(workspace_text,workspace_rect)
    pygame.draw.line(workingDisplay, BLACK, (disp_width/3,70),(disp_width/3,disp_height),2)
    pygame.draw.line(workingDisplay, BLACK, (0,100), (disp_width,100))

    Display.blit(workingDisplay, (0,0))
    
    # toolkit buttons and page counter
    global upAndDownButtons, pageCounter
    upAndDownButtons.append(Button(['images/up_button_unpressed.png', 'images/up_button_pressed.png'],
                                   (disp_width/3-100,75)))
    upAndDownButtons.append(Button(['images/down_button_unpressed.png', 'images/down_button_pressed.png'],
                                   (disp_width/3-50,75)))
    pageCounter = PageCounter((disp_width/3-74, 76))
    coreAndTrivialButtons.append(Button(
        ['images/core_button_unpressed.png', 'images/core_button_pressed.png'], (40,75)))
    coreAndTrivialButtons.append(Button(
        ['images/trivial_button_unpressed.png', 'images/trivial_button_pressed.png'], (84,75)))
    coreAndTrivialButtons[0].click()

    sandboxBackdrop.blit(workingDisplay,(0,0))

    # ctState : 0  -  core page : 1
    rhythm_pop(0, 1)


#run program
Display.blit(workingDisplay,(0,0))
pygame.display.update()
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        
        if event.type == MOUSEBUTTONDOWN:

            # clickable top menu opbjects
            if homeRect.collidepoint((pygame.mouse.get_pos())):
                print('homescreen')
                
            if sandboxRect.collidepoint((pygame.mouse.get_pos())):
                pygame.draw.ellipse(Display,(120,130,130),(practiceRect.left-5, practiceRect.top-5,
                                                           practiceRect.width+10, practiceRect.height+10))
                Display.blit(practiceText, practiceRect)
                pygame.draw.ellipse(Display,(50,150,50),(sandboxRect.left-5, sandboxRect.top-5,
                                                         sandboxRect.width+10, sandboxRect.height+10))
                Display.blit(sandboxText, sandboxRect)
                sandbox_init()
                
            if practiceRect.collidepoint((pygame.mouse.get_pos())):
                pygame.draw.ellipse(Display,(120,130,130),(sandboxRect.left-5, sandboxRect.top-5,
                                                           sandboxRect.width+10, sandboxRect.height+10))
                Display.blit(sandboxText, sandboxRect)
                pygame.draw.ellipse(Display,(50,150,50),(practiceRect.left-5, practiceRect.top-5,
                                                         practiceRect.width+10, practiceRect.height+10))
                Display.blit(practiceText, practiceRect)
                
            if guideRect.collidepoint((pygame.mouse.get_pos())):
                print('guide screen')
                
            if settingsRect.collidepoint((pygame.mouse.get_pos())):
                print('settings')

            # clicking up/down core/trivial buttons
            if len(upAndDownButtons):
                for x in range(0,len(upAndDownButtons)):
                    if upAndDownButtons[x].rect.collidepoint((pygame.mouse.get_pos())):

                        Display.blit(workingDisplay,(0,0))
                        pageCounter.page_change(0,x)
                        Display.blit(upAndDownButtons[(x+1)%2].surf, upAndDownButtons[(x+1)%2].rect)
                        upAndDownButtons[x].click()
                        Display.blit(coreAndTrivialButtons[0].surf, coreAndTrivialButtons[0].rect)
                        Display.blit(coreAndTrivialButtons[1].surf, coreAndTrivialButtons[1].rect)
                        
                        rhythm_pop(coreVsTrivialMode, pageCounter.page)
                        lastUpDownClicked = x
                        upDownClick = True
            
            if len(coreAndTrivialButtons):
                for x in range(0,len(coreAndTrivialButtons)):
                    if (coreAndTrivialButtons[x].rect.collidepoint((pygame.mouse.get_pos())) and
                                                                  coreVsTrivialMode != x):

                        ghostIterator = [0]
                        Display.blit(workingDisplay, (0,0))
                        Display.blit(upAndDownButtons[0].surf, upAndDownButtons[0].rect)
                        Display.blit(upAndDownButtons[1].surf, upAndDownButtons[1].rect)

                        coreAndTrivialButtons[0].click()
                        coreAndTrivialButtons[1].click()

                        Display.blit(coreAndTrivialButtons[0].surf, coreAndTrivialButtons[0].rect)
                        Display.blit(coreAndTrivialButtons[1].surf, coreAndTrivialButtons[1].rect)

                        coreVsTrivialMode = x
                        pageCounter.page_change(pressVsReset = 1)
                        
                        rhythm_pop(coreVsTrivialMode, pageCounter.page)
                        

            '''  
            # move rhythm rectangles
            if mode == 'sandbox':
                for i in range(len(rhythmInstances)):
                    if rhythmInstances[i].collidepoint((pygame.mouse.get_pos())):
                        activeRhythms.append(rhythmInstances[i])
                        while event.type != MOUSEBUTTONUP:
                         activeRhythms[len(activeRhythms)].move()
            '''
            
        if event.type == MOUSEBUTTONUP:

            # unclicking up/down buttons
            if upDownClick:
                upAndDownButtons[lastUpDownClicked].click()
                upDownClick = False

                    
    pygame.display.update()
