#!/usr/bin/env python3
import pygame, sys
from pygame.locals import *
from matrixGen3 import data, cores, trivials
import time

### display init ---------------------------------------------
pygame.init()
disp_width = 1300
disp_height = 800
Display = pygame.display.set_mode((disp_width, disp_height),0,32)
pygame.display.set_caption('The Rhythm Trainer')
workingDisplay = pygame.Surface((disp_width,disp_height), SRCALPHA)
workingDisplay.fill((120,130,130))
sandboxBackdrop = pygame.Surface((disp_width,disp_height), SRCALPHA)
pygame.mixer.set_num_channels(14)

### vars init ------------------------------------------------
mode = 0
rhyDotLen = 22
rhythmIterator = 0
subdivHighlighter = 0
ghostIterator = [0]
lastUpDownClicked = 0
lastPlaybackClicked = 0
ctState = 0
coresAndTrivials = [cores,trivials]
metronomeSound = pygame.mixer.Sound('sounds/metronome.wav')
update_needed = False
playbackClick = False
upDownClick = False  #up/core = 0, down/trivial = 1
updateNeeded = False
playback_keyed = False

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
tinyFont = pygame.font.SysFont('Serif', 10)

### init for sound change wheel -------------------------------
colors = [(236,146,48), (237,35,51), (207,102,205), (233,60,160),
          (233,209,67), (144, 208, 68), (96,99,205), (109, 157, 205), WHITE]
text = ['Snare', 'Kick', 'Ride', 'Hihat', 'Clave', 'Cowbell', 'Shaker', 'Snap', 'Metronome']
sounds = [pygame.mixer.Sound(x) for x in ('sounds/snare.wav','sounds/kick.wav',
                                          'sounds/ride.wav','sounds/hihat.wav',
                                          'sounds/clave.wav', 'sounds/cowbell.wav',
                                          'sounds/shaker.wav', 'sounds/snap.wav')]

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
            if self.type == 'clear':
                self.status = 0
            self.image = pygame.image.load(self.graphics[self.status]).convert_alpha()
            self.rect = self.image.get_rect(topleft = pos)
        if type == 'mixer':
            self.mixing = False
        
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
                global lastPlaybackClicked
                self.status = 1
                lastPlaybackClicked = self.type[1]
            else:
                self.status = 0

            # click play button -> play
            global timer
            if self.type[1] == 0 and timer.active == False and cursor.sprite is None:
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
                if mode != 'sandbox':
                    sandbox_init()
            elif self.type[1] == 2:
                print('practice screen')
            elif self.type[1] == 3:
                print('guide screen')
            elif self.type[1] == 4:
                print('settings screen')

        elif self.type == 'mixer':
            if self.mixing == False:
                mixables = []
                W = DropdownBox(8)
                sprites.add(W)
                sprites.add(W.slider)
                dropdownBoxes.add(W)
                for x in activeRhythms:
                    if x.decoupled:
                        for sound in x.decoupled_sounds:
                            if sound not in mixables:
                                mixables.append(sound)
                                W = DropdownBox(sound)
                                sprites.add(W)
                                sprites.add(W.slider)
                                dropdownBoxes.add(W)
                    elif not x.decoupled:
                        if x.sound not in mixables:
                            mixables.append(x.sound)
                            W = DropdownBox(x.sound)
                            sprites.add(W)
                            sprites.add(W.slider)
                            dropdownBoxes.add(W)
                self.mixing = True
            else:
                for x in (dropdownBoxes.sprites(), sliders.sprites()):
                    for y in x:
                        y.kill()
                self.mixing = False

        elif self.type == 'clear':
            if self.status == 0:
                for x in activeRhythms:
                    x.kill()
                activeRhythms.empty()
                buttons.sprites()[6].click()
                buttons.sprites()[6].click()
                self.status = 1
            else:
                self.status = 0
            self.image = pygame.image.load(self.graphics[self.status]).convert_alpha()
            
            
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
    def __init__(self, pos: tuple, type: str) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.type = type
        self.num = {'metronome': 60, 'subdivision': 4, 'toolboxPage': 1}[type]
        self.max = {'metronome': 300, 'subdivision': 12, 'toolboxPage': 5}[type]
        if self.type == 'toolboxPage' or self.type == 'subdivision':
            self.image = pygame.Surface((22, 22))
        elif self.type == 'metronome':
            self.image = pygame.Surface((34, 22))
        self.image.fill((255,255,255,255))
        self.rect = self.image.get_rect(topleft = pos)
        self.text = miniFont.render((str(self.num)), True, (0,0,0, 255))
        self.image.set_alpha(255)
        
    def update(self) -> None:
        self.text = miniFont.render((str(self.num)), True, (0,0,0, 255))
        self.image.fill((255,255,255,255))
        self.image.blit(self.text, (3,3))

    def validate(self) -> None:
        if self.num < 1:
            self.num = 1
        elif self.num > self.max:
            self.num = self.max
