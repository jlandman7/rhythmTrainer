#!/usr/bin/env python3
import pygame, sys
from pygame.locals import *
import matrixGen3
from matrixGen3 import data, cores, trivials

### display init ---------------------------------------------
pygame.init()
disp_width = 1300
disp_height = 800
Display = pygame.display.set_mode((disp_width, disp_height),0,32)
pygame.display.set_caption('The Rhythm Trainer')
workingDisplay = pygame.Surface((disp_width,disp_height))
workingDisplay.fill((120,130,130))
sandboxBackdrop = pygame.Surface((disp_width,disp_height))

### vars init ------------------------------------------------
mode = 0
updateNeeded = False
rhyDotLen = 22
rhythmIterator = 0
ghostIterator = [0]
upDownClick = False  #up/core = 0, down/trivial = 1
lastUpDownClicked = 0
playbackClick = False
lastPlaybackClicked = 0
ctState = 0
coresAndTrivials = [cores,trivials]
clock = pygame.time.Clock()
loadedSound = pygame.mixer.Sound('sounds/bongo4_cymatics.wav')
# loadedSound2 = pygame.mixer.Sound('sounds/shaker6_cymatics.wav')
sounds = [pygame.mixer.Sound(x) for x in ('sounds/snare.wav','sounds/kick.wav',
                                          'sounds/ride.wav','sounds/hihat.wav')]
subdivHighlighter = 0
update_needed = False

### Colors and fonts init -------------------------------------
BLACK = (0,0,0)
WHITE = (255,255,255)
AQUA = (0,200,155)
ORANGE = (180,70,30)
WORKSPACEPURPLE = (120, 30, 180)
homeFont = pygame.font.SysFont('Serif', 48)
headerFont = pygame.font.SysFont('Serif',28)
subHeaderFont = pygame.font.SysFont('Serif',22)
miniFont = pygame.font.SysFont('Serif',16)
colors = [(236,146,48), (237,35,51), (207,102,205), (233,60,160),
          (233,209,67), (144, 208, 68), (96,99,205), (109, 157, 205)]

### classes and groups ----------------------------------------
sprites = pygame.sprite.Group()

class Button(pygame.sprite.Sprite):
    def __init__(self, graphics, pos: tuple, type: tuple) -> None: # graphics: [unpressed, pressed]
        pygame.sprite.Sprite.__init__(self)
        self.type = type
        if type[0] == 'home':
            if type[1] == 0:
                self.image = homeFont.render(graphics, True, AQUA)
            else:
                self.image = headerFont.render(graphics, True, AQUA)
            self.rect = self.image.get_rect(center = (pos, 35))
        else:
            self.graphics: list = graphics
            if self.type[0] == 'CT':
                self.status = ctState
            else:
                self.status = 0
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
                    if counters.sprites()[0].num < 5 and ctState == 0:
                        counters.sprites()[0].num += 1
                elif self.type[1] == 1:
                    if counters.sprites()[0].num > 1:
                        counters.sprites()[0].num -= 1
            else:
                self.status = 0
                upDownClick = False

        elif self.type[0] == 'CT':
            if self.type[1] != self.status:
                ctState = self.type[1]
                counters.sprites()[0].num = 1
                global ghostIterator
                ghostIterator = [0]
        
        elif self.type[0] == 'playback':
            # set up unclicking
            if self.status == 0:
                global playbackClick, lastPlaybackClicked
                self.status = 1
                playbackClick = True
                lastPlaybackClicked = self.type[1]
            else:
                self.status = 0

            # click play button -> play
            global timer
            if self.type[1] == 0 and timer.active == False:
                timer = Timer(counters.sprites()[1].num, counters.sprites()[2].num)
            # click pause/stop button -> pause/return home
            elif self.type[1] and timer.active == True:
                timer.deactivate()
            if self.type[1] == 2:
                highlighter.sprite.return_home()

        elif self.type[0] == 'onOff':
            if self.status == 0:
                self.status = 1
            else:
                self.status = 0
        
        elif self.type[0] == 'home':
            if self.type[1] == 0:
                print('homescreen')
            elif self.type[1] == 1:
                sandbox_init()
            elif self.type[1] == 2:
                print('practice screen')
            elif self.type[1] == 3:
                print('guide screen')
            elif self.type[1] == 4:
                print('settings screen')

    def update(self) -> None:
        if self.type[0] == 'CT':
            self.status = ctState
            if self.type[1] == self.status:
                self.image = pygame.image.load(self.graphics[1]).convert_alpha()
            elif self.type[1] != self.status:
                self.image = pygame.image.load(self.graphics[0]).convert_alpha()
        elif self.type[0] == 'UpDown' or self.type[0] == 'playback' or self.type[0] == 'onOff':
            self.image = pygame.image.load(self.graphics[self.status]).convert_alpha()
