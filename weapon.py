import pygame as pg
from setting import *

class Weapon:
    def __init__(self, game, path='resources/sprites/weapon/shotgun/0.png', scale=0.4):
        self.game = game
        # Tải hình ảnh súng
        self.image = pg.image.load(path).convert_alpha()
        # Điều chỉnh kích thước hình ảnh
        self.image = pg.transform.smoothscale(
            self.image, 
            (self.image.get_width() * scale, self.image.get_height() * scale)
        )
        # Tính vị trí để đặt súng (giữa dưới màn hình)
        self.weapon_pos = (HALF_WIDTH - self.image.get_width() // 2, HEIGHT - self.image.get_height())

    def draw(self):
        # Vẽ hình ảnh súng lên màn hình tại vị trí đã tính
        self.game.screen.blit(self.image, self.weapon_pos)

    def update(self):
        # Không cần xử lý hoạt hình, để trống hoặc có thể thêm logic khác sau này
        pass