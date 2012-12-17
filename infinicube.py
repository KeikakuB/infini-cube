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

from thecubes import PlayerCube, HoriLeftCube, HoriRightCube, VertiTopCube, VertiBotCube, DiaCube, RockCube

import csv

def main():
    CUBE_TYPES = ['HoriLeftCube','HoriRightCube','VertiTopCube',
                  'VertiBotCube','DiaCube','RockCube']
    
    WHITE = (255,255,255)
    
    HIGHSCORE_FILENAME = 'highscores.txt'
    
    def play_sound(sound_name):
        pygame.mixer.music.stop()
        
        sound = pygame.mixer.Sound(sound_folder + settings['sound'][sound_name])
        sound.set_volume(float(settings['sound']['Volume']))
        sound.play()
        
        pygame.time.wait(int(sound.get_length() * 1000))
        
        pygame.mixer.music.rewind()
        pygame.mixer.music.play(-1)
    
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        
    settings = configparser.ConfigParser()
    settings.read('config' + os.sep + 'settings.ini')
    
    if settings['gameplay']['CheatsEnabled'] == '1':
        cheats_enabled = True
    else:
        cheats_enabled = False
    
    
    sound_folder = settings['sound']['FolderName'] + os.sep
    
    size = width, height = (int(settings['graphics']['Width']), int(settings['graphics']['Height'])) 
    black = (0, 0, 0)
    frame_rate = int(settings['gameplay']['FrameRate'])
    
    safety_zone_x = int(settings['gameplay']['SafetyZoneX'])
    safety_zone_y = int(settings['gameplay']['SafetyZoneY'])
    
    pygame.init()
    
    font = pygame.font.SysFont("comicsansms", 12)
    
    pygame.display.set_caption("InfiniCube v0.7")
    
    pygame.mixer.music.load(sound_folder + settings['sound']['Theme'])
    pygame.mixer.music.set_volume(float(settings['sound']['Volume']))
    
    pygame.mixer.music.play(loops=-1)
    
    screen = pygame.display.set_mode(size)
    
    good_cube = PlayerCube()
    
    game_clock = pygame.time.Clock()
    
    
    campaign_settings = configparser.ConfigParser()
    campaign_settings.read('config' + os.sep + 'campaign.ini')
    
    levels = campaign_settings.sections()
    
    max_lives = int(settings['gameplay']['NumberOfLives'])
    current_lives = max_lives
    
    #Build score zones
    score_zone_A = pygame.Rect( (0,0), (width//5, height//5))
    score_zone_B = pygame.Rect( (0,0), (width//2, height//2))
    score_zone_C = pygame.Rect( (0,0), (width, height))
    
    score_zones = [score_zone_A, score_zone_B, score_zone_C]
    
    for score_zone in score_zones:
        score_zone.center = (width//2, height//2)
    
    current_score = 0
    current_zone = 'A'
    
    is_campaign_finished = False
    
    current_level_index = -1
    is_new_round = True
    has_died = False
    while True:
        zone_index = good_cube.rect.collidelist(score_zones)
        if zone_index != -1:            
            if zone_index == 0:
                score_to_add = 7
                current_zone = 'A'
            
            elif zone_index == 1:
                score_to_add = 3
                current_zone = 'B'
                
            elif zone_index == 2:
                score_to_add = 1
                current_zone = 'C'
            
            current_score += score_to_add
        
        if is_new_round or has_died:            
            if not has_died and current_level_index != -1:
                play_sound('NextRound')
                play_sound('NextRound')
                current_level_index += 1
                current_lives += 1 
                
            if current_level_index == -1:
                current_level_index += 1                     
                
            if has_died:
                def save_score(campaign_short_name):
                    
                    high_score_filename = campaign_short_name + '_' + HIGHSCORE_FILENAME
                    #Add new score
                    with open(high_score_filename, 'a', newline='') as csvfile:
                        high_score_writer = csv.writer(csvfile, delimiter=' ',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        
                        score_str = str(current_score)
                        level_str = "Level #" + str(current_level_index + 1) + " - " + level_name
                        
                        high_score = [score_str, level_str]
                        high_score_writer.writerow(high_score)
                    
                    #Sort scores
                    with open(high_score_filename, newline='') as csvfile:
                        high_score_reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                        high_scores = list(high_score_reader)[1:]
                        high_scores.sort(key=lambda row: int(row[0]), reverse=True)
                    
                    #Write new sorted scores
                    with open(high_score_filename, 'w', newline='') as csvfile:
                        high_score_writer = csv.writer(csvfile, delimiter=' ',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        
                        high_score_writer.writerow([campaign_settings[level_name]['CampaignName']])
                        for high_score in high_scores:
                            high_score_writer.writerow(high_score)
                
                play_sound('Loss')
                play_sound('Loss')
                
                if current_level_index == 0 and current_lives == 1:
                    save_score(campaign_settings[level_name]['CampaignShortName'])
                    
                    current_score = 0
                    
                if current_level_index != 0:
                    current_lives -= 1
                    
                if current_lives == 0:
                    save_score(campaign_settings[level_name]['CampaignShortName'])
                    
                    current_level_index = 0
                    current_score = 0
                    current_lives = max_lives
            
            
            #Win Condition (TODO: Write high score)
            if current_level_index > len(levels)-1:
                sys.exit(0)
            
            level_name = levels[current_level_index]
            
            good_cube = PlayerCube()
            
            good_cube_speed = int(campaign_settings[level_name]['GoodCubeSpeed'])
            
            if campaign_settings[level_name]['KeepOnScreen'] == '1':
                should_keep_on_screen = True
            else:
                should_keep_on_screen = False
            
            base_bad_cube_speed = int(campaign_settings[level_name]['StartSpeed'])
            speed_modifier = 0
            
            max_speed_modifier = int(campaign_settings[level_name]['SpeedLevelsPerRound'])
            seconds_per_level = float(campaign_settings[level_name]['SecondsPerLevel'])
            
            bad_cube_spawn_rate = float(campaign_settings[level_name]['SpawnRate'])
            
            max_hori_left_cubes = int(campaign_settings[level_name]['MaxHoriLCubes'])
            max_hori_right_cubes = int(campaign_settings[level_name]['MaxHoriRCubes'])
            
            max_verti_top_cubes = int(campaign_settings[level_name]['MaxVertiTCubes'])
            max_verti_bottom_cubes = int(campaign_settings[level_name]['MaxVertiBCubes'])
            
            max_dia_cubes = int(campaign_settings[level_name]['MaxDiaCubes'])
            max_rock_cubes = int(campaign_settings[level_name]['MaxRockCubes'])
            
            
            bad_cube_maxes_dict = {CUBE_TYPES[0]: max_hori_left_cubes,
                                   CUBE_TYPES[1]: max_hori_right_cubes,
                                   CUBE_TYPES[2]: max_verti_top_cubes,
                                   CUBE_TYPES[3]: max_verti_bottom_cubes,
                                   CUBE_TYPES[4]: max_dia_cubes, 
                                   CUBE_TYPES[5]: max_rock_cubes}
            
            bad_cube_list = []
            bad_cube_counts_dict = {CUBE_TYPES[0]: 0, CUBE_TYPES[1]: 0,
                                    CUBE_TYPES[2]: 0, CUBE_TYPES[3]: 0,
                                    CUBE_TYPES[4]: 0, CUBE_TYPES[5]: 0}
            
            frame_counter = 0
            
            zone_display = font.render("Zone: " + current_zone, True, WHITE)
            score_display = font.render("Score: " + str(current_score), True, WHITE)
            round_display = font.render("Level #" + str(current_level_index + 1) + ': ' + level_name, True, WHITE)
            lives_display = font.render("Lives: " + str(current_lives), True, WHITE)
            
            if is_campaign_finished:
                sys.exit(0)
        
            is_new_round = False
            has_died = False
        
        frame_counter += 1        
        
        if speed_modifier == max_speed_modifier:
            is_new_round = True
            
        #Creates bad cubes
        if frame_counter % seconds_to_frames(frame_rate, bad_cube_spawn_rate) == 0:
            
            is_spawned = False
            
            while not is_spawned:
                cube_type_index = random.randint(0, 5)
                
                new_speed = base_bad_cube_speed + speed_modifier
                
                cube_name = CUBE_TYPES[cube_type_index]
                
                if bad_cube_counts_dict[cube_name] < bad_cube_maxes_dict[cube_name]:
                    if cube_name == CUBE_TYPES[0]:
                        bad_cube = HoriLeftCube(new_speed)
                        bad_cube_counts_dict[cube_name] += 1
                    elif cube_name == CUBE_TYPES[1]:
                        bad_cube = HoriRightCube(new_speed)
                        bad_cube_counts_dict[cube_name] += 1
                    elif cube_name == CUBE_TYPES[2]:
                        bad_cube = VertiTopCube(new_speed)
                        bad_cube_counts_dict[cube_name] += 1
                    elif cube_name == CUBE_TYPES[3]:
                        bad_cube = VertiBotCube(new_speed)
                        bad_cube_counts_dict[cube_name] += 1
                    elif cube_name == CUBE_TYPES[4]:
                        bad_cube = DiaCube(new_speed)
                        bad_cube_counts_dict[cube_name] += 1
                    elif cube_name == CUBE_TYPES[5]:
                        bad_cube = RockCube()
                        bad_cube_counts_dict[cube_name] += 1
                    
                    
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
            if cheats_enabled:
                def change_round(round_number, by_how_much):
                    return (round_number + by_how_much, True, True, 999)
                
                if pressed_keys[pygame.K_PAGEUP]:
                    (current_level_index, is_new_round, has_died, current_lives) = change_round(current_level_index, 1)
                elif pressed_keys[pygame.K_PAGEDOWN]:
                    (current_level_index, is_new_round, has_died, current_lives) = change_round(current_level_index, -1)
                
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
            #TODO: Should be using Pythagor (sp?) theorem. (Only works well for
            # multiples of 4 now
            if good_cube.speed_x and good_cube.speed_y:
                if good_cube.speed_x > 0:
                    good_cube.speed_x = good_cube.speed_x // 2 + good_cube.speed_x // 4
                else:
                    good_cube.speed_x = good_cube.speed_x // 2 - ((-good_cube.speed_x) // 4)
                
                if good_cube.speed_y > 0:
                    good_cube.speed_y = good_cube.speed_y // 2 + good_cube.speed_y // 4
                else:
                    good_cube.speed_y = good_cube.speed_y // 2 - ((-good_cube.speed_y) // 4)
        
        good_cube.move()
        
        #Keeps good cube on screen
        good_cube.keep_on_screen()

        screen.fill(black)
        
        indices_to_delete = []
        for i in range(0, len(bad_cube_list)):
            bad_cube_list[i].move()
            
            if bad_cube_list[i].is_off_screen():
                
                if should_keep_on_screen:
                    bad_cube_list[i].keep_on_screen()
                else:
                    indices_to_delete.append(i)
            
            screen.blit(bad_cube_list[i].surface, bad_cube_list[i].rect)
        
        del_count = 0
        for index in indices_to_delete:
            cube_to_delete = bad_cube_list[index-del_count]
            
            if isinstance(cube_to_delete, HoriLeftCube):
                bad_cube_counts_dict[CUBE_TYPES[0]] -= 1
            elif isinstance(cube_to_delete, HoriRightCube):
                bad_cube_counts_dict[CUBE_TYPES[1]] -= 1
            elif isinstance(cube_to_delete, VertiTopCube):
                bad_cube_counts_dict[CUBE_TYPES[2]] -= 1
            elif isinstance(cube_to_delete, VertiBotCube):
                bad_cube_counts_dict[CUBE_TYPES[3]] -= 1
            elif isinstance(cube_to_delete, DiaCube):
                bad_cube_counts_dict[CUBE_TYPES[4]] -= 1
            elif isinstance(cube_to_delete, RockCube):
                bad_cube_counts_dict[CUBE_TYPES[5]] -= 1
            
            del bad_cube_list[index-del_count]
            del_count += 1
        
        zone_display = font.render("Zone: " + current_zone, True, WHITE)
        score_display = font.render(str(current_score), True, WHITE)
        
        screen.blit(zone_display, (width - zone_display.get_width(), height-zone_display.get_height()))
        screen.blit(score_display, (width - score_display.get_width(),0 ))    
        screen.blit(round_display, (0,0))
        screen.blit(lives_display, (0,height-lives_display.get_height()))
            
        screen.blit(good_cube.surface, good_cube.rect)        
        
        pygame.display.flip()
         
        game_clock.tick(frame_rate)

def seconds_to_frames(frame_rate, number_of_seconds):
    return int(number_of_seconds * frame_rate)

if __name__== "__main__":
        main()