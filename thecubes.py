# Copyright 2012 Bill Tyros
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import pygame
import random
import configparser
import os

settings = configparser.ConfigParser()
settings.read('config' + os.sep + 'settings.ini')

width = int(settings['graphics']['Width'])
height = int(settings['graphics']['Height'])


spawn_buffer = int(settings['gameplay']['SpawnBuffer'])

image_folder = settings['images']['FolderName'] + os.sep

player_filename = image_folder + settings['images']['PlayerCube']
hori_filename = image_folder + settings['images']['HoriCube']
verti_filename = image_folder + settings['images']['VertiCube']
dia_filename = image_folder + settings['images']['DiaCube']


class Cube(object):
    """Represents a graphical Cube."""    
    def __init__(self, filename, speed_x=0, speed_y=0):
        """Initializes a Cube."""
        (self._surface, self._rect) = load_image(filename)
        self._speed_x = speed_x
        self._speed_y = speed_y
    
    @property
    def surface(self):
        return self._surface
    
    @property
    def rect(self):
        return self._rect
    
    @rect.setter
    def rect(self, new_rect):
        self._rect = new_rect

    def set_speed(self, x_y_speed):
        self._speed_x = x_y_speed[0]
        self._speed_y = x_y_speed[1]

    @property
    def speed_x(self):
        return self._speed_x
    
    @speed_x.setter
    def speed_x(self, new_speed_x):
        self._speed_x = new_speed_x
    
    @property
    def speed_y(self):
        return self._speed_y
    
    @speed_y.setter
    def speed_y(self, new_speed_y):
        self._speed_y = new_speed_y
    
    def move(self):
        self._rect = self._rect.move(self._speed_x, self._speed_y)
    
    def keep_on_screen(self):
        #Keeps cube on screen
        if self.rect.left < 0:
            self.rect = self.rect.move(width,0)
        elif self.rect.right > width:
            self.rect = self.rect.move(-width,0)
        elif self.rect.top < 0:
            self.rect = self.rect.move(0,height)
        elif self.rect.bottom > height:
            self.rect = self.rect.move(0,-height)

class PlayerCube(Cube):
    def __init__(self):
        super().__init__(player_filename)
        
        #Move cube to middle of screen
        self.rect = self.rect.move(width//2, height//2)

class HoriCube(Cube):
    
    def __init__(self, speed):
        super().__init__(hori_filename)
        
        if random.randint(0,1):
            spawn_delta = get_spawn_delta('left')
            self.speed_x = speed
        else:
            spawn_delta = get_spawn_delta('right')
            self.speed_x = -speed
        
        self.rect = self.rect.move(spawn_delta[0], spawn_delta[1])

class VertiCube(Cube):
    
    def __init__(self, speed):
        super().__init__(verti_filename)
        
        if random.randint(0,1):
            spawn_delta = get_spawn_delta('top')
            self.speed_y = speed
        else:
            spawn_delta = get_spawn_delta('bottom')
            self.speed_y = -speed
        
        self.rect = self.rect.move(spawn_delta[0], spawn_delta[1])
            
class DiaCube(Cube):
    def __init__(self, speed):
        super().__init__(dia_filename)
        
        if random.randint(0,1):
            if random.randint(0,1):
                spawn_delta = get_spawn_delta('left')
                self.speed_x = speed
            else:
                spawn_delta = get_spawn_delta('right')
                self.speed_x = -speed
            
            if random.randint(0,1):
                self.speed_y = speed
            else:
                self.speed_y = -speed
                
        else:
            if random.randint(0,1):
                spawn_delta = get_spawn_delta('top')
                self.speed_y = speed
            else:
                spawn_delta = get_spawn_delta('bottom')
                self.speed_y = -speed
            
            if random.randint(0,1):
                self.speed_x = speed
            else:
                self.speed_x = -speed
        
        self.rect = self.rect.move(spawn_delta[0], spawn_delta[1])

def get_spawn_delta(direction):
    if direction == 'left':
        return [spawn_buffer, random.randint(spawn_buffer, height - spawn_buffer)]
    elif direction == 'right':
        return [width - spawn_buffer, random.randint(spawn_buffer, height - spawn_buffer)]
    elif direction == 'top':
        return [random.randint(spawn_buffer, width - spawn_buffer), spawn_buffer]
    elif direction == 'bottom':
        return [random.randint(spawn_buffer, width - spawn_buffer), height - spawn_buffer]

def load_image(filename):
    image = pygame.image.load(filename).convert()
    imagerect = image.get_rect()
    
    return (image, imagerect)