import pygame as pg
from settings import *


class ObjectRenderer:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.wall_textures = self.load_wall_textures()
        self.sky_image = self.get_texture('resources/textures/sky.png', (WIDTH, HALF_HEIGHT))
        self.sky_offset = 0
        self.blood_screen = self.get_texture('resources/textures/blood_screen.png', RES)
        self.digit_size = 90
        self.digit_images = [self.get_texture(f'resources/textures/digits/{i}.png', [self.digit_size] * 2)
                             for i in range(11)]
        self.digits = dict(zip(map(str, range(11)), self.digit_images))
        self.game_over_image = self.get_texture('resources/textures/game_over.png', RES)
        self.win_image = self.get_texture('resources/textures/win.png', RES)

    def draw(self):
        self.draw_background()
        self.render_game_objects()
        self.draw_player_health()

    def win(self):
        self.screen.blit(self.win_image, (0, 0))

    def game_over(self):
        self.screen.blit(self.game_over_image, (0, 0))

    def draw_player_health(self):
        health = str(self.game.player.health)
        for i, char in enumerate(health):
            self.screen.blit(self.digits[char], (i * self.digit_size, 0))
        self.screen.blit(self.digits['10'], ((i + 1) * self.digit_size, 0))

    def player_damage(self):
        self.screen.blit(self.blood_screen, (0, 0))

    def draw_background(self):
        self.sky_offset = (self.sky_offset + 4.5 * self.game.player.rel) % WIDTH
        self.screen.blit(self.sky_image, (-self.sky_offset, 0))
        self.screen.blit(self.sky_image, (-self.sky_offset + WIDTH, 0))
        # floor
        pg.draw.rect(self.screen, FLOOR_COLOR, (0, HALF_HEIGHT, WIDTH, HEIGHT))

    def render_game_objects(self):
        list_objects = sorted(self.game.raycasting.objects_to_render, key=lambda t: t[0], reverse=True)
        for depth, image, pos in list_objects:
            self.screen.blit(image, pos)

    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)

    def load_wall_textures(self):
        return {
            1: self.get_texture('resources/textures/1.png'),
            2: self.get_texture('resources/textures/2.png'),
            3: self.get_texture('resources/textures/3.png'),
            4: self.get_texture('resources/textures/4.png'),
            5: self.get_texture('resources/textures/5.png'),
        }
    
    def draw_minimap(self):
        # Mini-map settings
        map_scale = 5  # Scale factor for the mini-map
        map_size = 150  # Size of the mini-map
        map_offset = 50  # Offset from the top-left corner
        player_color = (0, 255, 0)  # Green for player
        npc_color = (255, 0, 0)  # Red for NPCs
        wall_color = (255, 255, 255)  # White for walls
        health_color = (255, 255, 0)

        # Draw the mini-map background
        pg.draw.rect(self.game.screen, (0, 0, 0), (map_offset, map_offset, map_size, map_size))

        # Draw walls
        for x, y in self.game.map.world_map:
            rect = (map_offset + x * map_scale, map_offset + y * map_scale, map_scale, map_scale)
            pg.draw.rect(self.game.screen, wall_color, rect)

                # Draw health points
        for hp in self.game.map.health_points:
            x, y = hp
            rect = (map_offset + x * map_scale, map_offset + y * map_scale, map_scale, map_scale)
            pg.draw.rect(self.game.screen, health_color, rect)
        # Draw NPCs
        for npc in self.game.object_handler.npc_list:
            if npc.alive:
                rect = (map_offset + npc.x * map_scale, map_offset + npc.y * map_scale, map_scale, map_scale)
                pg.draw.rect(self.game.screen, npc_color, rect)

        # Draw player
        player_x, player_y = self.game.player.x, self.game.player.y
        player_rect = (map_offset + player_x * map_scale, map_offset + player_y * map_scale, map_scale, map_scale)
        pg.draw.rect(self.game.screen, player_color, player_rect)