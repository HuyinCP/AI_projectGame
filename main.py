import pygame as pg
import sys
from setting import *
from map import *
from object_renderer import *
from player import *
from raycasting import *
from player import *
from weapon import *
from sprite_objects import *
from map import *
from object_handler import *
from sound import *

class Game:
    def __init__(self):
        #khởi tạo tất cả modul của Pygame
        pg.init() 
        pg.mouse.set_visible(False)
    
        #tạo cửa sổ hiển thị với kích thước là RES
        self.screen = pg.display.set_mode(RES) 
        
         #theo dõi tốc độ khungn hình FPS
        self.clock = pg.time.Clock()

        #Lưu trữ thời gian trôi qua giữa các Frame
        self.delta_time = 1 

        # self.weapon = Weapon(self)

        #gọi hàm new_game để khởi tạo các đối tượng nhân vật, bản đồ, hoặc là npc ...
        self.new_game() 
    
    def new_game(self):
        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = Raycasting(self)
        # self.static_sprite = SpriteObject(self)
        # self.animated_sprite = AnimatedSprite(self)
        self.object_handler = ObjectHandler(self)
        self.weapon = Weapon(self)
        self.sound = Sound(self)

    def update(self):   
        #cập nhật trạng thái của đối tượng Player
        self.player.update() 
        self.raycasting.update()
        # self.static_sprite.update()
        # self.animated_sprite.update()
        self.object_handler.update()
        self.weapon.update()
        #cập nhật toàn bộ khung hình game
        pg.display.flip() 

        # self.weapon.update()
        #kiểm soát tốc độ khug hình theo giá trị FPS
        self.delta_time = self.clock.tick(FPS) 
        
        pg.display.set_caption(f'{self.clock.get_fps() :.1f}')
        # pg.display.set_caption("AI Game")
    
    def draw(self):
        self.screen.fill('black')
        # self.object_renderer.draw()
        # self.weapon.draw()
        # self.weapon.draw()
        self.map.draw() #vẽ map 2D
        self.player.draw() #vẽ chấm xanh người chơi

    def check_event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE) :
                pg.quit()
                sys.exit()
            self.player.single_fire_event(event)

    def run(self):
        while True:
            self.check_event()
            self.update()
            self.draw()

    


if __name__ == '__main__':
    game = Game()
    game.run()




