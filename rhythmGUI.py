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

rhyDotLen = 22
rhythmIterator = 0
ghostIterator = [0]

    # convention for button states   ->   up/core = 0, down/trivial = 1
upDownClick = False
lastUpDownClicked = 0
ctState = 0
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

    pygame.draw.ellipse(workingDisplay,(50,150,50),(sandboxRect.left-5, sandboxRect.top-5,
                                                         sandboxRect.width+10, sandboxRect.height+10))
    
    workingDisplay.blit(sandboxText, sandboxRect)
    sandboxBackdrop.blit(workingDisplay, (0,0))
    
    # toolkit buttons and page counter
    global pageCounter
    buttons.add(Button(['images/up_button_unpressed.png', 'images/up_button_pressed.png'],
                                   (disp_width/3-100,75), ('UpDown', 0)))
    buttons.add(Button(['images/down_button_unpressed.png', 'images/down_button_pressed.png'],
                                   (disp_width/3-50,75), ('UpDown', 1)))
    buttons.add(Button(['images/core_button_unpressed.png', 'images/core_button_pressed.png'],
                        (40,75), ('CT', 0)))
    buttons.add(Button(['images/trivial_button_unpressed.png', 'images/trivial_button_pressed.png'],
                        (84,75), ('CT', 1)))
    pageCounter.add(PageCounter((disp_width/3-74, 76)))
    
    Display.blit(workingDisplay,(0,0))
    
    update_all()


# classes and groups
class Button(pygame.sprite.Sprite):
    def __init__(self, graphics: list, pos: tuple, type: tuple) -> None: # graphics: [unpressed, pressed]
        pygame.sprite.Sprite.__init__(self)
        self.type = type
        self.graphics = graphics

        if self.type[0] == 'UpDown':
            self.status = 0
        elif self.type[0] == 'CT':
            self.status = ctState

        self.image = pygame.image.load(self.graphics[self.status]).convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)
        
    def click(self) -> None:   #toggle on/off 
        global ctState
        if self.type[0] == 'UpDown':
            if self.status == 0:
                self.status = 1
                global lastUpDownClicked, upDownClick
                lastUpDownClicked, upDownClick = self.type[1], True
                if self.type[1] == 0:    
                    if pageCounter.sprites()[0].page < 5 and ctState == 0:
                        pageCounter.sprites()[0].page += 1
                if self.type[1] == 1:
                    if pageCounter.sprites()[0].page > 1:
                        pageCounter.sprites()[0].page -= 1
            else:
                self.status = 0
                upDownClick = False

        if self.type[0] == 'CT':
            if self.type[1] != self.status:
                ctState = self.type[1]
                pageCounter.sprites()[0].page = 1
                global ghostIterator
                ghostIterator = [0]

    def update(self) -> None:
        if self.type[0] == 'CT':
            self.status = ctState
            if self.type[1] == self.status:
                self.image = pygame.image.load(self.graphics[1]).convert_alpha()
            elif self.type[1] != self.status:
                self.image = pygame.image.load(self.graphics[0]).convert_alpha()
        if self.type[0] == 'UpDown':
            self.image = pygame.image.load(self.graphics[self.status]).convert_alpha()
buttons = pygame.sprite.Group()

class PageCounter(pygame.sprite.Sprite):
    def __init__(self, pos: tuple) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.page = 1
        self.image = pygame.Surface((22,22))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(topleft = pos)
        self.text = miniFont.render((" " + str(self.page)), True, BLACK)
        
    def update(self) -> None:
        self.text = miniFont.render((" " + str(self.page)), True, BLACK)
        self.image.fill(WHITE)
        self.image.blit(self.text,(0,0))     
pageCounter = pygame.sprite.GroupSingle()    

class Rhythm(pygame.sprite.Sprite):
    def __init__(self, ctState: int, rhythmIterator: int, rowCount:int , rowLength: int) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.image = Rhythm.rhythm_surface(coresAndTrivials[ctState][rhythmIterator])
        self.pos = (rowLength, rowCount*50+102)
        self.rect = self.image.get_rect(topright = self.pos)
        self.binary = coresAndTrivials[ctState][rhythmIterator]

    # I : binary string / O : surface with visual rhythm
    def rhythm_surface(rhythm: str) -> pygame.Surface:
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
rhythms = pygame.sprite.Group()

