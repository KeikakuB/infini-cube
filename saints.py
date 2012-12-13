#!/usr/bin/env python3

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
import sys
import os
import logging
import random

def main():
    
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    
    pygame.init()

    size = width, height = (600, 200) 
    speed = [0, 0]
    black = (0, 0, 0)
    
    screen = pygame.display.set_mode(size)
    
    image_folder = "images" + os.sep
    
    (background, background_rect) = load_image(image_folder + "background.jpg")
    (avatar, avatar_rect) = load_image(image_folder + "megaman.jpg")
    
    bomb_list = []
    bomb_counter = 0
    while True:
        
        bomb_counter += 1
        
        if bomb_counter == 300:
            (bomb, bomb_rect) = load_image(image_folder + 'Spike_Trap.png' )
            bomb_rect = bomb_rect.move(random.randint(0, width), random.randint(0, height) )
            bomb_list.append((bomb, bomb_rect))
            bomb_counter = 0
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()
            
            pressed_keys = pygame.key.get_pressed()
            
            if pressed_keys[pygame.K_LEFT] and pressed_keys[pygame.K_UP]:
                move_left(speed)
                move_up(speed)
                
            elif pressed_keys[pygame.K_LEFT] and pressed_keys[pygame.K_DOWN]: 
                move_left(speed)
                move_down(speed)
            
            elif pressed_keys[pygame.K_RIGHT] and pressed_keys[pygame.K_UP]:
                move_right(speed)
                move_up(speed)
                
            elif pressed_keys[pygame.K_RIGHT] and pressed_keys[pygame.K_DOWN]: 
                move_right(speed)
                move_down(speed)
            
            if pressed_keys[pygame.K_LEFT]:
                move_left(speed)
                
            elif pressed_keys[pygame.K_RIGHT]:
                move_right(speed)
            
            elif pressed_keys[pygame.K_DOWN]:
                move_down(speed)
            
            elif pressed_keys[pygame.K_UP]:
                move_up(speed)
            
            else:
                (speed[0], speed[1]) = (0, 0)
        
        
        avatar_rect = avatar_rect.move(speed)
        if avatar_rect.left < 0 or avatar_rect.right > width:
            speed[0] = 0
        if avatar_rect.top < 0 or avatar_rect.bottom > height:
            speed[1] = 0
        
        screen.blit(background, background_rect)
        
        for (bomb, bomb_rect) in bomb_list:
            screen.blit(bomb, bomb_rect)
            
            
        screen.blit(avatar, avatar_rect)
        
        
        pygame.display.flip()
        pygame.time.wait(10)

def load_image(filename):
    image = pygame.image.load(filename).convert()
    imagerect = image.get_rect()
    
    return (image, imagerect)

def move_up(speed):
    speed[1] = -2

def move_down(speed):
    speed[1] = 2

def move_right(speed):
    speed[0] = 2

def move_left(speed):
    speed[0] = -2
    
if __name__== "__main__":
        main()