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

from thecubes import PlayerCube, HoriLeftCube, HoriRightCube, VertiTopCube
from thecubes import VertiBotCube, DiaCube, RockCube

import csv


CUBE_TYPES = ['HoriLeftCube', 'HoriRightCube', 'VertiTopCube',
              'VertiBotCube', 'DiaCube', 'RockCube']

WHITE = (255, 255, 255)
GRAY = (84, 84, 84)
BLACK = (0, 0, 0)

DIFFICULTY_LEVELS = ['Easy', 'Medium', 'Hard', 'Very Hard']

HIGHSCORE_FOLDER = 'highscores' + os.sep
HIGHSCORE_FILENAME = 'highscores.txt'


# game_state dictionary keys
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

IS_MENU = 'is_menu'
IS_MENU_LISTED = 'is_menu_listed'
CAMPAIGN_SETTINGS = 'campaign_settings'
CAMPAIGN_MENU_CHOICES = 'campaign_menu_choices'
CAMPAIGN_MENU_CHOICES_NAMES = 'campaign_menu_choices_names'

SCORE_ZONES = 'score_zones'

LEVELS = 'levels'

PLAYER_CUBE = 'player_cube'
PLAYER_CUBE_SPEED = 'player_cube_speed'
SHOULD_KEEP_ON_SCREEN = 'should_keep_on_screen'
BAD_CUBES = 'bad_cubes'    


# game_config dictionary keys
game_config = {}

WIDTH = 'width'
HEIGHT = 'height'
FRAME_RATE = 'frame_rate'
FONT_HUD = 'font_hud'
FONT_MENU = 'font_menu'

CHEATS_ENABLED = 'cheats_enabled'
SKIP_MENU = 'skip_menu'
SKIP_SOUNDS = 'skip_sounds'

SAFETY_ZONE_X = 'safety_zone_x'
SAFETY_ZONE_Y = 'safety_zone_y'

def seconds_to_frames(frame_rate, number_of_seconds):
    """Converts number_of_seconds to the equivalent number of frames."""
    return int(number_of_seconds * frame_rate)

def play_sound(settings, sound_name, repeat=1):
    """Stop the game loop and play a sound a certain number of times."""
    def seconds_to_ms(time_in_seconds):
        """Converts seconds to milliseconds"""
        return time_in_seconds * 1000
    
    pygame.mixer.music.stop()
    
    sound_folder = settings['sound']['FolderName'] + os.sep
    
    sound = pygame.mixer.Sound(sound_folder + settings['sound'][sound_name])
    sound.set_volume(float(settings['sound']['Volume']))
    
    for _ in range(0, repeat):
        sound.play()
        pygame.time.wait(int(seconds_to_ms(sound.get_length())))
    
    pygame.mixer.music.rewind()
    pygame.mixer.music.play(-1)

def add_points_to_score(game_state):
    zone_rects = [zone_rect for (_, zone_rect) in game_state[SCORE_ZONES]]
    zone_index = game_state[PLAYER_CUBE].rect.collidelist(zone_rects)
    if zone_index != -1:            
        if zone_index == 0:
            score_to_add = 7
        
        elif zone_index == 1:
            score_to_add = 3
            
        elif zone_index == 2:
            score_to_add = 1
        
        game_state[CURRENT_SCORE] += score_to_add
        
