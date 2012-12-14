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


class Cube(object):
    """Represents a graphical Cube."""

    def __init__(self, filename, speed=[0,0]):
        """Initializes a Cube."""
        (self._surface, self._rect) = load_image(filename)
        self._speed = speed
    
    @property
    def surface(self):
        return self._surface
    
    @property
    def rect(self):
        return self._rect
    
    @rect.setter
    def rect(self, new_rect):
        self._rect = new_rect

    @property
    def speed(self):
        return self._speed
    
    @speed.setter
    def speed(self, x_y_list):
        self._speed = x_y_list

def load_image(filename):
    image = pygame.image.load(filename).convert()
    imagerect = image.get_rect()
    
    return (image, imagerect)