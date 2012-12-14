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
import configparser

def main():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        
    settings = configparser.ConfigParser()
    settings.read('config' + os.sep + 'settings.ini')
    
    pygame.init()

    size = width, height = (int(settings['graphics']['width']), int(settings['graphics']['height'])) 
    speed = [0, 0]
    black = (0, 0, 0)
    frame_rate = int(settings['graphics']['frame_rate'])
    
    screen = pygame.display.set_mode(size)
    
    image_folder = settings['images']['folder_name'] + os.sep
    
    (good_cube, good_cube_rect) = load_image(image_folder + settings['images']['good_cube'])
    
    #Move good cube to middle of screen
    good_cube_rect = good_cube_rect.move(width//2, height//2)
    
    game_clock = pygame.time.Clock()
    
    elapsed_time = 0
    bad_cube_list = []
    bad_cube_rect_list = []
    bad_cube_speed_list = []
    
    current_bad_cube_speed = 0
    bad_cube_counter = 0
    while True:       
        bad_cube_counter += 1
        
        #Creates bad cubes
        if bad_cube_counter % seconds_to_frames(frame_rate, 0.3) == 0:
            is_done = False
            
            while not is_done:
                (bad_cube, bad_cube_rect) = load_image(image_folder + settings['images']['bad_cube'] )
                bad_cube_rect = bad_cube_rect.move(random.randint(20, width - 20), random.randint(20, height - 20) )
                
                #Prevents bad cube from spawning around the good cube
                if not good_cube_rect.inflate(100, 100).colliderect(bad_cube_rect):
                    bad_cube_list.append(bad_cube)
                    bad_cube_rect_list.append(bad_cube_rect)
                    
                    
                    #Gets speed for new bad cube
                    if random.randint(0, 1) == 0:
                        if random.randint(0, 1) == 0:
                            new_speed = [0, current_bad_cube_speed]
                        else:
                            new_speed = [0, -current_bad_cube_speed]
                    else:
                        if random.randint(0, 1) == 0:
                            new_speed = [current_bad_cube_speed, 0]
                        else:
                            new_speed = [-current_bad_cube_speed, 0]
                        
                    bad_cube_speed_list.append(new_speed)
                    
                    is_done = True
        
        #Deletes bad cubes
        if bad_cube_counter % seconds_to_frames(frame_rate, 0.6) == 0:
            rand_index = random.randint(0, len(bad_cube_list) - 1)
            del bad_cube_list[rand_index]
            del bad_cube_rect_list[rand_index]
            del bad_cube_speed_list[rand_index]
        
        if bad_cube_counter % seconds_to_frames(frame_rate, 10) == 0:
            current_bad_cube_speed += 1
        
        #Detects loss condition
        if len(bad_cube_list) >= 1 and good_cube_rect.collidelist(bad_cube_rect_list) > 0:
            print("You survived: " + str(elapsed_time/1000) + " seconds")
            sys.exit()
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()
            
            pressed_keys = pygame.key.get_pressed()
            
            #Restarts the game
            if pressed_keys[pygame.K_SPACE]:
                bad_cube_list = []
                bad_cube_rect_list = []
                bad_cube_speed_list = []
                elapsed_time = 0
                current_bad_cube_speed = 0
            
            #Controls movement
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
        
        
        good_cube_rect = good_cube_rect.move(speed)
        
        #Keeps good cube on screen
        good_cube_rect = keep_on_screen(good_cube_rect, width, height)
        
        screen.fill(black)
        
        for i in range(0, len(bad_cube_list)):
            bad_cube_rect_list[i] = bad_cube_rect_list[i].move(bad_cube_speed_list[i])
            bad_cube_rect_list[i] = keep_on_screen(bad_cube_rect_list[i], width, height)
            
            screen.blit(bad_cube_list[i], bad_cube_rect_list[i])
            
        screen.blit(good_cube, good_cube_rect)
        
        
        pygame.display.flip()
        
        elapsed_time += game_clock.get_time()
         
        game_clock.tick(frame_rate)

def load_image(filename):
    image = pygame.image.load(filename).convert()
    imagerect = image.get_rect()
    
    return (image, imagerect)

def seconds_to_frames(frame_rate, number_of_seconds):
    return int(number_of_seconds * frame_rate)

def move_up(speed):
    speed[1] = -4

def move_down(speed):
    speed[1] = 4

def move_right(speed):
    speed[0] = 4

def move_left(speed):
    speed[0] = -4

def keep_on_screen(rect, width, height):
    #Keeps cube on screen
    if rect.left < 0:
        rect = rect.move(width,0)
    elif rect.right > width:
        rect = rect.move(-width,0)
    elif rect.top < 0:
        rect = rect.move(0,height)
    elif rect.bottom > height:
        rect = rect.move(0,-height)
    
    return rect

if __name__== "__main__":
        main()