def save_score(game_state, campaign_settings):
    """Saves player's score to a .txt file according to the name and
    short name of the campaign being played."""
    campaign_name = campaign_settings[game_state[LEVEL_NAME]]['CampaignName']
    campaign_short_name = campaign_settings[game_state[LEVEL_NAME]]['CampaignShortName']
    
    high_score_filename = HIGHSCORE_FOLDER + campaign_short_name
    high_score_filename += '_' + HIGHSCORE_FILENAME
    
    # Add new score
    with open(high_score_filename, 'a', newline='') as csvfile:
        high_score_writer = csv.writer(csvfile, delimiter=' ',
                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
        
        score_str = str(game_state[CURRENT_SCORE])
        
        level_str = "Level #" + str(game_state[CURRENT_LEVEL_INDEX] + 1) 
        level_str += " - " + game_state[LEVEL_NAME]
        
        high_score = [score_str, level_str]
        high_score_writer.writerow(high_score)
    
    # Sort scores
    with open(high_score_filename, newline='') as csvfile:
        high_score_reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        
        high_scores = list(high_score_reader)
        
        # removes campaign title if there
        high_scores = [score for score in high_scores if len(score) != 1]
        
        high_scores.sort(key=lambda row: int(row[0]), reverse=True)
    
    # Write new sorted scores
    with open(high_score_filename, 'w', newline='') as csvfile:
        high_score_writer = csv.writer(csvfile, delimiter=' ',
                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
        
        high_score_writer.writerow([campaign_name])
        for high_score in high_scores:
            high_score_writer.writerow(high_score)

def is_all_maxed_out(bad_cube_counts, bad_cube_maximums):
    """Determines whether all the cubes of each type are at their maximum 
    amounts."""
    for cube_type in CUBE_TYPES:
        if bad_cube_counts[cube_type] < bad_cube_maximums[cube_type]:
            return False
        
    return True

def change_level(game_state, game_config, settings):
    campaign_settings = game_state[CAMPAIGN_SETTINGS]
    
    if not game_state[HAS_DIED] and game_state[CURRENT_LEVEL_INDEX] != -1:
        if not game_config[SKIP_SOUNDS]:
            play_sound(settings, 'NextRound', repeat=1)
        
        game_state[CURRENT_LEVEL_INDEX] += 1
        game_state[CURRENT_LIVES] += 1 
        
    if game_state[CURRENT_LEVEL_INDEX] == -1 and not game_state[IS_MENU]:
        game_state[CURRENT_LEVEL_INDEX] += 1                     
        
    if game_state[HAS_DIED]: 
        if not game_config[SKIP_SOUNDS]:               
            play_sound(settings, 'Loss', repeat=1)
        
        if game_state[CURRENT_LEVEL_INDEX] == 0 and game_state[CURRENT_LIVES] == game_state[MAX_LIVES]:
            if not game_config[CHEATS_ENABLED]:
                save_score(game_state, campaign_settings)
            
            game_state[CURRENT_SCORE] = 0
            
        if game_state[CURRENT_LEVEL_INDEX] != 0:
            game_state[CURRENT_LIVES] -= 1
            
        if game_state[CURRENT_LIVES] == 0:
            if not game_config[CHEATS_ENABLED]:
                save_score(game_state, campaign_settings)
            
            game_state[CURRENT_LEVEL_INDEX] = 0
            game_state[CURRENT_SCORE] = 0
            game_state[CURRENT_LIVES] = game_state[MAX_LIVES]
    
    # Player has beaten all levels in a campaign
    if game_state[CURRENT_LEVEL_INDEX] > len(game_state[LEVELS]) - 1:
        if not game_config[CHEATS_ENABLED]:
            play_sound(settings, 'NextRound', repeat=3)
            save_score(game_state, campaign_settings)
        sys.exit(0)
    
    game_state[LEVELS] = campaign_settings.sections()
    game_state[LEVEL_NAME] = game_state[LEVELS][game_state[CURRENT_LEVEL_INDEX]]
        
    game_state[SPEED_MODIFIER] = 0
    game_state[BAD_CUBES] = []
    game_state[FRAME_COUNTER] = 0
    game_state[IS_NEW_ROUND] = False
    game_state[HAS_DIED] = False
    
    game_state[PLAYER_CUBE] = PlayerCube()
    
    game_state[PLAYER_CUBE_SPEED] = int(campaign_settings[game_state[LEVEL_NAME]]['GoodCubeSpeed'])
    
    if campaign_settings[game_state[LEVEL_NAME]]['KeepOnScreen'] == '1':
        game_state[SHOULD_KEEP_ON_SCREEN] = True
    else:
        game_state[SHOULD_KEEP_ON_SCREEN] = False
    
    game_state[BASE_BAD_CUBE_SPEED] = int(campaign_settings[game_state[LEVEL_NAME]]['StartSpeed'])
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
    
    game_state[BAD_CUBE_COUNTS] = {CUBE_TYPES[0]: 0, CUBE_TYPES[1]: 0,
                                    CUBE_TYPES[2]: 0, CUBE_TYPES[3]: 0,
                                    CUBE_TYPES[4]: 0, CUBE_TYPES[5]: 0}

def spawn_new_bad_cube(game_state, game_config):
    is_spawned = False    
    while not is_spawned:
        cube_type_index = random.randint(0, 5)
        
        new_speed = game_state[BASE_BAD_CUBE_SPEED] + game_state[SPEED_MODIFIER]
        
        cube_name = CUBE_TYPES[cube_type_index]
        
        # Do nothing if every cube is maxed out
        if is_all_maxed_out(game_state[BAD_CUBE_COUNTS], game_state[BAD_CUBE_MAXIMUMS]):
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


def has_player_died(player_cube, bad_cubes):
    """
    Determines whether the player cube has collided with any of the bad 
    cubes.
    """
    are_there_cubes = len(bad_cubes) >= 1
    
    bad_cubes_rects = [cube.rect for cube in bad_cubes]
    does_player_collide = player_cube.rect.collidelist(bad_cubes_rects) != -1
    
    if are_there_cubes and does_player_collide:
        return True
    
    return False

def cheats_input(pressed_keys, game_state):
    """Changes levels when certain keys are pressed."""
    is_cheating = False
    if pressed_keys[pygame.K_PAGEUP]:
        is_cheating = True
        game_state[CURRENT_LEVEL_INDEX] += 1 
    
    elif pressed_keys[pygame.K_PAGEDOWN]:
        game_state[CURRENT_LEVEL_INDEX] -= 1
        is_cheating = True
    
    if is_cheating:
        game_state[IS_NEW_ROUND] = True
        game_state[HAS_DIED] = True
        game_state[CURRENT_LIVES] = 9999
        game_state[CURRENT_SCORE] = 0
         

def movement_input(pressed_keys, player_cube, player_cube_speed):
    """
        Converts user input on keyboard into movement of player_cube on 
        screen.
    """
    
    def set_x_and_y_speeds(player_cube, player_cube_speed):
        """
            Sets x and y speeds of player_cube depending on which keys are 
            pressed.
        """
        # Controls movement
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
        """
            Alters x and y speeds of player_cube to normalize (equal in speed 
            to non-diagonal movement) diagonal movement.
        """
        # Keeps absolute speed constant-ish diagonal vs. straight
        # TODO: Should be using Pythagor (sp?) theorem. (Only works well for
        # multiples of 4 now
        if player_cube.speed_x and player_cube.speed_y:
            x_speed = player_cube.speed_x
            y_speed = player_cube.speed_y
            
            if player_cube.speed_x > 0:
                player_cube.speed_x = x_speed // 2 + x_speed // 4
            else:
                player_cube.speed_x = x_speed // 2 - ((-x_speed) // 4)
            
            if player_cube.speed_y > 0:
                player_cube.speed_y = y_speed // 2 + y_speed // 4
            else:
                player_cube.speed_y = y_speed // 2 - ((-y_speed) // 4)
    
    set_x_and_y_speeds(player_cube, player_cube_speed)
    normalize_diagonal_movement(player_cube) 


def display_game_info_on_screen(screen, game_state, game_config):
    """Display current score, level name and lives onto screen."""
    score_display = game_config[FONT_HUD].render(str(game_state[CURRENT_SCORE]),
                                             True, WHITE)
    screen.blit(score_display,
                (game_config[WIDTH] - score_display.get_width(), 0))
    
    level_str = "Level #" + str(game_state[CURRENT_LEVEL_INDEX] + 1)
    level_str += ': ' + game_state[LEVEL_NAME]
    level_display = game_config[FONT_HUD].render(level_str, True, WHITE)
    screen.blit(level_display, (0, 0))
    
    lives_str = "Lives: " + str(game_state[CURRENT_LIVES])
    lives_display = game_config[FONT_HUD].render(lives_str, True, WHITE)    
    screen.blit(lives_display,
                (0, game_config[HEIGHT] - lives_display.get_height()))        

def draw_campaign_choices(screen, game_state, game_config):
    vertical_offset = 0
    for (menu_surface, menu_rect) in game_state[CAMPAIGN_MENU_CHOICES]:
        screen.blit(menu_surface, menu_rect)
        vertical_offset += menu_surface.get_height() + 10


def draw_score_zone_areas(screen, score_zones, font):
    """Draws score_zones areas onto screen."""
    for (zone_name, zone_rect) in score_zones:
        pygame.draw.rect(screen, GRAY, zone_rect, 1)
        zone_name_display = font.render(zone_name, True, GRAY)
        screen.blit(zone_name_display, zone_rect.bottomleft)

def move_cubes(screen, player_cube, bad_cubes, should_keep_on_screen, bad_cube_counts):
    """
        Move player_cube and all cubes in bad_cubes and keep them on screen.
        
        Unless should_keep_on_screen is False, in which case, delete the bad 
        cubes which move off screen and decrement their count in bad_cube_counts.
    """
    
    player_cube.move()
    player_cube.keep_on_screen()
        
    indices_to_delete = []
    for i in range(0, len(bad_cubes)):
        bad_cubes[i].move()
        
        if bad_cubes[i].is_off_screen():
            
            if should_keep_on_screen:
                bad_cubes[i].keep_on_screen()
            else:
                indices_to_delete.append(i)
    
    del_count = 0
    for index in indices_to_delete:
        cube_to_delete = bad_cubes[index - del_count]
        
        if isinstance(cube_to_delete, HoriLeftCube):
            bad_cube_counts[CUBE_TYPES[0]] -= 1
        elif isinstance(cube_to_delete, HoriRightCube):
            bad_cube_counts[CUBE_TYPES[1]] -= 1
        elif isinstance(cube_to_delete, VertiTopCube):
            bad_cube_counts[CUBE_TYPES[2]] -= 1
        elif isinstance(cube_to_delete, VertiBotCube):
            bad_cube_counts[CUBE_TYPES[3]] -= 1
        elif isinstance(cube_to_delete, DiaCube):
            bad_cube_counts[CUBE_TYPES[4]] -= 1
        elif isinstance(cube_to_delete, RockCube):
            bad_cube_counts[CUBE_TYPES[5]] -= 1
        
        del bad_cubes[index - del_count]
        del_count += 1

def draw_cubes(screen, player_cube, bad_cubes):
    """Draw player_cube and all cubes in bad_cubes onto screen."""
    screen.blit(player_cube.surface, player_cube.rect)
    
    for bad_cube in bad_cubes:
        screen.blit(bad_cube.surface, bad_cube.rect)

def build_campaign_menu_choices(game_state, game_config):
    
    def get_key_by_difficulty(difficulty_levels, difficulty):
        if difficulty in difficulty_levels:
            return DIFFICULTY_LEVELS.index(difficulty)
        else:
            return -1

    game_state[CAMPAIGN_MENU_CHOICES_NAMES] = []

    for files in os.listdir('campaigns' + os.sep):
        if files.endswith(".ini"):
            campaign_info = configparser.ConfigParser()
            campaign_info.read('campaigns' + os.sep + files)
            
            campaign = (files, campaign_info['DEFAULT']['CampaignName'], campaign_info['DEFAULT']['Difficulty'])
            game_state[CAMPAIGN_MENU_CHOICES_NAMES].append(campaign)
    
    game_state[CAMPAIGN_MENU_CHOICES_NAMES].sort(key=lambda x: get_key_by_difficulty(DIFFICULTY_LEVELS, x[2]))     
    
    count = 0
    multiplier = -1
    absolute_offset = 0
    vertical_offsets = []
    for _ in range(0, len(game_state[CAMPAIGN_MENU_CHOICES_NAMES])):
        vertical_offsets.append(absolute_offset * multiplier)
        
        multiplier *= -1
        
        if count % 2 != 1 or count == 0:
            absolute_offset += 50
            
        count += 1
    
    vertical_offsets.sort()
    
    game_state[CAMPAIGN_MENU_CHOICES] = []
    i = 0
    for offset in vertical_offsets:
        (_, campaign_name, difficulty ) = game_state[CAMPAIGN_MENU_CHOICES_NAMES][i]
        campaign_display = game_config[FONT_MENU].render(campaign_name + ' (' + difficulty + ')', True, WHITE)
        
        campaign_display_rect = campaign_display.get_rect()
        
        x_value = game_config[WIDTH] // 2
        y_value = game_config[HEIGHT] // 2 + offset
        
        campaign_display_rect.center = (x_value, y_value)
        
        campaign_option = (campaign_display, campaign_display_rect)
        game_state[CAMPAIGN_MENU_CHOICES].append(campaign_option)
        
        i += 1
      
    game_state[IS_MENU_LISTED] = True

def main():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        
    settings = configparser.ConfigParser()
    settings.read('config' + os.sep + 'settings.ini')
    
    
    game_state = {}
    game_config = {}
    
    if settings['gameplay']['CheatsEnabled'] == '1':
        game_config[CHEATS_ENABLED] = True
    else:
        game_config[CHEATS_ENABLED] = False
    
    if settings['gameplay']['SkipMenu'] == '1':
        game_state[IS_MENU] = False
    else:
        game_state[IS_MENU] = True
    
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
    
    game_config[FONT_HUD] = pygame.font.SysFont("comicsansms", 12)
    game_config[FONT_MENU] = pygame.font.SysFont("comicsansms", 30)
    
    theme_path = settings['sound']['FolderName'] + os.sep
    theme_path += settings['sound']['Theme']
    pygame.mixer.music.load(theme_path)
    pygame.mixer.music.set_volume(float(settings['sound']['Volume']))
    
    pygame.mixer.music.play(loops= -1)
    

    screen = pygame.display.set_mode((game_config[WIDTH], game_config[HEIGHT]))
    
    pygame.display.set_caption("InfiniCube v0.8")
    
    game_state[PLAYER_CUBE] = PlayerCube()
    
    game_state[GAME_CLOCK] = pygame.time.Clock()
    
    game_state[CAMPAIGN_SETTINGS] = configparser.ConfigParser()
    campaign_path = 'campaigns' + os.sep
    campaign_path += settings['gameplay']['CampaignFilename']
    game_state[CAMPAIGN_SETTINGS].read(campaign_path)
    
    game_state[LEVELS] = game_state[CAMPAIGN_SETTINGS].sections()
    
    game_state[MAX_LIVES] = int(game_state[CAMPAIGN_SETTINGS]['DEFAULT']['NumberOfLives'])
    game_state[CURRENT_LIVES] = game_state[MAX_LIVES]
    
    
    # Build score zones
    score_zone_A = pygame.Rect((0, 0), (int(game_config[WIDTH] // 4 * 1.5),
                                         int(game_config[HEIGHT] // 4 * 1.5)))
    
    score_zone_B = pygame.Rect((0, 0), (int(game_config[WIDTH] // 2 * 1.5),
                                         int(game_config[HEIGHT] // 2 * 1.5)))
    
    score_zone_C = pygame.Rect((0, 0), (game_config[WIDTH],
                                        game_config[HEIGHT]))
    
    game_state[SCORE_ZONES] = [('A', score_zone_A), ('B', score_zone_B),
                                ('C', score_zone_C)]
    
    for (_, score_zone) in game_state[SCORE_ZONES]:
        score_zone.center = (game_config[WIDTH] // 2, game_config[HEIGHT] // 2)
    
    
    game_state[CURRENT_SCORE] = 0
    game_state[CURRENT_LEVEL_INDEX] = -1
    game_state[IS_NEW_ROUND] = True
    game_state[HAS_DIED] = False
    
    game_state[IS_MENU_LISTED] = False
    while True:
        if game_state[IS_MENU]:
            if not game_state[IS_MENU_LISTED]:
                build_campaign_menu_choices(game_state, game_config)
        
        # Changes level if needed and resets score, lives, ... if needed
        if game_state[IS_NEW_ROUND] or game_state[HAS_DIED]:
            change_level(game_state, game_config, settings)
            
        if not game_state[IS_MENU]:
            add_points_to_score(game_state)
            
            game_state[FRAME_COUNTER] += 1        
            
            if game_state[SPEED_MODIFIER] == game_state[MAX_SPEED_MODIFIER]:
                game_state[IS_NEW_ROUND] = True
                
            # Spawn new bad cubes
            if game_state[FRAME_COUNTER] % seconds_to_frames(game_config[FRAME_RATE], game_state[BAD_CUBE_SPAWN_RATE]) == 0:            
                spawn_new_bad_cube(game_state, game_config)
            
            if game_state[FRAME_COUNTER] % seconds_to_frames(game_config[FRAME_RATE], game_state[SECONDS_PER_LEVEL]) == 0:
                game_state[SPEED_MODIFIER] += 1            
            
            
            game_state[HAS_DIED] = has_player_died(game_state[PLAYER_CUBE], game_state[BAD_CUBES])
        
        
        for event in pygame.event.get():            
            pressed_keys = pygame.key.get_pressed()
            
            if event.type == pygame.QUIT or pressed_keys[pygame.K_ESCAPE]:
                sys.exit()
            
            # Select campaign
            if game_state[IS_MENU] and (pressed_keys[pygame.K_SPACE] or pressed_keys[pygame.K_RETURN]):
                menu_option_rects = [rect for (_, rect) in game_state[CAMPAIGN_MENU_CHOICES]]
                choice_index = game_state[PLAYER_CUBE].rect.collidelist(menu_option_rects)
                if choice_index != -1:
                    game_state[CAMPAIGN_SETTINGS] = configparser.ConfigParser()
                    game_state[CAMPAIGN_SETTINGS].read('campaigns' + os.sep + game_state[CAMPAIGN_MENU_CHOICES_NAMES][choice_index][0])
                    game_state[IS_MENU] = False
                    change_level(game_state, game_config, settings)
            
            if not game_state[IS_MENU] and pressed_keys[pygame.K_BACKSPACE]:
                save_score(game_state, game_state[CAMPAIGN_SETTINGS])
                play_sound(settings, 'Loss')
                
                game_state[IS_MENU] = True
                game_state[CURRENT_SCORE] = 0
                game_state[CURRENT_LEVEL_INDEX] = -1
                game_state[IS_NEW_ROUND] = True
                game_state[HAS_DIED] = False

            # DEBUG: Fast Round Switch
            if game_config[CHEATS_ENABLED] and not game_state[IS_MENU]:
                cheats_input(pressed_keys, game_state)
            
            movement_input(pressed_keys,
                           game_state[PLAYER_CUBE], game_state[PLAYER_CUBE_SPEED])
        

        screen.fill(BLACK)
        
        if not game_state[IS_MENU]:
            display_game_info_on_screen(screen, game_state, game_config)
            draw_score_zone_areas(screen, game_state[SCORE_ZONES], game_config[FONT_HUD])
        
        if game_state[IS_MENU]:
            draw_campaign_choices(screen, game_state, game_config)
        
        move_cubes(screen, game_state[PLAYER_CUBE], game_state[BAD_CUBES],
                   game_state[SHOULD_KEEP_ON_SCREEN], game_state[BAD_CUBE_COUNTS])
        
        draw_cubes(screen, game_state[PLAYER_CUBE], game_state[BAD_CUBES])
        
        pygame.display.flip()
         
        game_state[GAME_CLOCK].tick(game_config[FRAME_RATE])

if __name__ == "__main__":
        main()