counters = pygame.sprite.Group()

class Cursor(pygame.sprite.Sprite):
    def __init__(self, attached_to: pygame.sprite.Sprite) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((2,17), pygame.SRCALPHA)
        self.image.fill((0,0,0,255))
        self.attached_to = attached_to
        self.x = self.attached_to.rect.left + 5 + self.attached_to.text.get_width()
        self.rect = self.image.get_rect(topleft = (self.x, self.attached_to.rect.top + 2))
        self.start_time = pygame.time.get_ticks()

    def type_number(self, key: int) -> None:
        key_str = str(key-48)
        self.attached_to.num = int(str(self.attached_to.num) + key_str)
        self.attached_to.update()

    def delete_number(self) -> None:
        try:
            self.attached_to.num = int((str(self.attached_to.num))[:-1])
        except ValueError:
            self.attached_to.num = 0
        self.attached_to.update()

    def blinky(self) -> None:
        if pygame.time.get_ticks() - self.start_time > 500:
            self.start_time = pygame.time.get_ticks()
            if self.image.get_alpha() == 255:
                self.image.set_alpha(0)
            else:
                self.image.set_alpha(255)
    
    def update(self) -> None:
        self.x = self.attached_to.rect.left + 5 + self.attached_to.text.get_width()
        self.rect = self.image.get_rect(topleft = (self.x, self.attached_to.rect.top + 2))
cursor = pygame.sprite.GroupSingle()

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
        self.sound = 0
        self.decoupled = False
        self.decoupled_sounds = []
        self.update_image()
        self.rect = self.image.get_rect(center = pos)
        self.grid_pos = (round((self.rect.left - (disp_width / 3)) / 22), 
                         round((self.rect.top - 100) / 44))
        self.move_bool = False
        self.relative_grid_pos = (0,0)
    
    def update_image(self) -> pygame.Surface:
        self.image = Rhythm.rhythm_surface(self.binary, color = self.sound)
        if not self.decoupled:    
            if self in selectedRhythms.sprites():
                pygame.draw.rect(self.image, (255,255,255), (0,0,self.image.get_width(), self.image.get_height()), 1)
        elif self.decoupled:
            w = len(self.binary) * rhyDotLen
            rhy_surf = pygame.Surface((w, 2*rhyDotLen-1))
            rhy_surf.fill(WHITE)
            sound_iterator = 0
            temp_color = colors[self.decoupled_sounds[sound_iterator]]
            if self in selectedRhythms.sprites():
                pygame.draw.rect(rhy_surf, (150,150,150), (0,0,self.image.get_width(), self.image.get_height()), 1)
            for j in range(0,len(self.binary)):
                if self.binary[j] == "1":
                    pygame.draw.circle(rhy_surf, temp_color, (rhyDotLen*j+11,11), 10)
                    sound_iterator += 1
                    try:
                        temp_color = colors[self.decoupled_sounds[sound_iterator]]
                    except IndexError: pass
                elif self.binary[j] == "0":
                    pygame.draw.circle(rhy_surf, BLACK, (rhyDotLen*j+11,32), 10, 2)
            self.image = rhy_surf

    def update(self) -> None:
        self.update_image() # whoops, can be cleaned up later

    def permutate(self) -> None:
        if soundChanger.sprite is None:    
            if not self.decoupled:
                self.binary = self.binary[1:]+self.binary[0]
                self.update_image()
            else:
                if self.binary[0] == "1":
                    self.decoupled_sounds = self.decoupled_sounds[1:] + [self.decoupled_sounds[0]]
                self.binary = self.binary[1:]+self.binary[0]
                self.update_image()

    def move(self, rel: tuple) -> None:
        self.rect = self.rect.move((rel[0], rel[1]))
        self.move_bool = True

    def soundChange(self, newSound: int) -> None:
        self.sound = newSound
        self.update_image()
        buttons.sprites()[6].click() # refresh mixer
        buttons.sprites()[6].click()

    def snap(self) -> None:
        pos = self.rect.topleft
        snap_by = (((pos[0] - int(disp_width / 3)) %22, 
                    (pos[1] - 100) % 44))
        self.rect = self.rect.move((-snap_by[0]+2, -snap_by[1]+1))
        self.grid_pos = (round((self.rect.left - (disp_width / 3)) / 22) , 
                         round((self.rect.top - 100) / 44))

    def decouple(self) -> None:
        """
        Turn active rhythm into a rhythm with decoupled sound
        This allows you to have multiple sounds for one rhythm pattern
        Instead of permutating multiple disparate rhythms
        Once decoupled, the individual dots can be soundchanged separately
        """
        w = 0
        rhy_surf = pygame.Surface((w, 2*rhyDotLen-1))
        rhy_surf.fill(WHITE)
        if not self.decoupled_sounds:
            for j in range(0,len(self.binary)):
                if self.binary[j] == "1":
                    self.decoupled_sounds.append(self.sound)
        self.decoupled = True
        self.update_image()
        buttons.sprites()[6].click() # refresh mixer
        buttons.sprites()[6].click()
    
    def recouple(self) -> None:
        self.decoupled = False
        self.update_image()
        buttons.sprites()[6].click() # refresh mixer
        buttons.sprites()[6].click()
