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

from thecubes import *


def main():
    
    def play_loss_sound():
        pygame.mixer.music.stop()
        
        loss_tone = pygame.mixer.Sound(sound_folder + settings['sound']['LossTone'])
        loss_tone.set_volume(float(settings['sound']['Volume']))
        loss_tone.play()
        
        pygame.time.wait(int(loss_tone.get_length() * 1000))
        
        pygame.mixer.music.rewind()
        pygame.mixer.music.play(-1)
    
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        
    settings = configparser.ConfigParser()
    settings.read('config' + os.sep + 'settings.ini')
    
    sound_folder = settings['sound']['FolderName'] + os.sep

    pygame.init()
    
    pygame.display.set_caption("InfiniCube v0.4")
    
    font = pygame.font.SysFont("comicsansms", 12)
    
    size = width, height = (int(settings['graphics']['Width']), int(settings['graphics']['Height'])) 
    speed = [0, 0]
    black = (0, 0, 0)
    frame_rate = int(settings['gameplay']['FrameRate'])
    
    pygame.mixer.music.load(sound_folder + settings['sound']['Theme'])
    pygame.mixer.music.set_volume(float(settings['sound']['Volume']))
    
    pygame.mixer.music.play(loops=-1)
    
    screen = pygame.display.set_mode(size)
    
    good_cube = PlayerCube()
    
    game_clock = pygame.time.Clock()
    
    elapsed_time = 0
    
    score_timer = font.render(str(int(elapsed_time / 1000)), True, (255, 255, 255))
    
    bad_cube_list = []
    
    base_bad_cube_speed = 1
    current_bad_cube_speed = base_bad_cube_speed
    
    bad_cube_counter = 0
    while True:       
        bad_cube_counter += 1
        
        if bad_cube_counter % seconds_to_frames(frame_rate, 1) == 0:
            score_timer = font.render(str(int(elapsed_time / 1000)), True, (255, 255, 255))
        
        #Creates bad cubes
        if bad_cube_counter % seconds_to_frames(frame_rate, float(settings['gameplay']['SpawnRate'])) == 0:
            cube_type = random.randint(0, 2)
            
            if cube_type == 0:
                bad_cube = HoriCube(current_bad_cube_speed)
            elif cube_type == 1:
                bad_cube = VertiCube(current_bad_cube_speed)
            elif cube_type == 2:
                bad_cube = DiaCube(current_bad_cube_speed) 
            
            bad_cube_list.append(bad_cube)
        
        if bad_cube_counter % seconds_to_frames(frame_rate, 10) == 0:
            current_bad_cube_speed += 1
        
        #Detects loss condition
        if len(bad_cube_list) >= 1 and good_cube.rect.collidelist( [cube.rect for cube in bad_cube_list] ) > 0:
            play_loss_sound()
            
            good_cube = PlayerCube()
            bad_cube_list = []
            elapsed_time = 0
            current_bad_cube_speed = base_bad_cube_speed
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()
            
            pressed_keys = pygame.key.get_pressed()
            
            if pressed_keys[pygame.K_ESCAPE]:
                sys.exit()
                
            #Restarts the game
            if pressed_keys[pygame.K_SPACE]:
                play_loss_sound()
                
                good_cube = PlayerCube()
                bad_cube_list = []
                elapsed_time = 0
                current_bad_cube_speed = base_bad_cube_speed
            
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
        
        
        good_cube.rect = good_cube.rect.move(speed)
        
        #Keeps good cube on screen
        good_cube.keep_on_screen()

        screen.fill(black)
        
        for bad_cube in bad_cube_list:
            bad_cube.move()
            bad_cube.keep_on_screen()
            
            screen.blit(bad_cube.surface, bad_cube.rect)
        
        screen.blit(good_cube.surface, good_cube.rect)
        
        screen.blit(score_timer, (width-15,height-20))
        
        pygame.display.flip()
        
        elapsed_time += game_clock.get_time()
         
        game_clock.tick(frame_rate)

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

if __name__== "__main__":
        main()