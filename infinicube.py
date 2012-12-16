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
    
    LEFT = 'left'
    RIGHT = 'right'
    TOP = 'top'
    BOTTOM = 'bottom'
    
    
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
    black = (0, 0, 0)
    frame_rate = int(settings['gameplay']['FrameRate'])
    
    safety_zone_x = int(settings['gameplay']['SafetyZoneX'])
    safety_zone_y = int(settings['gameplay']['SafetyZoneY'])
    
    pygame.init()
    
    font = pygame.font.SysFont("comicsansms", 12)
    
    pygame.display.set_caption("InfiniCube v0.6")
    
    pygame.mixer.music.load(sound_folder + settings['sound']['Theme'])
    pygame.mixer.music.set_volume(float(settings['sound']['Volume']))
    
    pygame.mixer.music.play(loops=-1)
    
    screen = pygame.display.set_mode(size)
    
    good_cube = PlayerCube()
    
    game_clock = pygame.time.Clock()
    
    
    round_settings = configparser.ConfigParser()
    round_settings.read('config' + os.sep + 'rounds.ini')
    
    max_lives = int(settings['gameplay']['NumberOfLives'])
    current_lives = max_lives
    
    current_round = -1
    is_new_round = True
    has_died = False
    while True:
        
        if is_new_round or has_died:            
            if not has_died and current_round != -1:
                play_sound('NextRound')
                current_round += 1
                current_lives += 1 
                
            if current_round == -1:
                current_round += 1                     
                
            if has_died:
                play_sound('Loss')
                
                if current_round != 0:
                    current_lives -= 1
                
                if current_lives == 0:
                    current_round = 0
                    current_lives = max_lives
            
            round_str = 'round' + str(current_round)
            
            round_name = round_settings[round_str]['Name']
            
            good_cube = PlayerCube()
            
            good_cube_speed = int(round_settings[round_str]['GoodCubeSpeed'])
            
            
            base_bad_cube_speed = int(round_settings[round_str]['StartSpeed'])
            speed_modifier = 0
            
            max_speed_modifier = int(round_settings[round_str]['SpeedLevelsPerRound'])
            seconds_per_level = float(round_settings[round_str]['SecondsPerLevel'])
            
            bad_cube_spawn_rate = float(round_settings[round_str]['SpawnRate'])
            
            max_hori_left_cubes = int(round_settings[round_str]['MaxHoriLCubes'])
            max_hori_right_cubes = int(round_settings[round_str]['MaxHoriRCubes'])
            
            max_verti_top_cubes = int(round_settings[round_str]['MaxVertiTCubes'])
            max_verti_bottom_cubes = int(round_settings[round_str]['MaxVertiBCubes'])
            
            max_dia_cubes = int(round_settings[round_str]['MaxDiaCubes'])
            max_rock_cubes = int(round_settings[round_str]['MaxRockCubes'])
            
            bad_cube_maxes = [max_hori_left_cubes,max_hori_right_cubes,max_verti_top_cubes, max_verti_bottom_cubes,max_dia_cubes, max_rock_cubes]
            
            bad_cube_list = []
            bad_cube_counts = [0, 0, 0, 0, 0, 0]
            
            frame_counter = 0
            
            round_display = font.render("Round #" + str(current_round) + ': ' + round_name, True, (255, 255, 255))
            lives_display = font.render("Lives: " + str(current_lives), True, (255, 255, 255))
            
            is_new_round = False
            has_died = False
        
        
        frame_counter += 1
        
        if speed_modifier == max_speed_modifier:
            is_new_round = True
            
        #Creates bad cubes
        if frame_counter % seconds_to_frames(frame_rate, bad_cube_spawn_rate) == 0:
            
            is_spawned = False
            
            while not is_spawned:
                cube_type = random.randint(0, 5)
                
                new_speed = base_bad_cube_speed + speed_modifier
                
                if bad_cube_counts[cube_type] < bad_cube_maxes[cube_type]:
                    if cube_type == 0:
                        bad_cube = HoriCube(LEFT, new_speed)
                        bad_cube_counts[cube_type] += 1
                    elif cube_type == 1:
                        bad_cube = HoriCube(RIGHT, new_speed)
                        bad_cube_counts[cube_type] += 1
                    elif cube_type == 2:
                        bad_cube = VertiCube(TOP, new_speed)
                        bad_cube_counts[cube_type] += 1
                    elif cube_type == 3:
                        bad_cube = VertiCube(BOTTOM, new_speed)
                        bad_cube_counts[cube_type] += 1
                    elif cube_type == 4:
                        bad_cube = DiaCube(new_speed)
                        bad_cube_counts[cube_type] += 1
                    elif cube_type == 5:
                        bad_cube = RockCube()
                        bad_cube_counts[cube_type] += 1
                    
                    
                    if not good_cube.rect.inflate(safety_zone_x, safety_zone_y).colliderect(bad_cube.rect):
                        bad_cube_list.append(bad_cube)
                        is_spawned = True
        
        if frame_counter % seconds_to_frames(frame_rate, seconds_per_level) == 0:
            speed_modifier += 1
        
        #Detects loss condition
        if len(bad_cube_list) >= 1 and good_cube.rect.collidelist( [cube.rect for cube in bad_cube_list] ) != -1:
            has_died = True
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()
            
            pressed_keys = pygame.key.get_pressed()
            
            
            if pressed_keys[pygame.K_ESCAPE]:
                sys.exit()
            
            #DEBUG: Fast Round Switch
            if pressed_keys[pygame.K_0]:
                is_new_round = True
                has_died = True
                current_lives = 999
                current_round = 0
            if pressed_keys[pygame.K_1]:
                is_new_round = True
                has_died = True
                current_lives = 999
                current_round = 1
            if pressed_keys[pygame.K_2]:
                is_new_round = True
                has_died = True
                current_lives = 999
                current_round = 2
            if pressed_keys[pygame.K_3]:
                is_new_round = True
                has_died = True
                current_lives = 999
                current_round = 3
            if pressed_keys[pygame.K_4]:
                is_new_round = True
                has_died = True
                current_lives = 999
                current_round = 4
            if pressed_keys[pygame.K_5]:
                is_new_round = True
                has_died = True
                current_lives = 999
                current_round = 5
            if pressed_keys[pygame.K_6]:
                is_new_round = True
                has_died = True
                current_lives = 999
                current_round = 6
            if pressed_keys[pygame.K_7]:
                is_new_round = True
                has_died = True
                current_lives = 999
                current_round = 7
            if pressed_keys[pygame.K_8]:
                is_new_round = True
                has_died = True
                current_lives = 999
                current_round = 8
            if pressed_keys[pygame.K_9]:
                is_new_round = True
                has_died = True
                current_lives = 999
                current_round = 9
            
            
            #Controls movement
            if pressed_keys[pygame.K_LEFT]:
                good_cube.speed_x = -good_cube_speed
                
            elif pressed_keys[pygame.K_RIGHT]:
                good_cube.speed_x = good_cube_speed
            
            else:
                good_cube.speed_x = 0
                
            if pressed_keys[pygame.K_DOWN]:
                good_cube.speed_y = good_cube_speed
            
            elif pressed_keys[pygame.K_UP]:
                good_cube.speed_y = -good_cube_speed
            else:
                good_cube.speed_y = 0
            
            #Keeps absolute speed constant-ish diagonal vs. straight
            if good_cube.speed_x and good_cube.speed_y:
                if good_cube.speed_x > 0:
                    good_cube.speed_x = good_cube.speed_x // 2 + 2
                else:
                    good_cube.speed_x = good_cube.speed_x // 2 - 2
                
                if good_cube.speed_y > 0:
                    good_cube.speed_y = good_cube.speed_y // 2 + 1
                else:
                    good_cube.speed_y = good_cube.speed_y // 2 - 1
        
        good_cube.move()
        
        #Keeps good cube on screen
        good_cube.keep_on_screen()

        screen.fill(black)
        
        for bad_cube in bad_cube_list:
            bad_cube.move()
            bad_cube.keep_on_screen()
            
            screen.blit(bad_cube.surface, bad_cube.rect)
        
        screen.blit(round_display, (4,2))
        screen.blit(lives_display, (4,height-20))
            
        screen.blit(good_cube.surface, good_cube.rect)        
        
        pygame.display.flip()
         
        game_clock.tick(frame_rate)

def seconds_to_frames(frame_rate, number_of_seconds):
    return int(number_of_seconds * frame_rate)

if __name__== "__main__":
        main()