buttons = pygame.sprite.Group()
playbackButtons = pygame.sprite.Group()
homeButtons = pygame.sprite.Group()

class Counter(pygame.sprite.Sprite):
    def __init__(self, pos: tuple, default_num: int) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.num = default_num
        if self.num == 1:
            self.image = pygame.Surface((22, 22))
        elif self.num == 60:
            self.image = pygame.Surface((34, 22))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(topleft = pos)
        self.text = miniFont.render((str(self.num)), True, BLACK)
        
    def update(self) -> None:
        self.text = miniFont.render((str(self.num)), True, BLACK)
        self.image.fill(WHITE)
        self.image.blit(self.text, (3,3))    
counters = pygame.sprite.Group()    

class Rhythm(pygame.sprite.Sprite):
    def __init__(self, ctState: int, rhythmIterator: int, rowCount:int , rowLength: int) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.image = Rhythm.rhythm_surface(coresAndTrivials[ctState][rhythmIterator])
        self.pos = (rowLength, rowCount*50+102)
        self.rect = self.image.get_rect(topright = self.pos)
        self.binary = coresAndTrivials[ctState][rhythmIterator]

    # I : binary string / O : surface with visual rhythm
    def rhythm_surface(rhythm: str,*,color: int = -1) -> pygame.Surface:
        w = 0
        rhy_surf = pygame.Surface((w, 2*rhyDotLen-1))
        if color>=0:
            filler = colors[color]
        else:
            filler = WHITE
            rhy_surf.fill(filler)
        for j in range(0,len(rhythm)):
            if rhythm[j] == "1":
                w += rhyDotLen
                temp = rhy_surf
                rhy_surf = pygame.Surface((w, 2*rhyDotLen-1))
                rhy_surf.fill(filler)
                rhy_surf.blit(temp, (0,0))
                pygame.draw.circle(rhy_surf, BLACK, (rhyDotLen*j+11,11), 10)
            elif rhythm[j] == "0":
                w += rhyDotLen
                temp = rhy_surf
                rhy_surf = pygame.Surface((w, 2*rhyDotLen-1))
                rhy_surf.fill(filler)
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
        self.grid_pos = (round((self.rect.left - (disp_width / 3)) / 22) , 
                         round((self.rect.top - 100) / 44))
        self.move_bool = False
        self.sound = 0
    
    def permutate(self) -> None:
        self.binary = self.binary[1:]+self.binary[0]
        self.image = Rhythm.rhythm_surface(self.binary, color = self.sound)

    def move(self, rel: tuple) -> None:
        self.rect = self.rect.move((rel[0], rel[1]))
        self.move_bool = True

    def soundChange(self, newSound: int):
        self.sound = newSound
        self.image = Rhythm.rhythm_surface(self.binary, color = self.sound)

    def snap(self) -> None:
        pos = self.rect.topleft
        snap_by = (((pos[0] - int(disp_width / 3)) %22, 
                    (pos[1] - 100) % 44))
        self.rect = self.rect.move((-snap_by[0]+2, -snap_by[1]+1))
        self.grid_pos = (round((self.rect.left - (disp_width / 3)) / 22) , 
                         round((self.rect.top - 100) / 44))
activeRhythms = pygame.sprite.Group()
pickedUpRhythm = pygame.sprite.GroupSingle()

class Dragger(pygame.sprite.Sprite):
    def __init__(self,  pos: tuple, type: str) -> None:
        pygame.sprite.Sprite.__init__(self)
        graphics = ['images/dragger_0.png', 'images/dragger_1.png']
        self.graphics = [pygame.image.load(x).convert() for x in graphics]
        self.status = 0
        self.image = self.graphics[0]
        self.type = type
        self.pos = pos
        self.rect = self.image.get_rect(topleft = pos)

    def animate(self) -> None:
        if self.status == 0: 
            self.status = 1
        else: 
            self.status = 0
        self.image = self.graphics[self.status]

    def update(self, dir_dragged: str = 'none') -> None:
        if self.type == 'metronome':
            if dir_dragged == 'up' and counters.sprites()[1].num < 300:
                counters.sprites()[1].num += 1
            elif dir_dragged == 'down' and counters.sprites()[1].num > 1:
                counters.sprites()[1].num -= 1  
        elif self.type == 'subdivision':
            if dir_dragged == 'up' and counters.sprites()[2].num < 9:
                counters.sprites()[2].num += 1
            elif dir_dragged == 'down' and counters.sprites()[2].num > 1:
                counters.sprites()[2].num -= 1
        if dir_dragged != 'none':
            self.animate()
