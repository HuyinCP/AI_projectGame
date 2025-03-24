from main import *
import pygame as pg
_ = False
mini_map = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 2, 2, _, 1],
    [1, _, 2, _, _, _, _, _, _, _, _, 2, _, 2, _, 2, 2, _, 1],
    [1, _, 2, _, _, 2, _, _, _, _, _, 2, _, 2, _, 2, 2, _, 1],
    [1, _, 2, _, _, 2, _, _, _, _, _, 2, _, 2, _, 2, 2, _, 1],
    [1, _, _, _, 2, _, _, _, _, _, _, 2, _, 2, _, 2, 2, _, 1],
    [1, _, _, _, 2, 2, _, _, 2, 2, 2, 2, _, 2, 2, 2, 2, _, 1],
    [1, _, _, _, _, _, _, _, 2, _, _, _, _, _, _, _, _, _, 1],
    [1, _, _, _, _, 2, _, _, _, _, _, _, _, _, _, _, _, _, 3],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]
class Map:
    def __init__(self, game):
        self.game = game
        self.mini_map = mini_map
        #tọa độ dạng tuple (x, y)
        self.world_map = {}
        self.get_map()

    def get_map(self):
        self.world_map = {}
        for j, rows in enumerate(mini_map):
            for i, val in enumerate(rows):
                if val in [1, 2, 3]:
                    self.world_map[(i, j)] = val

    def draw(self):
        # Rect(left, top, width, height) -> Rect
        # Rect((left, top), (width, height)) -> Rect
        # Rect(object) -> Rect
        for pos in self.world_map:
            pg.draw.rect(self.game.screen, 'darkgray', (pos[0] * 100, pos[1] * 100, 100, 100), 2)

    