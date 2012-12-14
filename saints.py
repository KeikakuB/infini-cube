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

    size = width, height = (400, 400) 
    speed = [0, 0]
    black = (0, 0, 0)
    
    screen = pygame.display.set_mode(size)
    
    image_folder = "images" + os.sep
    
    (white_cube, white_cube_rect) = load_image(image_folder + "white_cube.bmp")
    
    red_cube_list = []
    red_cube_rect_list = []
    red_cube_counter = 0
    while True:
        
        red_cube_counter += 1
        
        #Creates red cubes
        if red_cube_counter % 50 == 0:
            (red_cube, red_cube_rect) = load_image(image_folder + 'red_cube.bmp' )
            red_cube_rect = red_cube_rect.move(random.randint(0, width), random.randint(0, height) )
            red_cube_list.append(red_cube)
            red_cube_rect_list.append(red_cube_rect)
        
        #Deletes red cubes
        if red_cube_counter % 100 == 0:
            rand_index = random.randint(0, len(red_cube_list) - 1)
            del red_cube_list[rand_index]
            del red_cube_rect_list[rand_index]
        
        #Detects loss condition
        if len(red_cube_list) >= 1 and white_cube_rect.collidelist(red_cube_rect_list) > 0:
            print("You lose!")
            sys.exit()
        
        
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
        
        
        white_cube_rect = white_cube_rect.move(speed)
        
        #Keeps cube on screen
        if white_cube_rect.left < 0:
            white_cube_rect = white_cube_rect.move(width,0)
        elif white_cube_rect.right > width:
            white_cube_rect = white_cube_rect.move(-width,0)
        elif white_cube_rect.top < 0:
            white_cube_rect = white_cube_rect.move(0,height)
        elif white_cube_rect.bottom > height:
            white_cube_rect = white_cube_rect.move(0,-height)
        
        
        
        screen.fill(black)
        
        for (red_cube, red_cube_rect) in zip(red_cube_list, red_cube_rect_list):
            screen.blit(red_cube, red_cube_rect)
            
        screen.blit(white_cube, white_cube_rect)
        
        
        pygame.display.flip()
        pygame.time.wait(5)

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