draggers = pygame.sprite.Group()      
clickedDragger = pygame.sprite.GroupSingle()  

class Kernel(pygame.sprite.Sprite):
    def __init__(self, LR: str) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.LR = LR
        if LR == 'left':
            self.image = pygame.image.load('images/left_kernel.png')
            self.rect = self.image.get_rect(midleft = (disp_width/3 - 2, 103))
        elif LR == 'right':
            self.image = pygame.image.load('images/right_kernel.png')
            self.rect = self.image.get_rect(midleft = (disp_width/3 + 87, 103))
        self.grid_pos = round((self.rect.left - disp_width/3) / 22)

    
    def move(self, rel: int) -> None:
        if self.LR == 'left':
            if self.rect.right + rel < kernels.sprites()[1].rect.left-1 and self.rect.left > disp_width/3-3:
                self.rect.move_ip(rel, 0)
        elif self.LR == 'right':
            if self.rect.left + rel > kernels.sprites()[0].rect.right+1 and self.rect.right + rel < disp_width + 2:
                self.rect.move_ip(rel, 0)
    
    def snap(self) -> None:
        snap_by = (self.rect.left - disp_width / 3) % 22
        if self.LR == 'left' and self.rect.left - snap_by > disp_width / 3:
            self.rect.move_ip(-snap_by - 2,0)
        elif self.LR == 'right':
            self.rect.move_ip(22-snap_by,0)
        self.rect.move_ip(-(self.rect.left - disp_width / 3) % 22 - 2, 0)
        self.grid_pos = round((self.rect.left - disp_width/3) / 22)
kernels = pygame.sprite.Group()
clickedKernel = pygame.sprite.GroupSingle()

