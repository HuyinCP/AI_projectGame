import pygame as pg
import sys
from setting import *
from map import *
from object_renderer import *
from player import *
from raycasting import *


class Game:
    """
    Initializes the Game class, setting up the Pygame environment.

    This constructor initializes Pygame, sets the display mode using the
    resolution defined in the settings, and creates a clock object for
    managing the game's frame rate.
    """
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()

if __name__ == '__main__':
    game = Game()
        



