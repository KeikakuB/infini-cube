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
    
    def play_sound(sound_name):
        pygame.mixer.music.stop()
        
        loss_tone = pygame.mixer.Sound(sound_folder + settings['sound'][sound_name])
        loss_tone.set_volume(float(settings['sound']['Volume']))
        loss_tone.play()
        
        pygame.time.wait(int(loss_tone.get_length() * 1000))
        
        pygame.mixer.music.rewind()
        pygame.mixer.music.play(-1)
    
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        
    settings = configparser.ConfigParser()
    settings.read('config' + os.sep + 'settings.ini')
    
    sound_folder = settings['sound']['FolderName'] + os.sep
    
    size = width, height = (int(settings['graphics']['Width']), int(settings['graphics']['Height'])) 
    speed = [0, 0]
    black = (0, 0, 0)
    frame_rate = int(settings['gameplay']['FrameRate'])
    
    safety_zone_x = int(settings['gameplay']['SafetyZoneX'])
    safety_zone_y = int(settings['gameplay']['SafetyZoneY'])
    
    pygame.init()
    
    font = pygame.font.SysFont("comicsansms", 12)
    
    pygame.display.set_caption("InfiniCube v0.4")
    
    pygame.mixer.music.load(sound_folder + settings['sound']['Theme'])
    pygame.mixer.music.set_volume(float(settings['sound']['Volume']))
    
    pygame.mixer.music.play(loops=-1)
    
    screen = pygame.display.set_mode(size)
    
    good_cube = PlayerCube()
    
    game_clock = pygame.time.Clock()
    
    
    base_bad_cube_speed = int(settings['gameplay']['StartSpeed'])
    speed_modifier = 0
    max_speed_modifier = int(settings['gameplay']['SpeedLevelsPerRound'])
    current_round = 0
    elapsed_time = 0
    
    max_lives = int(settings['gameplay']['NumberOfLives'])
    current_lives = max_lives 
    
    time_display = font.render(str(int(elapsed_time / 1000)), True, (255, 255, 255))
    round_display = font.render("Round: " + str(current_round), True, (255, 255, 255))
    lives_display = font.render("Lives: " + str(current_lives), True, (255, 255, 255))
    
    bad_cube_list = []
    bad_cube_counter = 0
    while True:       
        bad_cube_counter += 1
        
        if speed_modifier == max_speed_modifier:
            current_round += 1
            
            play_sound('NextRound')
            
            bad_cube_list = []
            speed_modifier = 0
            
        if bad_cube_counter % seconds_to_frames(frame_rate, 1) == 0:
            time_display = font.render(str(int(elapsed_time / 1000)), True, (255, 255, 255))
            round_display = font.render("Round: " + str(current_round), True, (255, 255, 255))
            lives_display = font.render("Lives: " + str(current_lives), True, (255, 255, 255))
        
        #Creates bad cubes
        if bad_cube_counter % seconds_to_frames(frame_rate, float(settings['gameplay']['SpawnRate'])) == 0:
            
            is_spawned = False
            
            while not is_spawned:
                cube_type = random.randint(0, 3)
                
                new_speed = base_bad_cube_speed + speed_modifier + current_round
                if cube_type == 0:
                    bad_cube = HoriCube(new_speed)
                elif cube_type == 1:
                    bad_cube = VertiCube(new_speed)
                elif cube_type == 2:
                    bad_cube = DiaCube(new_speed)
                elif cube_type == 3:
                    bad_cube = RockCube()
                
                if not good_cube.rect.inflate(safety_zone_x, safety_zone_y).colliderect(bad_cube.rect):
                    bad_cube_list.append(bad_cube)
                    is_spawned = True
        
        if bad_cube_counter % seconds_to_frames(frame_rate, float(settings['gameplay']['SecondsPerLevel'])) == 0:
            speed_modifier += 1
        
        #Detects loss condition
        if len(bad_cube_list) >= 1 and good_cube.rect.collidelist( [cube.rect for cube in bad_cube_list] ) > 0:
            play_sound('Loss')
            
            good_cube = PlayerCube()
            bad_cube_list = []
            speed_modifier = 0
            
            if current_round != 0:
                current_lives -= 1
            
            if current_lives == 0:
                elapsed_time = 0
                current_round = 0
                current_lives = max_lives
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()
            
            pressed_keys = pygame.key.get_pressed()
            
            if pressed_keys[pygame.K_ESCAPE]:
                sys.exit()
                
            #Restarts the game
            if pressed_keys[pygame.K_SPACE]:
                play_sound('Loss')
                
                good_cube = PlayerCube()
                bad_cube_list = []
                elapsed_time = 0
                speed_modifier = 0
                
                current_round = 0
                current_lives = max_lives
            
            #Controls movement
            if pressed_keys[pygame.K_LEFT]:
                good_cube.speed_x = -4
                
            elif pressed_keys[pygame.K_RIGHT]:
                good_cube.speed_x = 4
            
            else:
                good_cube.speed_x = 0
                
            if pressed_keys[pygame.K_DOWN]:
                good_cube.speed_y = 4
            
            elif pressed_keys[pygame.K_UP]:
                good_cube.speed_y = -4
            else:
                good_cube.speed_y = 0
        
        good_cube.move()
        
        #Keeps good cube on screen
        good_cube.keep_on_screen()

        screen.fill(black)
        
        for bad_cube in bad_cube_list:
            bad_cube.move()
            bad_cube.keep_on_screen()
            
            screen.blit(bad_cube.surface, bad_cube.rect)
        
        screen.blit(time_display, (width-15,height-20))
        screen.blit(round_display, (4,2))
        screen.blit(lives_display, (4,height-20))
            
        screen.blit(good_cube.surface, good_cube.rect)        
        
        pygame.display.flip()
        
        elapsed_time += game_clock.get_time()
         
        game_clock.tick(frame_rate)

def seconds_to_frames(frame_rate, number_of_seconds):
    return int(number_of_seconds * frame_rate)

if __name__== "__main__":
        main()