class Highlighter(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((21, disp_height - 141))
        self.image.fill((200,200,0))
        self.rect = self.image.get_rect(topleft = (disp_width / 3 + 2, 101))
        self.grid_pos = 0
        self.sounds = []

    def return_home(self):
        self.rect.move_ip(kernels.sprites()[0].rect.left + 4 - self.rect.left, 0)

    def step(self):
        self.rect.move_ip(22,0)
    
    # turns highlighter red and plays sound
    def chameleon(self):
        self.image.fill((200, 0, 0))
        self.sounds.append(loadedSound)

    def dechameleon(self):
        self.image.fill((200, 200, 0))

    # if colliding with active rhythm, play any beats hovering on
    def rhythm_collisions(self):
        if buttons.sprites()[5].status == 0:
            for x in activeRhythms.sprites():
                if self.rect.colliderect(x.rect):
                    highlighted_pos = self.grid_pos - x.grid_pos[0]
                    print(self.grid_pos)
                    try:
                        if x.binary[highlighted_pos] == '1':
                            self.sounds.append(sounds[x.sound])
                    except IndexError: pass

    def play_sounds(self):
        if self.sounds:
            for x in self.sounds:
                x.play()
            self.sounds = []

    def reset(self):
        self.grid_pos = round((self.rect.left - (disp_width / 3)) / 22)
        if buttons.sprites()[5].status == 0:
            self.rhythm_collisions()
        # keep chameleon skin for 1 beat
        if timer.sub_iterator == 1:
            self.dechameleon()
        # update position for rhycollide, play and empty sounds
        self.play_sounds()

    def move(self):
        # after a subdivision: decham, step or return home, check rhycollide
        if self.grid_pos < kernels.sprites()[1].grid_pos - 1:
            self.step()
        else:
            self.return_home()
highlighter = pygame.sprite.GroupSingle()

class Timer:
    def __init__(self, bpm = 1, subdivs = 1):
        self.sub_iterator = 0
        if bpm == 1 and subdivs == 1:
            self.active = False
        else:
            self.active = True
            self.pulse(counters.sprites()[1].num, counters.sprites()[2].num)
            highlighter.sprite.reset()
            self.AV_update()
            
    def subdivision(self):
        self.sub_iterator += 1
        highlighter.sprite.move()
        self.AV = True

    def deactivate(self):
        self.active = False
        highlighter.sprite.sounds = []
        self.start_time = 0

    def pulse(self, bpm = 1, subdivs = 1):
        if self.active:
            # initialize
            self.duration = 60 / bpm * 1000
            self.sub_duration = self.duration / subdivs
            self.start_time = pygame.time.get_ticks()
            self.sub_iterator = 0

            if buttons.sprites()[4].status == 0:
                highlighter.sprite.chameleon()
            self.AV = True


    def AV_update(self):
        highlighter.sprite.reset()
        global update_needed
        update_needed = True
        self.AV = False

    def update(self):
        current_time = pygame.time.get_ticks()
        elapsed =  (current_time - self.start_time)
        if elapsed - (self.sub_duration * self.sub_iterator) >= self.sub_duration:
            self.subdivision()
        if elapsed >= self.duration:
            self.pulse(counters.sprites()[1].num, counters.sprites()[2].num)
        if self.AV:
            self.AV_update()
        
        

timer = Timer()

class SoundChanger(pygame.sprite.Sprite):
    def __init__(self, pos: tuple, assocRhythm: object):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('images/soundChangeWheel.png').convert_alpha()
        self.rect = self.image.get_rect(center = pos)
        self.assocRhythm = assocRhythm
        self.deathWish = 0
    
    def octant_check(self, pos):
        print('octant check')
        radius = ((pos[0] - self.rect.centerx)**2 + (pos[1] - self.rect.centery)**2)**(1/2)
        if radius < 81:
            LR: int = pos[0] < self.rect.centerx   #left true, right false
            UD: int = pos[1] > self.rect.centery   #down true, up false
            # y-hug false, x-hug true
            hug: int = (pos[0]-self.rect.centerx)**2 > (pos[1]-self.rect.centery)**2   
            print('LR: {0}, UD: {1}, hug: {2}'.format(LR, UD, hug))
            octant = 4*LR + 2*UD + hug
            self.assocRhythm.soundChange(octant)
soundChanger = pygame.sprite.GroupSingle()

### global functions -----------------------------------------
def top_menu_init():
    top_menu_data = [(' Rhythm Trainer ', (disp_width/2), ('home', 0)), 
                     (' Sandbox ', (disp_width/10), ('home', 1)),
                     (' Practice ', (disp_width/4), ('home', 2)),
                     (' Guide ', (3*disp_width/4), ('home', 3)),
                     (' Settings ', (9*disp_width/10), ('home', 4))]
    
    for x in top_menu_data:
        homeButtons.add(Button(x[0], x[1], x[2]))

    pygame.draw.line(workingDisplay, BLACK, (0,70), (disp_width, 70))

def update_rhythms(ctState, rhythmPage) -> None:
    for x in rhythms:
        x.kill()      
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
    for x in rhythms.sprites():
        sprites.add(x)

def update_all() -> None:
    Display.blit(workingDisplay, (0,0))
    try:
        update_rhythms(ctState, counters.sprites()[0].num)
    except IndexError: pass
    sprites.update()
    sprites.draw(Display)

def sprites_clicked(mouse_pos: tuple, mouse_buttons: tuple) -> None:
    try:
        # handle sprite-click functions
        for x in range(0, len(sprites.sprites())):
            spr = sprites.sprites()
            if spr[x].rect.collidepoint(mouse_pos):
                Display.blit(workingDisplay,(0,0))
                if spr[x] in buttons:
                    spr[x].click()
                elif spr[x] in playbackButtons:
                    spr[x].click()
                elif spr[x] in homeButtons:
                    spr[x].click()
                elif spr[x] in soundChanger:
                    spr[x].octant_check(mouse_pos)
                elif spr[x] in rhythms:
                    pygame.mouse.get_rel()
                    new_rhythm = ActiveRhythm(spr[x].binary, (mouse_pos))
                    activeRhythms.add(new_rhythm)
                    pickedUpRhythm.add(new_rhythm)
                    sprites.add(new_rhythm)
                elif spr[x] in activeRhythms:
                    if mouse_buttons[0] == True:
                        pygame.mouse.get_rel()
                        pickedUpRhythm.add(spr[x])
                    elif mouse_buttons[2] == True:
                        wheel = SoundChanger(mouse_pos, spr[x])
                        soundChanger.add(wheel)
                        sprites.add(wheel)
                elif spr[x] in draggers:
                    pygame.mouse.get_rel()
                    clickedDragger.add(spr[x])
                elif spr[x] in kernels:
                    pygame.mouse.get_rel()
                    clickedKernel.add(spr[x])
       
        # leave soundChanger up for 1 grace click before killing
        if len(soundChanger.sprites()):
            if soundChanger.sprite.deathWish == 0:
                soundChanger.sprite.deathWish += 1
            elif soundChanger.sprite.deathWish == 1:
                soundChanger.sprite.kill()
    except IndexError: pass
    update_all()            
    
def sandbox_init() -> None:
    global mode
    mode = 'sandbox'

    # toolkit/workspace  background/text/lines  onto workingDisplay
    toolkit_surf = pygame.Surface((disp_width/3,Display.get_height()-71))
    toolkit_surf.fill((60,60,60))
    toolkit_rect = toolkit_surf.get_rect(topleft = (0,70))
    workingDisplay.blit(toolkit_surf, toolkit_rect)
    toolkit_text = headerFont.render(' Toolkit ', True, ORANGE)
    toolkit_text_rect = toolkit_text.get_rect(center = (disp_width/6,86))
    workingDisplay.blit(toolkit_text,toolkit_text_rect)
    workspace_surf = pygame.Surface((disp_width*2/3-2,disp_height-71))
    workspace_surf.fill((220,220,220))
    workspace_rect = workspace_surf.get_rect(topleft = (disp_width/3+2,70))
    workingDisplay.blit(workspace_surf, workspace_rect)
    workspace_text = headerFont.render(' Workspace ',True, WORKSPACEPURPLE, (200,200,200))
    workspace_rect = workspace_text.get_rect(center = (8*disp_width/11+1,85))
    workingDisplay.blit(workspace_text,workspace_rect)
    pygame.draw.line(workingDisplay, BLACK, (disp_width/3,70),
                     (disp_width/3,disp_height),2)
    pygame.draw.line(workingDisplay, BLACK, (0,100), (disp_width,100))

    sb_text_rect = homeButtons.sprites()[1].rect
    pygame.draw.ellipse(workingDisplay,(50,150,50),
                        (sb_text_rect.left-5, sb_text_rect.top-5, 
                         sb_text_rect.width+10, sb_text_rect.height+10))
    
    # draw lines in workspace 
    # (spaced by 22 pixels (rhydotlen) in x, 43 (rhy height) in y)
    line_x = disp_width / 3 + 1
    line_y = 100
    while line_y < disp_height:
        pygame.draw.line(workingDisplay, BLACK, (disp_width / 3, line_y),
                         (disp_width,line_y))
        line_y += 44
    pygame.draw.rect(workingDisplay, BLACK, ((disp_width / 3, line_y - 44) ,
                                             (disp_width * 2 / 3, disp_height - (line_y - 44))))
    while line_x < disp_width:
        pygame.draw.line(workingDisplay, BLACK, (line_x, 100), 
                         (line_x, disp_height))
        line_x += 22
    pygame.draw.rect(workingDisplay, BLACK, ((line_x-22,100), 
                                             (disp_width-(line_x-23), disp_height-100)))

    # sandboxBackdrop.blit(workingDisplay, (0,0))
    
    # toolkit population
    buttons.add(Button(['images/up_button_unpressed.png', 'images/up_button_pressed.png'],
                                   (disp_width/3-100,75), ('UpDown', 0)))
    buttons.add(Button(['images/down_button_unpressed.png', 'images/down_button_pressed.png'],
                                   (disp_width/3-50,75), ('UpDown', 1)))
    buttons.add(Button(['images/core_button_unpressed.png', 'images/core_button_pressed.png'],
                        (40,75), ('CT', 0)))
    buttons.add(Button(['images/trivial_button_unpressed.png', 'images/trivial_button_pressed.png'],
                        (84,75), ('CT', 1)))
    counters.add(Counter((disp_width/3-74, 76), 1))
    
    # workspace population
    metronome_x = disp_width/3 + 55
    buttons.add(Button(['images/on_button.png', 'images/off_button.png'],
                       (metronome_x - 30, 72), ('onOff', 4)))
    bpm_text = miniFont.render('Metronome (bpm):', True, WORKSPACEPURPLE)
    bpm_text_rect = bpm_text.get_rect(midleft = (metronome_x, 86))
    counters.add(Counter((metronome_x + bpm_text_rect.width + 5, 74), 60))
    draggers.add(Dragger((metronome_x + bpm_text_rect.width + 41, 73), 'metronome'))
    subdiv_x = disp_width/2 + 70
    buttons.add(Button(['images/on_button.png', 'images/off_button.png'],
                       (subdiv_x - 30, 72), ('onOff', 5)))
    subdiv_text = miniFont.render('Subdivision:', True, WORKSPACEPURPLE)
    subdiv_text_rect = subdiv_text.get_rect(midleft = (subdiv_x, 86))
    counters.add(Counter((subdiv_x + subdiv_text_rect.width + 5, 74), 1))
    draggers.add(Dragger((subdiv_x + subdiv_text_rect.width + 30, 73), 'subdivision'))
    workingDisplay.blit(bpm_text, bpm_text_rect)
    workingDisplay.blit(subdiv_text, subdiv_text_rect)

    playbackButtons.add(Button(['images/play_button_unpressed.png', 'images/play_button_pressed.png'],
                       (disp_width - 220, 72), ('playback', 0)))
    playbackButtons.add(Button(['images/pause_button_unpressed.png', 'images/pause_button_pressed.png'],
                       (disp_width - 190, 72), ('playback', 1)))
    playbackButtons.add(Button(['images/stop_button_unpressed.png', 'images/stop_button_pressed.png'],
                       (disp_width - 160, 72), ('playback', 2)))
    
    kernels.add(Kernel(x) for x in ['left', 'right'])

    highlighter.add(Highlighter())

    Display.blit(workingDisplay,(0,0))
    
    spritify()
    update_all()

def spritify() -> None:
    classes = [homeButtons, buttons, counters, rhythms, highlighter, activeRhythms, draggers, kernels, playbackButtons]
    for x in classes:
        for j in range(0, len(x.sprites())):
            sprites.add(x.sprites()[j])

### init display ---------------------------------------------
top_menu_init()
Display.blit(workingDisplay,(0,0))
spritify()
update_all()
pygame.display.update()

### game loop ------------------------------------------------
while True:

    if timer:
        if timer.active:
            timer.update()

    # picking up rhythms
    if len(pickedUpRhythm.sprites()):
        rel = pygame.mouse.get_rel()
        if rel[0]+rel[1]:
            pickedUpRhythm.sprite.move(rel)
        update_needed = True

    # dragging draggers
    if len(clickedDragger.sprites()):
        rel = pygame.mouse.get_rel()
        if rel[1] < 0:
            clickedDragger.update('up')
        if rel[1] > 0:
            clickedDragger.update('down')
        update_needed = True

    # moving kernels
    if len(clickedKernel.sprites()):
        rel = pygame.mouse.get_rel()
        clickedKernel.sprite.move(rel[0])
        update_needed = True


    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # if event.type == KEYDOWN:
        #     if event.key == 32:
        #         if playing == True:
        #             playing = 'paused'
        #         else:
        #             playing = True

        if event.type == MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            mouse_buttons = pygame.mouse.get_pressed()
            # checking if present class instances were clicked
            sprites_clicked(mouse_pos, mouse_buttons)
            

        if event.type == MOUSEBUTTONUP:
            # unclicking buttons
            if upDownClick:
                buttons.sprites()[lastUpDownClicked].click()
                update_needed = True
            if playbackClick:
                playbackButtons.sprites()[lastPlaybackClicked].click()
                playbackClick = False
                update_needed = True

            # dropping rhythms
            if len(pickedUpRhythm.sprites()):
                Display.blit(workingDisplay,(0,0))
                pur = pickedUpRhythm.sprite
                killed = False
                if pur.rect.left < disp_width/3 or pur.rect.top < 100 or pur.rect.centery > disp_height - 2*rhyDotLen or pur.rect.right > disp_width + 2:
                    pur.kill()
                    killed = True
                elif pur.move_bool == False:
                    pur.permutate()
                else:
                    pur.move_bool = False
                    pur.snap()    
                # check collision with other active rhythms
                pur.remove(activeRhythms)
                for x in range(0, len(activeRhythms.sprites())):
                    if activeRhythms.sprites()[x].rect.colliderect(pur.rect):
                        pur.kill()
                        killed = True
                if killed == False:
                    pur.add(activeRhythms)
                pickedUpRhythm.empty()
                update_needed = True
            
            # dropping dragger
            if len(clickedDragger.sprites()):
                Display.blit(workingDisplay, (0,0))
                clickedDragger.empty()
                update_needed = True

            # dropping kernel
            if len(clickedKernel.sprites()):
                clickedKernel.sprite.snap()
                clickedKernel.empty()
                update_needed = True

    if update_needed:
        update_all()
        update_needed = False
    pygame.display.update()