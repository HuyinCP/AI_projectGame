import pygame as pg
from raycasting import *
from setting import *

class ObjectRenderer:
    # Phương thức khởi tạo, được gọi khi tạo một đối tượng ObjectRenderer
    def __init__(self, game):
        # Lưu đối tượng game (chứa các thành phần như màn hình, raycasting, v.v.) vào thuộc tính self.game
        self.game = game
        # Lấy bề mặt màn hình (Pygame Surface) từ game.screen để vẽ lên màn hình
        self.screen = game.screen
        # Tải các texture (hình ảnh) của bức tường và lưu vào self.wall_textures
        self.wall_textures = self.load_wall_textures()
        self.sky_image = self.get_texture(r"resources\textures\sky3.png", (WIDTH, HALF_HEIGHT))
        self.sky_offset = 0

    # Phương thức chính để vẽ tất cả các đối tượng trong mỗi khung hình
    def draw(self):
        # Gọi phương thức render_game_object để thực hiện việc vẽ
        self.draw_backgroud()
        self.render_game_object()

    def draw_backgroud(self):
        self.sky_offset = (self.sky_offset + 4.5 * self.game.player.rel) % WIDTH
        self.screen.blit(self.sky_image, (-self.sky_offset, 0))
        self.screen.blit(self.sky_image, (-self.sky_offset + WIDTH, 0))
        #floor 
        pg.draw.rect(self.screen, FLOOR_COLOR, (0, HALF_HEIGHT, WIDTH, HEIGHT))

    # Phương thức để vẽ các đối tượng (như bức tường) lên màn hình
    def render_game_object(self):
        # Lấy danh sách các đối tượng cần vẽ từ Raycasting (self.game.raycasting.objects_to_render)
        # Mỗi đối tượng là một tuple (depth, image, pos)
        list_objects = self.game.raycasting.objects_to_render
        for depth, image, pos in list_objects:
            # Vẽ hình ảnh (image) lên màn hình tại vị trí pos (tọa độ x, y)
            # depth là khoảng cách, image là cột texture, pos là vị trí trên màn hình
            self.screen.blit(image, pos)
    #
    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        # Tải hình ảnh từ đường dẫn path và chuyển đổi để hỗ trợ độ trong suốt (alpha channel)
        texture = pg.image.load(path).convert_alpha()
        # Điều chỉnh kích thước của texture thànres (mặc định là TEXTURE_SIZE x TEXTURE_SIZE)
        # Sau đó trả về texture đã được thay đổi kích thước
        return pg.transform.scale(texture, res)
    
    # Phương thức để tải các texture của bức tường và lưu vào một dictionary
    def load_wall_textures(self):
        # Trả về một dictionary với các cặp key-value:
        # - Key: Số nguyên (1, 2, 3,...) đại diện cho loại bức tường
        # - Value: Texture (hình ảnh) tương ứng, được tải bằng get_texture
        return {
            1: self.get_texture(r'resources\textures\1.png'),
            2: self.get_texture(r'resources\textures\2.png'),
            3: self.get_texture(r'resources\textures\3.png'),
            4: self.get_texture(r'resources\textures\4.png'),
            5: self.get_texture(r'resources\textures\5.png'),
        }