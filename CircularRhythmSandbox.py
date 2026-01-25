#!/usr/bin/env python3

### INIT ###--------------------------------------------------------------
import pygame
import math
import time
from sys import exit
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Circular Rhythm Sandbox")
screen.fill((20, 20, 20))

last_time = time.time()

### CLASSES ###--------------------------------------------------------------
class Manager:
    def __init__(self):
        self.circle = circle.sprites()[0]
        self.bpm = 60
        self.subdivisions = 4
        self.running = False

    def angle_per_time(self, elapsed_time):
        angle = (2*math.pi) / (60 / self.bpm) * elapsed_time
        print(angle)
        return angle

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def update(self):
        self.circle.advance(self.angle_per_time(dt))
        # self.sine_wave.update_waveform()
    
class Circle(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, color):
        super().__init__()
        self.x = x
        self.y = y
        self.radians_colored = 0
        self.radius = radius
        self.color = color
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius, 4)
        self.rect = self.image.get_rect(center=(x, y))

    def advance(self, angle):
        self.radians_colored += angle
        if self.radians_colored >= 2 * math.pi:
            self.radians_colored -= 2 * math.pi
            print("Circle completed a full rotation.")
            self.image.fill((0,0,0,0))
            pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius, 4)

        # Update visual representation here if needed
        pygame.draw.arc(self.image, (0,200,200), (0.1*self.radius, 0.1*self.radius, (0.9*self.radius)*2, (0.9*self.radius)*2), self.radians_colored, angle, 5)
        self.rect = self.image.get_rect(center=(self.x, self.y))

class CircleNode(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, color):
        super().__init__()
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 0, 0), (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))

class SineWave(pygame.sprite.Sprite):
    def __init__(self, x, y, width, antinodes, color):
        super().__init__()
        self.height = 100/antinodes
        self.image = pygame.Surface((width, antinodes))
        self.image.fill(color)
        self.rect = self.image.get_rect(midleft=(x, y))

    def update_waveform(self):
        
        pass  # Waveform update logic to be implemented
        
### GROUPS AND INSTANCES ###-----------------------------------------------------
circle = pygame.sprite.GroupSingle()
sine_waves = pygame.sprite.Group()

### GLOBAL FUNCTIONS ###--------------------------------------------------------------
def init_sandbox():
    screen.fill((20, 20, 20))
    circle.add(Circle(400, 300, 200, (255,230,230)))
    global manager
    manager = Manager()
    print("Sandbox initialized.")

init_sandbox()

### GAME LOOP ###--------------------------------------------------------------
while True:
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time

    if manager.running:
        manager.update()
        circle.draw(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if manager.running:
                    manager.stop()
                else:
                    manager.start()

    pygame.display.update()