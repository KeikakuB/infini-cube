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
    def play_sound(game_config, sound_name):
        if not game_config[SKIP_SOUNDS]:
            pygame.mixer.music.stop()
            
            sound_folder = settings['sound']['FolderName'] + os.sep
            
            sound = pygame.mixer.Sound(sound_folder + settings['sound'][sound_name])
            sound.set_volume(float(settings['sound']['Volume']))
            sound.play()
            
            pygame.time.wait(int(sound.get_length() * 1000))
            
            pygame.mixer.music.rewind()
            pygame.mixer.music.play(-1)
    
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        
    settings = configparser.ConfigParser()
    settings.read('config' + os.sep + 'settings.ini')
    
    
    CUBE_TYPES = ['HoriLeftCube','HoriRightCube','VertiTopCube',
                  'VertiBotCube','DiaCube','RockCube']
    
    WHITE = (255,255,255)
    GRAY = (84,84,84)
    BLACK = (0, 0, 0)
    
    HIGHSCORE_FOLDER = 'highscores' + os.sep
    HIGHSCORE_FILENAME = 'highscores.txt'
    
    #game_state dictionary keys
    game_state = {}
    
    FRAME_COUNTER = 'frame_counter'
    CURRENT_LIVES = 'current_lives'
    MAX_LIVES = 'max_lives'
    CURRENT_SCORE = 'current_score'
    CURRENT_LEVEL_INDEX = 'current_level_index'
    SPEED_MODIFIER = 'speed_modifier'
    MAX_SPEED_MODIFIER = 'max_speed_modifier'
    
    LEVEL_NAME = 'level_name'
    
    IS_NEW_ROUND = 'is_new_round'
    HAS_DIED = 'has_died'
    
    BASE_BAD_CUBE_SPEED = 'base_bad_cube_speed'
    SECONDS_PER_LEVEL = 'seconds_per_level'
    
    BAD_CUBE_SPAWN_RATE = 'bad_cube_spawn_rate'    
    
    BAD_CUBE_MAXIMUMS = 'bad_cube_maximums'
    
    BAD_CUBE_COUNTS = 'bad_cube_counts'
    
    GAME_CLOCK = 'game_clock'
    SCORE_ZONES = 'score_zones'
    
    LEVELS = 'levels'
    
    PLAYER_CUBE = 'player_cube'
    PLAYER_CUBE_SPEED = 'player_cube_speed'
    SHOULD_KEEP_ON_SCREEN = 'should_keep_on_screen'
    BAD_CUBES = 'bad_cubes'    
    
    #game_config dictionary keys
    game_config = {}
    
    WIDTH = 'width'
    HEIGHT = 'height'
    FRAME_RATE = 'frame_rate'
    FONT = 'font'
    
    CHEATS_ENABLED = 'cheats_enabled'
    SKIP_SOUNDS = 'skip_sounds'
    
    SAFETY_ZONE_X = 'safety_zone_x'
    SAFETY_ZONE_Y = 'safety_zone_y'
    
    if settings['gameplay']['CheatsEnabled'] == '1':
        game_config[CHEATS_ENABLED] = True
    else:
        game_config[CHEATS_ENABLED] = False
    
    if settings['sound']['SkipSounds'] == '1':
        game_config[SKIP_SOUNDS] = True
    else:
        game_config[SKIP_SOUNDS] = False
    
    game_config[WIDTH] = int(settings['graphics']['Width'])
    game_config[HEIGHT] = int(settings['graphics']['Height'])
    
    game_config[FRAME_RATE] = int(settings['gameplay']['FrameRate'])
    
    game_config[SAFETY_ZONE_X] = int(settings['gameplay']['SafetyZoneX'])
    game_config[SAFETY_ZONE_Y] = int(settings['gameplay']['SafetyZoneY'])
    
    
    pygame.init()
    
    game_config[FONT] = pygame.font.SysFont("comicsansms", 12)
    
    pygame.display.set_caption("InfiniCube v0.7")
    
    pygame.mixer.music.load(settings['sound']['FolderName'] + os.sep + settings['sound']['Theme'])
    pygame.mixer.music.set_volume(float(settings['sound']['Volume']))
    
    pygame.mixer.music.play(loops=-1)
    
    screen = pygame.display.set_mode((game_config[WIDTH],game_config[HEIGHT]))
    
    
    game_state[PLAYER_CUBE] = PlayerCube()
    
    game_state[GAME_CLOCK] = pygame.time.Clock()
    
    campaign_settings = configparser.ConfigParser()
    campaign_settings.read('campaigns' + os.sep + settings['gameplay']['CampaignFilename'])
    
    game_state[LEVELS] = campaign_settings.sections()
    
    game_state[MAX_LIVES] = int(campaign_settings['DEFAULT']['NumberOfLives'])
    game_state[CURRENT_LIVES] = game_state[MAX_LIVES]
    
    #Build score zones
    score_zone_A = pygame.Rect( (0,0), (int(game_config[WIDTH]//4 * 1.5), int(game_config[HEIGHT]//4 * 1.5)))
    score_zone_B = pygame.Rect( (0,0), (int(game_config[WIDTH]//2 * 1.5), int(game_config[HEIGHT]//2 * 1.5)))
    score_zone_C = pygame.Rect( (0,0), (game_config[WIDTH], game_config[HEIGHT]))
    
    
    game_state[SCORE_ZONES] = [('A', score_zone_A), ('B', score_zone_B), ('C', score_zone_C)]
    
    for (_, score_zone) in game_state[SCORE_ZONES]:
        score_zone.center = (game_config[WIDTH]//2, game_config[HEIGHT]//2)
    
    game_state[CURRENT_SCORE] = 0
    
    game_state[CURRENT_LEVEL_INDEX] = -1
    
    game_state[IS_NEW_ROUND] = True
    game_state[HAS_DIED] = False
    while True:
        zone_index = game_state[PLAYER_CUBE].rect.collidelist([zone for (_, zone) in game_state[SCORE_ZONES]])
        if zone_index != -1:            
            if zone_index == 0:
                score_to_add = 7
            
            elif zone_index == 1:
                score_to_add = 3
                
            elif zone_index == 2:
                score_to_add = 1
            
            game_state[CURRENT_SCORE] += score_to_add
        
        if game_state[IS_NEW_ROUND] or game_state[HAS_DIED]:            
            if not game_state[HAS_DIED] and game_state[CURRENT_LEVEL_INDEX] != -1:
                play_sound(game_config, 'NextRound')
                play_sound(game_config, 'NextRound')
                game_state[CURRENT_LEVEL_INDEX] += 1
                game_state[CURRENT_LIVES] += 1 
                
            if game_state[CURRENT_LEVEL_INDEX] == -1:
                game_state[CURRENT_LEVEL_INDEX] += 1                     
                
            if game_state[HAS_DIED]:
                def save_score(game_state, campaign_short_name):
                    
                    high_score_filename = HIGHSCORE_FOLDER + campaign_short_name + '_' + HIGHSCORE_FILENAME
                    #Add new score
                    with open(high_score_filename, 'a', newline='') as csvfile:
                        high_score_writer = csv.writer(csvfile, delimiter=' ',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        
                        score_str = str(game_state[CURRENT_SCORE])
                        level_str = "Level #" + str(game_state[CURRENT_LEVEL_INDEX] + 1) + " - " + game_state[LEVEL_NAME]
                        
                        high_score = [score_str, level_str]
                        high_score_writer.writerow(high_score)
                    
                    #Sort scores
                    with open(high_score_filename, newline='') as csvfile:
                        high_score_reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                        
                        high_scores = list(high_score_reader)
                        
                        #removes campaign title if there
                        high_scores = [high_score for high_score in high_scores if len(high_score) != 1]
                        
                        high_scores.sort(key=lambda row: int(row[0]), reverse=True)
                    
                    #Write new sorted scores
                    with open(high_score_filename, 'w', newline='') as csvfile:
                        high_score_writer = csv.writer(csvfile, delimiter=' ',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        
                        high_score_writer.writerow([campaign_settings[game_state[LEVEL_NAME]]['CampaignName']])
                        for high_score in high_scores:
                            high_score_writer.writerow(high_score)
                
                play_sound(game_config, 'Loss')
                play_sound(game_config, 'Loss')
                
                if game_state[CURRENT_LEVEL_INDEX] == 0 and game_state[CURRENT_LIVES] == game_state[MAX_LIVES]:
                    save_score(game_state, campaign_settings[game_state[LEVEL_NAME]]['CampaignShortName'])
                    
                    game_state[CURRENT_SCORE] = 0
                    
                if game_state[CURRENT_LEVEL_INDEX] != 0:
                    game_state[CURRENT_LIVES] -= 1
                    
                if game_state[CURRENT_LIVES] == 0:
                    save_score(game_state, campaign_settings[game_state[LEVEL_NAME]]['CampaignShortName'])
                    
                    game_state[CURRENT_LEVEL_INDEX] = 0
                    game_state[CURRENT_SCORE] = 0
                    game_state[CURRENT_LIVES] = game_state[MAX_LIVES]
            
            if game_state[CURRENT_LEVEL_INDEX] > len(game_state[LEVELS])-1:
                save_score(game_state, campaign_settings[game_state[LEVELS][game_state[CURRENT_LEVEL_INDEX]-1]]['CampaignShortName'])
                sys.exit(0)
            
            game_state[LEVELS] = campaign_settings.sections()
            game_state[LEVEL_NAME] = game_state[LEVELS][game_state[CURRENT_LEVEL_INDEX]]
            
            game_state[PLAYER_CUBE] = PlayerCube()
            
            game_state[PLAYER_CUBE_SPEED] = int(campaign_settings[game_state[LEVEL_NAME]]['GoodCubeSpeed'])
            
            if campaign_settings[game_state[LEVEL_NAME]]['KeepOnScreen'] == '1':
                game_state[SHOULD_KEEP_ON_SCREEN] = True
            else:
                game_state[SHOULD_KEEP_ON_SCREEN] = False
            
            game_state[BASE_BAD_CUBE_SPEED] = int(campaign_settings[game_state[LEVEL_NAME]]['StartSpeed'])
            game_state[SPEED_MODIFIER] = 0
            
            game_state[MAX_SPEED_MODIFIER] = int(campaign_settings[game_state[LEVEL_NAME]]['SpeedLevelsPerRound'])
            game_state[SECONDS_PER_LEVEL] = float(campaign_settings[game_state[LEVEL_NAME]]['SecondsPerLevel'])
            
            
            game_state[BAD_CUBE_SPAWN_RATE] = float(campaign_settings[game_state[LEVEL_NAME]]['SpawnRate'])
            
            
            max_hori_left_cubes = int(campaign_settings[game_state[LEVEL_NAME]]['MaxHoriLCubes'])
            max_hori_right_cubes = int(campaign_settings[game_state[LEVEL_NAME]]['MaxHoriRCubes'])
            
            max_verti_top_cubes = int(campaign_settings[game_state[LEVEL_NAME]]['MaxVertiTCubes'])
            max_verti_bottom_cubes = int(campaign_settings[game_state[LEVEL_NAME]]['MaxVertiBCubes'])
            
            max_dia_cubes = int(campaign_settings[game_state[LEVEL_NAME]]['MaxDiaCubes'])
            max_rock_cubes = int(campaign_settings[game_state[LEVEL_NAME]]['MaxRockCubes'])
            
            
            game_state[BAD_CUBE_MAXIMUMS] = {CUBE_TYPES[0]: max_hori_left_cubes,
                                             CUBE_TYPES[1]: max_hori_right_cubes,
                                             CUBE_TYPES[2]: max_verti_top_cubes,
                                             CUBE_TYPES[3]: max_verti_bottom_cubes,
                                             CUBE_TYPES[4]: max_dia_cubes, 
                                             CUBE_TYPES[5]: max_rock_cubes}
            
            game_state[BAD_CUBE_COUNTS] =  {CUBE_TYPES[0]: 0, CUBE_TYPES[1]: 0,
                                            CUBE_TYPES[2]: 0, CUBE_TYPES[3]: 0,
                                            CUBE_TYPES[4]: 0, CUBE_TYPES[5]: 0}
            
            game_state[BAD_CUBES] = []
            
            game_state[FRAME_COUNTER] = 0
        
            game_state[IS_NEW_ROUND] = False
            game_state[HAS_DIED] = False
        
        game_state[FRAME_COUNTER] += 1        
        
        if game_state[SPEED_MODIFIER] == game_state[MAX_SPEED_MODIFIER]:
            game_state[IS_NEW_ROUND] = True
            
        #Creates bad cubes
        if game_state[FRAME_COUNTER] % seconds_to_frames(game_config[FRAME_RATE], game_state[BAD_CUBE_SPAWN_RATE]) == 0:
            def is_all_maxed_out():
                for cube_type in CUBE_TYPES:
                    if game_state[BAD_CUBE_COUNTS][cube_type] < game_state[BAD_CUBE_MAXIMUMS][cube_type]:
                        return False
                    
                return True
            
            is_spawned = False
            
            while not is_spawned:
                cube_type_index = random.randint(0, 5)
                
                new_speed = game_state[BASE_BAD_CUBE_SPEED] + game_state[SPEED_MODIFIER]
                
                cube_name = CUBE_TYPES[cube_type_index]
                
                #Do nothing if every cube is maxed out
                if is_all_maxed_out():
                    is_spawned = True
                
                elif game_state[BAD_CUBE_COUNTS][cube_name] < game_state[BAD_CUBE_MAXIMUMS][cube_name]:
                    def get_new_bad_cube(bad_cube_counts):
                        if cube_name == CUBE_TYPES[0]:
                            bad_cube = HoriLeftCube(new_speed)
                            bad_cube_counts[cube_name] += 1
                        elif cube_name == CUBE_TYPES[1]:
                            bad_cube = HoriRightCube(new_speed)
                            bad_cube_counts[cube_name] += 1
                        elif cube_name == CUBE_TYPES[2]:
                            bad_cube = VertiTopCube(new_speed)
                            bad_cube_counts[cube_name] += 1
                        elif cube_name == CUBE_TYPES[3]:
                            bad_cube = VertiBotCube(new_speed)
                            bad_cube_counts[cube_name] += 1
                        elif cube_name == CUBE_TYPES[4]:
                            bad_cube = DiaCube(new_speed)
                            bad_cube_counts[cube_name] += 1
                        elif cube_name == CUBE_TYPES[5]:
                            bad_cube = RockCube()
                            bad_cube_counts[cube_name] += 1
                            
                        return bad_cube
                    
                    bad_cube = get_new_bad_cube(game_state[BAD_CUBE_COUNTS])
                    
                    if not game_state[PLAYER_CUBE].rect.inflate(game_config[SAFETY_ZONE_X],
                                                                game_config[SAFETY_ZONE_Y]).colliderect(bad_cube.rect):
                        game_state[BAD_CUBES].append(bad_cube)
                        is_spawned = True
        
        if game_state[FRAME_COUNTER] % seconds_to_frames(game_config[FRAME_RATE], game_state[SECONDS_PER_LEVEL]) == 0:
            game_state[SPEED_MODIFIER] += 1
        
        def detect_player_death(player_cube, bad_cubes):
            if len(bad_cubes) >= 1 and player_cube.rect.collidelist( [cube.rect for cube in bad_cubes] ) != -1:
                return True
            
            return False
            
        
        game_state[HAS_DIED] = detect_player_death(game_state[PLAYER_CUBE], game_state[BAD_CUBES])
        
        for event in pygame.event.get():
            def movement_input(player_cube, player_cube_speed):
                
                def set_x_and_y_speeds(player_cube, player_cube_speed):
                    #Controls movement
                    if pressed_keys[pygame.K_LEFT]:
                        player_cube.speed_x = -player_cube_speed
                        
                    elif pressed_keys[pygame.K_RIGHT]:
                        player_cube.speed_x = player_cube_speed
                    
                    else:
                        player_cube.speed_x = 0
                        
                    if pressed_keys[pygame.K_DOWN]:
                        player_cube.speed_y = player_cube_speed
                    
                    elif pressed_keys[pygame.K_UP]:
                        player_cube.speed_y = -player_cube_speed
                    else:
                        player_cube.speed_y = 0
                
                def normalize_diagonal_movement(player_cube):
                    #Keeps absolute speed constant-ish diagonal vs. straight
                    #TODO: Should be using Pythagor (sp?) theorem. (Only works well for
                    # multiples of 4 now
                    if player_cube.speed_x and player_cube.speed_y:
                        if player_cube.speed_x > 0:
                            player_cube.speed_x = player_cube.speed_x // 2 + player_cube.speed_x // 4
                        else:
                            player_cube.speed_x = player_cube.speed_x // 2 - ((-player_cube.speed_x) // 4)
                        
                        if player_cube.speed_y > 0:
                            player_cube.speed_y = player_cube.speed_y // 2 + player_cube.speed_y // 4
                        else:
                            player_cube.speed_y = player_cube.speed_y // 2 - ((-player_cube.speed_y) // 4)
        
                set_x_and_y_speeds(player_cube, player_cube_speed)
                normalize_diagonal_movement(player_cube)    
            
            pressed_keys = pygame.key.get_pressed()
            
            if event.type == pygame.QUIT or pressed_keys[pygame.K_ESCAPE]:
                sys.exit()
            
            #DEBUG: Fast Round Switch
            if game_config[CHEATS_ENABLED]:
                def change_round(round_number, by_how_much):
                    return (round_number + by_how_much, True, True, 999)
                
                if pressed_keys[pygame.K_PAGEUP]:
                    (game_state[CURRENT_LEVEL_INDEX], 
                     game_state[IS_NEW_ROUND], 
                     game_state[HAS_DIED], 
                     game_state[CURRENT_LIVES]) = change_round(game_state[CURRENT_LEVEL_INDEX], 1)
                
                elif pressed_keys[pygame.K_PAGEDOWN]:
                    (game_state[CURRENT_LEVEL_INDEX],
                     game_state[IS_NEW_ROUND],
                     game_state[HAS_DIED],
                     game_state[CURRENT_LIVES]) = change_round(game_state[CURRENT_LEVEL_INDEX], -1)
            
            movement_input(game_state[PLAYER_CUBE], game_state[PLAYER_CUBE_SPEED])
        
        
        game_state[PLAYER_CUBE].move()
        
        #Keeps good cube on screen
        game_state[PLAYER_CUBE].keep_on_screen()

        screen.fill(BLACK)
        
        def display_game_info_on_screen(game_state):
            score_display = game_config[FONT].render(str(game_state[CURRENT_SCORE]), True, WHITE)
            level_display = game_config[FONT].render("Level #" + str(game_state[CURRENT_LEVEL_INDEX] + 1) + ': ' + game_state[LEVEL_NAME], True, WHITE)
            lives_display = game_config[FONT].render("Lives: " + str(game_state[CURRENT_LIVES]), True, WHITE)
                
            screen.blit(score_display, (game_config[WIDTH] - score_display.get_width(),0 ))    
            screen.blit(level_display, (0,0))
            screen.blit(lives_display, (0,game_config[HEIGHT]-lives_display.get_height()))
        
        display_game_info_on_screen(game_state) 
        
        
        def paint_zone_areas(game_state):
            for (zone_name, zone_rect) in game_state[SCORE_ZONES]:
                pygame.draw.rect(screen, GRAY, zone_rect, 1)
                zone_name_display = game_config[FONT].render(zone_name, True, GRAY)
                screen.blit(zone_name_display, zone_rect.bottomleft)
        
        paint_zone_areas(game_state)
        
        def blit_cubes(game_state):
            def keep_or_remove_cubes():
                indices_to_delete = []
                for i in range(0, len(game_state[BAD_CUBES])):
                    game_state[BAD_CUBES][i].move()
                    
                    if game_state[BAD_CUBES][i].is_off_screen():
                        
                        if game_state[SHOULD_KEEP_ON_SCREEN]:
                            game_state[BAD_CUBES][i].keep_on_screen()
                        else:
                            indices_to_delete.append(i)
                    
                    screen.blit(game_state[BAD_CUBES][i].surface,
                                game_state[BAD_CUBES][i].rect)
                
                del_count = 0
                for index in indices_to_delete:
                    cube_to_delete = game_state[BAD_CUBES][index-del_count]
                    
                    if isinstance(cube_to_delete, HoriLeftCube):
                        game_state[BAD_CUBE_COUNTS][CUBE_TYPES[0]] -= 1
                    elif isinstance(cube_to_delete, HoriRightCube):
                        game_state[BAD_CUBE_COUNTS][CUBE_TYPES[1]] -= 1
                    elif isinstance(cube_to_delete, VertiTopCube):
                        game_state[BAD_CUBE_COUNTS][CUBE_TYPES[2]] -= 1
                    elif isinstance(cube_to_delete, VertiBotCube):
                        game_state[BAD_CUBE_COUNTS][CUBE_TYPES[3]] -= 1
                    elif isinstance(cube_to_delete, DiaCube):
                        game_state[BAD_CUBE_COUNTS][CUBE_TYPES[4]] -= 1
                    elif isinstance(cube_to_delete, RockCube):
                        game_state[BAD_CUBE_COUNTS][CUBE_TYPES[5]] -= 1
                    
                    del game_state[BAD_CUBES][index-del_count]
                    del_count += 1
            
            screen.blit(game_state[PLAYER_CUBE].surface, game_state[PLAYER_CUBE].rect)
            keep_or_remove_cubes()      
        
        blit_cubes(game_state)
        
        pygame.display.flip()
         
        game_state[GAME_CLOCK].tick(game_config[FRAME_RATE])
    
def seconds_to_frames(frame_rate, number_of_seconds):
    return int(number_of_seconds * frame_rate)

if __name__== "__main__":
        main()