class ActiveRhythm(pygame.sprite.Sprite):
    def __init__(self, binary: str, pos: tuple) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.binary = binary
        self.image = Rhythm.rhythm_surface(binary)
        self.rect = self.image.get_rect(center = pos)
    
    def update(self, rel: tuple) -> None:
        self.rect = self.rect.move((rel[0], rel[1]))

activeRhythms = pygame.sprite.Group()
pickedUpRhythm = pygame.sprite.GroupSingle()

def update_rhythms(ctState, rhythmPage) -> None:
    rhythms.empty()       
    rowCount = 0
    global ghostIterator
    rhythmIterator = (ghostIterator[rhythmPage-1] - 1)

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
                rhythms.add(Rhythm(ctState, rhythmIterator, rowCount, rowLength))
            else:
                break

        rowCount += 1
    # record last rhythm to start off with next time
    ghostIterator.append(rhythmIterator)

def update_all():
    buttons.update()
    pageCounter.update()
    update_rhythms(ctState, pageCounter.sprite.page)

    buttons.draw(Display)
    pageCounter.draw(Display)
    rhythms.draw(Display)
    activeRhythms.draw(Display)

# init display
Display.blit(workingDisplay,(0,0))
pygame.display.update()

# game loop
while True:
    
    if len(pickedUpRhythm.sprites()):
            pickedUpRhythm.sprite.update(pygame.mouse.get_rel())
            Display.blit(workingDisplay,(0,0))
            update_all()    

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        
        if event.type == MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # clickable top menu opbjects
            if homeRect.collidepoint(mouse_pos):
                print('homescreen')
                
            if sandboxRect.collidepoint(mouse_pos):
                sandbox_init()

            '''    
            if practiceRect.collidepoint(pos):
                pygame.draw.ellipse(Display,(120,130,130),(sandboxRect.left-5, sandboxRect.top-5,
                                                           sandboxRect.width+10, sandboxRect.height+10))
                Display.blit(sandboxText, sandboxRect)
                pygame.draw.ellipse(Display,(50,150,50),(practiceRect.left-5, practiceRect.top-5,
                                                         practiceRect.width+10, practiceRect.height+10))
                Display.blit(practiceText, practiceRect)
            '''

            if guideRect.collidepoint(mouse_pos):
                print('guide screen')
                
            if settingsRect.collidepoint(mouse_pos):
                print('settings')

            # clicking up/down core/trivial buttons
            if len(buttons.sprites()):
                buttons_list = buttons.sprites()
                for x in range(0, len(buttons_list)):
                    if buttons_list[x].rect.collidepoint(mouse_pos):
                        print(f'collision with {buttons_list[x].type}'.format())
                        Display.blit(workingDisplay,(0,0))
                        buttons_list[x].click()
                        update_all()

            # picking up rhythms   
            if len(rhythms.sprites()):
                rhythms_list = rhythms.sprites()
                for x in range(0,len(rhythms_list)):
                    if rhythms_list[x].rect.collidepoint(mouse_pos):
                        pygame.mouse.get_rel()
                        new_rhythm = ActiveRhythm(rhythms_list[x].binary, (mouse_pos))
                        activeRhythms.add(new_rhythm)
                        pickedUpRhythm.add(new_rhythm)
                        update_all()

        if event.type == MOUSEBUTTONUP:

            # unclicking up/down buttons
            if upDownClick:
                buttons.sprites()[lastUpDownClicked].click()
                buttons.update()
                buttons.draw(Display)

            if len(pickedUpRhythm.sprites()):
                Display.blit(workingDisplay,(0,0))
                if pickedUpRhythm.sprite.rect.centerx < disp_width/3 or pickedUpRhythm.sprite.rect.top < 100:
                    pickedUpRhythm.sprite.kill()
                pickedUpRhythm.empty()
                update_all()
                    
                    
    pygame.display.update()