activeRhythms = pygame.sprite.Group()
pickedUpRhythm = pygame.sprite.GroupSingle()
selectedRhythms = pygame.sprite.Group()
clipboardRhythms = pygame.sprite.Group()

class Dragger(pygame.sprite.Sprite):
    def __init__(self,  pos: tuple, type: str) -> None:
        pygame.sprite.Sprite.__init__(self)
        graphics = ['images/dragger_0.png', 'images/dragger_1.png']
        self.graphics = [pygame.image.load(x).convert() for x in graphics]
        self.status = 0
        self.image = self.graphics[0]
        self.type = type
        for x in counters.sprites():
            if x.type == type:
                self.attached_to = x
        self.pos = pos
        self.rect = self.image.get_rect(topleft = pos)

    def animate(self) -> None:
        if self.status == 0: 
            self.status = 1
        else: 
            self.status = 0
        self.image = self.graphics[self.status]

    def update(self, dir_dragged: str = 'none') -> None:
        if dir_dragged == 'up' and self.attached_to.num < self.attached_to.max:
            self.attached_to.num += 1
        elif dir_dragged == 'down' and self.attached_to.num > 1:
            self.attached_to.num -= 1
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
            self.rect.move_ip(-snap_by - 3,0)
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
        self.sounds.append(metronomeSound)

    def dechameleon(self):
        self.image.fill((200, 200, 0))

    # if colliding with active rhythm, play any beats hovering on
    def rhythm_collisions(self):
        if buttons.sprites()[5].status == 0:
            for x in activeRhythms.sprites():
                if self.rect.colliderect(x.rect):
                    if not x.decoupled:
                        highlighted_pos = self.grid_pos - x.grid_pos[0]
                        try:
                            if x.binary[highlighted_pos] == '1':
                                self.sounds.append(x.sound)
                        except IndexError: pass
                    elif x.decoupled:
                        highlighted_pos = self.grid_pos - x.grid_pos[0]
                        try:
                            if x.binary[highlighted_pos] == '1':
                                hit_number = -1
                                for j in range(0, highlighted_pos + 1):
                                    if x.binary[j] == "1":
                                        hit_number += 1
                                self.sounds.append(x.decoupled_sounds[hit_number])
                        except IndexError: pass

    def play_sounds(self):
        if self.sounds:
            for x in self.sounds:
                if x == metronomeSound:
                    pygame.mixer.Channel(8).play(x)
                else:
                    pygame.mixer.Channel(x).stop
                    pygame.mixer.Channel(x).play(sounds[x])
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
            self.start_time = time.time() * 1000
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
        current_time = time.time() * 1000
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
        self.clicked_pos = pos
        self.image = pygame.image.load('images/soundChangeWheel.png').convert_alpha()
        self.rect = self.image.get_rect(center = pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.assocRhythm = assocRhythm
        self.deathWish = 0
    
    def octant_check(self, pos):
        radius = ((pos[0] - self.rect.centerx)**2 + (pos[1] - self.rect.centery)**2)**(1/2)
        if radius < 81 and radius > 14:
            LR: int = pos[0] < self.rect.centerx   #left true, right false
            UD: int = pos[1] > self.rect.centery   #down true, up false
            # y-hug false, x-hug true
            hug: int = (pos[0]-self.rect.centerx)**2 > (pos[1]-self.rect.centery)**2   
            octant = 4*LR + 2*UD + hug

            if self.assocRhythm.decoupled:
                highlighted_dot = (self.rect.centerx - self.assocRhythm.rect.left) // 22
                if self.assocRhythm.binary[highlighted_dot] == "1":
                    hit_number = -1
                    for x in range(0, highlighted_dot + 1):
                       if self.assocRhythm.binary[x] == "1":
                            hit_number += 1
                    self.assocRhythm.decoupled_sounds[hit_number] = octant
                    self.assocRhythm.update_image()
                
            else:
                if self.assocRhythm in selectedRhythms:
                    for x in selectedRhythms.sprites():
                        x.soundChange(octant)
                else:
                    self.assocRhythm.soundChange(octant)

        elif radius <= 14:
            if self.assocRhythm in selectedRhythms:
                i = 0
                for x in selectedRhythms.sprites():
                    if not x.decoupled:
                        i += 1
                if i == len(selectedRhythms.sprites()):
                    for x in selectedRhythms.sprites():
                        x.decouple()
                elif i == 0:
                    for x in selectedRhythms.sprites():
                        x.recouple()

            elif not self.assocRhythm.decoupled:
                self.assocRhythm.decouple()
            else:
                self.assocRhythm.recouple()
        self.kill()
soundChanger = pygame.sprite.GroupSingle()

class DropdownBox(pygame.sprite.Sprite):
    def __init__(self, sound: int):
        pygame.sprite.Sprite.__init__(self)
        self.sound = sound
        self.image_and_rect()
        self.slider = Slider(sound, self.rect.centery)
        sliders.add(self.slider)

    def image_and_rect(self):
        self.positioning()
        self.image = pygame.Surface((205, 43))
        self.image.fill(colors[self.sound])
        pygame.draw.rect(self.image, (0,0,0), (0,0,205,43), 1)
        a = miniFont.render(text[self.sound], 1, BLACK)
        self.image.blit(a, (4,18))
        if self.sound == 8:
            pygame.draw.rect(self.image, (240,240,240), (88,21,100,4))
        else:
            pygame.draw.rect(self.image, (240,240,240), (60,21,100,4))
        self.rect = self.image.get_rect(topright = (disp_width, self.y_pos))

    def positioning(self):
        self.y_pos = 101 + 44 * len(dropdownBoxes.sprites()) 
dropdownBoxes = pygame.sprite.Group()

class Slider(pygame.sprite.Sprite):
    def __init__(self, sound, y_pos):
        pygame.sprite.Sprite.__init__(self)
        self.sound = sound
        self.y_pos = y_pos
        self.value = int(pygame.mixer.Channel(self.sound).get_volume() * 100)
        self.image_and_rect()
        
    def image_and_rect(self):    
        self.image = pygame.Surface((18,18))
        pygame.draw.rect(self.image, (250,250,250), (0,0,18,18))
        pygame.draw.rect(self.image, (170,170,170), (0,0,18,18), width = 2)
        if self.sound < 8:
            self.rect = self.image.get_rect(center = (disp_width - 145 + self.value, self.y_pos))
        else:
            self.rect = self.image.get_rect(center = (disp_width - 117 + self.value, self.y_pos))
        self.text_update()

    def text_update(self):
        pygame.draw.rect(self.image, (250,250,250), (0,0,18,18))
        pygame.draw.rect(self.image, (170,170,170), (0,0,18,18), width = 2)
        self.text = str(self.value)
        if len(self.text) < 3:
            self.image.blit(tinyFont.render(self.text, 1, BLACK),(4,4))
        else:
            self.image.blit(tinyFont.render(self.text, 1, BLACK),(1,4))

    def move(self, rel):
        if self.value + rel > 100:
            self.value = 100
        elif self.value + rel < 0:
            self.value = 0
        else:
            self.rect.move_ip(rel, 0)
            self.value += rel
        pygame.mixer.Channel(self.sound).set_volume(self.value / 100)
        self.text_update()
sliders = pygame.sprite.Group()
clickedSlider = pygame.sprite.GroupSingle()

class SelectionBox(pygame.sprite.Sprite):
    def __init__(self, start_pos: tuple, end_pos: tuple):
        pygame.sprite.Sprite.__init__(self)
        self.start_pos = start_pos
        width = abs(start_pos[0] - end_pos[0])
        height = abs(start_pos[1] - end_pos[1])
        self.image = pygame.Surface((width, height), SRCALPHA)
        self.image.fill((230,230,230,0.1))
        pygame.draw.rect(self.image, (100,100,255,100), (0,0,width,height))
        pygame.draw.rect(self.image, (0,0,255,250), (0,0,width,height), 2)
        self.rect = self.image.get_rect(topleft = (self.start_pos[0], self.start_pos[1]))
    
    def clean_mouse_pos(self, mouse_pos: tuple) -> tuple:
        if mouse_pos_in_workspace():
            return mouse_pos
        else:
            x = min(max(mouse_pos[0], disp_width/3 + 2), disp_width - 2)
            y = min(max(mouse_pos[1], 100 + 1), disp_height - 2)
            return (x,y)

    def expand(self, new_end_pos: tuple) -> None:
        new_end_pos = self.clean_mouse_pos(new_end_pos)
        left = min(self.start_pos[0], new_end_pos[0])
        top = min(self.start_pos[1], new_end_pos[1])
        width = abs(self.start_pos[0] - new_end_pos[0])
        height = abs(self.start_pos[1] - new_end_pos[1])
        self.image = pygame.Surface((width, height), SRCALPHA)
        self.image.fill((230,230,230,0.1))
        pygame.draw.rect(self.image, (100,100,255,100), (0,0,width,height))
        pygame.draw.rect(self.image, (0,0,255,250), (0,0,width,height), 2)
        self.rect = self.image.get_rect(topleft = (left, top))

    def finalize(self) -> None:
        """
        On mouse release, check for collisions with active rhythms.
        Empty pickedUpRhythms group, update images of previously picked up rhythms.
        Add any colliding rhythms to pickedUpRhythms group and update their images.
        """
        selected_rhythms = pygame.sprite.Group()
        previously_selected = selectedRhythms.sprites()
        for x in selectedRhythms.sprites():
            x.relative_grid_pos = (0,0)
        selectedRhythms.empty()
        for x in activeRhythms.sprites():
            if self.rect.colliderect(x.rect):
                selected_rhythms.add(x)
        for x in selected_rhythms.sprites():
            selectedRhythms.add(x)
            x.update_image()
        for x in previously_selected:
            x.update_image()
        self.kill()
selectionBox = pygame.sprite.GroupSingle()

class ClipboardBox(pygame.sprite.Sprite):
    def __init__(self, pos: tuple, type: str):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((80, 25))
        self.image.fill((255,255,255))
        self.type = type
        self.rect = self.image.get_rect(topleft = pos)
        self.text = miniFont.render(self.type, True, (0,0,0))
        self.image.blit(self.text, (5,3))
        pygame.draw.rect(self.image, (0,0,0,2), (0,0,80,25), 1)
        self.clicked = False
        self.grace_clicked = False

    def click(self):
        self.image.fill((200,200,200))
        self.image.blit(self.text, (5,3))
        self.clicked = True

    def unclick(self):
        self.image.fill((255,255,255))
        self.image.blit(self.text, (5,3))
        self.clicked = False

    def finalize(self):
        if self.clicked:
            if self.type == 'copy':
                clipboardManager.copy()
            elif self.type == 'paste':
                clipboardManager.paste(copyBox.sprite.rect.topleft)
                print('pasted from clipboard')
            elif self.type == 'select all':
                clipboardManager.select_all()
            elif self.type == 'cut':
                clipboardManager.cut()
            for x in clipboardBoxes.sprites():
                x.kill()
clipboardBoxes = pygame.sprite.Group()
copyBox = pygame.sprite.GroupSingle()

class ClipboardManager:
    def __init__(self):
        pass

    def open_menu(self, mouse_pos: tuple):    
        clipboardBoxes.add(ClipboardBox((mouse_pos[0], mouse_pos[1] + 25*x), y)
                            for x, y in enumerate(['copy', 'paste', 'cut', 'select all']))
        for x in clipboardBoxes.sprites():
            sprites.add(x)
            if x.type == 'copy':
                copyBox.add(x)
        
    def copy(self):
        clipboardRhythms.empty()

        # prepare relative positions
        min_left_grid = 1000
        slave_top_grid = 1000
        for x in selectedRhythms.sprites():
            if x.grid_pos[0] < min_left_grid:
                min_left_grid = x.grid_pos[0]
                slave_top_grid = x.grid_pos[1]
            elif x.grid_pos[0] == min_left_grid:
                if x.grid_pos[1] < slave_top_grid:
                    slave_top_grid = x.grid_pos[1]
        for x in selectedRhythms.sprites():
            x.relative_grid_pos = (x.grid_pos[0] - min_left_grid, x.grid_pos[1] - slave_top_grid)

        # copy rhythms to clipboardRhythms
        for x in selectedRhythms.sprites():
            clip_rhy = ActiveRhythm(x.binary, (x.rect.center))
            clip_rhy.sound = x.sound
            clip_rhy.relative_grid_pos = x.relative_grid_pos
            if x.decoupled:
                clip_rhy.decoupled = True
                clip_rhy.decoupled_sounds = x.decoupled_sounds.copy()
                clip_rhy.update_image()
            clipboardRhythms.add(clip_rhy)

    def paste(self, pos: tuple):
        for x in clipboardRhythms.sprites():
            killed = False
            
            # create copy rhythm
            new_rhythm = ActiveRhythm(x.binary, (x.rect.center))
            new_rhythm.sound = x.sound
            new_rhythm.relative_grid_pos = x.relative_grid_pos
            if x.decoupled:
                new_rhythm.decoupled = True
                new_rhythm.decoupled_sounds = x.decoupled_sounds.copy()
                new_rhythm.update_image()

            # position according to mouse
            new_rhythm.rect.topleft = (pos[0] + new_rhythm.relative_grid_pos[0]*22,
                        pos[1] + new_rhythm.relative_grid_pos[1]*44)
            new_rhythm.snap()

            # determine if valid location
            if new_rhythm.rect.left < disp_width/3 or new_rhythm.rect.top < 100 or new_rhythm.rect.centery > disp_height - 2*rhyDotLen or new_rhythm.rect.right > disp_width + 2:
                new_rhythm.kill()
                killed = True
            for y in activeRhythms.sprites():
                if y.rect.colliderect(new_rhythm.rect):
                    new_rhythm.kill()
                    killed = True
            
            # add to activeRhythms if valid
            if not killed:
                activeRhythms.add(new_rhythm)
                selectedRhythms.add(new_rhythm)
                sprites.add(new_rhythm)
        buttons.sprites()[6].click()
        buttons.sprites()[6].click()

    def select_all(self):
        for x in activeRhythms.sprites():
            selectedRhythms.add(x)
            x.update_image()

    def cut(self):
        self.copy()
        for x in selectedRhythms.sprites():
            x.kill()
        selectedRhythms.empty()
clipboardManager = ClipboardManager()

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
    # handles sprite clicks
    try:
        unclicked = 0
        if cursor.sprites():
            cursor.sprite.attached_to.validate()
            cursor.sprite.kill()
        for x in range(0, len(sprites.sprites())):
            spr = sprites.sprites()
            if spr[x].rect.collidepoint(mouse_pos):
                Display.blit(workingDisplay,(0,0))
                if spr[x] in buttons:
                    spr[x].click()
                elif spr[x] in playbackButtons:
                    global playbackClick
                    playbackClick = True
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
                    if soundChanger.sprites():
                        if soundChanger.sprite.rect.collidepoint(mouse_pos):
                            soundChanger.sprite.octant_check(mouse_pos)
                        else:
                            if mouse_buttons[0] == True:
                                pygame.mouse.get_rel()
                                pickedUpRhythm.add(spr[x])
                            elif mouse_buttons[2] == True:
                                wheel = SoundChanger(mouse_pos, spr[x])
                                soundChanger.add(wheel)
                                sprites.add(wheel)
                    else:
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
                elif spr[x] in sliders:
                    pygame.mouse.get_rel()
                    clickedSlider.add(spr[x])
                elif spr[x] in clipboardBoxes:
                    spr[x].click()
                elif spr[x] in counters:
                    timer.deactivate()
                    newCursor = Cursor(spr[x])
                    cursor.add(newCursor)
                    sprites.add(newCursor)
            else:
                unclicked += 1
            
            # start selection box if not clicking on any sprite
            if mode == "sandbox" and mouse_pos_in_workspace() and unclicked == len(sprites.sprites()):
                if mouse_buttons[2] == True:
                    clipboardManager.open_menu(mouse_pos)
                else:
                    if soundChanger.sprites():
                        soundChanger.sprite.octant_check(mouse_pos)
                    else:
                        newSelectionBox = SelectionBox(mouse_pos, mouse_pos)
                        selectionBox.add(newSelectionBox)
                        sprites.add(newSelectionBox)
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
    toolkit_text = headerFont.render(' Toolkit ', True, ORANGE, (45,45,45))
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
    counters.add(Counter((disp_width/3-74, 76), 'toolboxPage'))
    
    # workspace population
    metronome_x = disp_width/3 + 55
    buttons.add(Button(['images/on_button.png', 'images/off_button.png'],
                       (metronome_x - 30, 72), ('onOff', 4)))
    bpm_text = miniFont.render('Metronome (bpm):', True, WORKSPACEPURPLE)
    bpm_text_rect = bpm_text.get_rect(midleft = (metronome_x, 86))
    counters.add(Counter((metronome_x + bpm_text_rect.width + 5, 74), 'metronome'))
    draggers.add(Dragger((metronome_x + bpm_text_rect.width + 41, 73), 'metronome'))
    subdiv_x = disp_width/2 + 70
    buttons.add(Button(['images/on_button.png', 'images/off_button.png'],
                       (subdiv_x - 30, 72), ('onOff', 5)))
    subdiv_text = miniFont.render('Subdivision:', True, WORKSPACEPURPLE)
    subdiv_text_rect = subdiv_text.get_rect(midleft = (subdiv_x, 86))
    counters.add(Counter((subdiv_x + subdiv_text_rect.width + 5, 74), 'subdivision'))
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

    buttons.add(Button(['images/mixer_button_unpressed.png', 'images/mixer_button_pressed.png',],
                       (disp_width-100,72),('mixer')))
    buttons.add(Button(['images/clear_button_unpressed.png', 'images/clear_button_pressed.png'],
                       (disp_width-34,72),('clear')))
    Display.blit(workingDisplay,(0,0))
    
    spritify()
    update_all()

def spritify() -> None:
    classes = [homeButtons, buttons, counters, rhythms, highlighter, activeRhythms, draggers, kernels, playbackButtons]
    for x in classes:
        for j in range(0, len(x.sprites())):
            sprites.add(x.sprites()[j])

def mouse_pos_in_workspace() -> bool:
    mouse_pos = pygame.mouse.get_pos()
    if mouse_pos[0] > disp_width/3 and mouse_pos[1] > 100:
        return True
    else:
        return False

### init display ---------------------------------------------
top_menu_init()
Display.blit(workingDisplay,(0,0))
spritify()
update_all()
pygame.display.update()

### game loop ------------------------------------------------
while True:
   
    # update timer if it's active
    if timer:
        if timer.active:
            timer.update()
    # picking up rhythms
    if len(pickedUpRhythm.sprites()):
        rel = pygame.mouse.get_rel()
        if rel[0]+rel[1]:
            if pickedUpRhythm.sprite in selectedRhythms:
                for x in selectedRhythms.sprites():
                    x.move(rel)
            else:
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
    # sliding sliders
    if len(clickedSlider.sprites()):
        rel = pygame.mouse.get_rel()
        clickedSlider.sprite.move(rel[0])
        update_needed = True
    # cursor blink
    if len(cursor.sprites()):
        cursor.sprite.blinky()
        update_needed = True

    for event in pygame.event.get():
        if cursor.sprites():
            if event.type == KEYDOWN:
                num_keys = [K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]
                if event.key in num_keys:
                    cursor.sprite.type_number(event.key)
                    update_needed = True
                if event.key == K_BACKSPACE or event.key == K_DELETE:
                    cursor.sprite.delete_number()
                    update_needed = True
                if event.key == K_RETURN or event.key == K_KP_ENTER:
                    cursor.sprite.attached_to.validate()
                    cursor.sprite.kill()
                    update_needed = True

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == KEYDOWN:
            if mode == 'sandbox':
                if event.key == K_SPACE: # play/pause toggle
                    if timer.active:
                        playbackButtons.sprites()[1].click()
                    else:
                        playbackButtons.sprites()[0].click()
                    playback_keyed = True
                    update_needed = True

                if event.key == K_b: # stop
                    playbackButtons.sprites()[2].click()
                    playback_keyed = True
                    update_needed = True

                if event.key == K_DELETE or event.key == K_BACKSPACE: # delete selected rhythms
                    for x in selectedRhythms.sprites():
                        x.kill()
                    buttons.sprites()[6].click()
                    buttons.sprites()[6].click()
                    update_needed = True
                
                if event.key == K_c: # copy selected rhythms (ctrl + c)
                    if pygame.key.get_mods() & KMOD_CTRL:
                        clipboardManager.copy()
                        update_needed = True
                
                if event.key == K_v: # paste copied rhythms (ctrl + v)
                    if pygame.key.get_mods() & KMOD_CTRL:
                        clipboardManager.paste(pygame.mouse.get_pos())
                        update_needed = True

                if event.key == K_a: # select all rhythms (ctrl + a)
                    if pygame.key.get_mods() & KMOD_CTRL:
                        clipboardManager.select_all()
                        update_needed = True

                if event.key == K_x: # cut selected rhythms (ctrl + x)
                    if pygame.key.get_mods() & KMOD_CTRL:   
                        clipboardManager.cut()
                        update_needed = True

        if event.type == KEYUP:
            if mode == 'sandbox':
                if event.key == K_SPACE or event.key == K_b:
                    if playback_keyed == True:
                        playbackButtons.sprites()[lastPlaybackClicked].click()
                        playback_keyed = False
                        update_needed = True

        if event.type == MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            mouse_buttons = pygame.mouse.get_pressed()
            # checking if present class instances were clicked
            sprites_clicked(mouse_pos, mouse_buttons)

        if event.type == MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            # updating selection box
            if len(selectionBox.sprites()) > 0:
                selectionBox.sprites()[0].expand(mouse_pos)
                update_needed = True

        if event.type == MOUSEBUTTONUP:
            # unclicking buttons
            if upDownClick:
                buttons.sprites()[lastUpDownClicked].click()
                update_needed = True
            if playbackClick:
                playbackButtons.sprites()[lastPlaybackClicked].click()
                playbackClick = False
                update_needed = True
            try:
                # clear button
                if buttons.sprites()[7].status == 1: 
                    buttons.sprites()[7].click()
                    update_needed = True
            except IndexError: pass

            # finalizing selection box
            if len(selectionBox.sprites()) > 0:
                selectionBox.sprites()[0].finalize()
                update_needed = True
            
            # finalizing clipboard boxes
            if len(clipboardBoxes.sprites()) > 0:
                for x in clipboardBoxes.sprites():
                    if x.rect.collidepoint(mouse_pos):
                        x.finalize()
                for x in clipboardBoxes.sprites():
                    if x.grace_clicked == False:
                        x.grace_clicked = True
                    else:
                        x.kill()
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
                    if pur not in selectedRhythms:
                        pur.permutate()
                    else:
                        for x in selectedRhythms.sprites():
                            x.permutate()
                else:
                    pur.move_bool = False
                    if pur in selectedRhythms:
                        selectedRhythms.remove(pur)
                        activeRhythms.remove(pur)
                        for x in selectedRhythms.sprites():
                            activeRhythms.remove(x)
                        for x in selectedRhythms.sprites():
                            x.snap()
                            if x.rect.left < disp_width/3 or x.rect.top < 100 or x.rect.centery > disp_height - 2*rhyDotLen or x.rect.right > disp_width + 2:
                                x.kill()
                            for y in activeRhythms.sprites():
                                if x.rect.colliderect(y.rect):
                                    x.kill()
                        for x in selectedRhythms.sprites():
                            activeRhythms.add(x)
                        selectedRhythms.add(pur)
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
                buttons.sprites()[6].click()
                buttons.sprites()[6].click()
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
            
            # dropping slider
            if len(clickedSlider.sprites()):
                clickedSlider.empty()
                update_needed = True
    
    if update_needed:
        update_all()
        update_needed = False
    pygame.display.update()