import pygame as pg
from math import *
from setting import*
from object_renderer import *

# Class Raycasting: Thực hiện thuật toán raycasting để tạo hiệu ứng 3D giả lập
# - Bắn các tia (rays) từ góc nhìn của người chơi
# - Xác định khoảng cách đến bức tường gần nhất
# - Tính chiều cao của bức tường trên màn hình
# - Chuẩn bị dữ liệu để vẽ các cột tường, chuyển từ 2D sang 3D

class Raycasting:
    def __init__(self, game):
        """Phương thức khởi tạo, được gọi khi tạo một đối tượng Raycasting"""
        # Lưu đối tượng game (chứa các thành phần như người chơi, bản đồ, v.v.) vào thuộc tính self.game
        self.game = game
        # Khởi tạo danh sách rỗng để lưu kết quả raycasting cho từng tia
        # Mỗi phần tử trong danh sách sẽ chứa thông tin: (depth, project_height, texture, offset)
        # - depth: Khoảng cách từ người chơi đến bức tường mà tia chạm vào
        # - project_height: Chiều cao dự kiến của bức tường trên màn hình
        # - texture: Loại texture (hình ảnh) của bức tường mà tia chạm vào
        # - offset: Giá trị offset để xác định phần nào của texture sẽ được vẽ
        self.ray_casting_result = [] 

        # Khởi tạo danh sách rỗng để lưu các đối tượng cần vẽ (dùng bởi ObjectRenderer)
        # Mỗi phần tử sẽ chứa thông tin: (depth, image, pos)
        # - depth: Khoảng cách (dùng để sắp xếp khi vẽ)
        # - image: Cột texture đã được xử lý
        # - pos: Vị trí trên màn hình để vẽ
        self.objects_to_render = []

        # Lấy dictionary chứa các texture của bức tường từ ObjectRenderer
        # self.textures là một dictionary với key là loại tường (1, 2, 3,...) và value là texture
        self.textures = self.game.object_renderer.wall_textures
    

    def get_object_to_rander(self):
        """Phương thức để tạo danh sách các đối tượng cần vẽ (self.objects_to_render) từ kết quả raycasting"""
        self.objects_to_render = [] # Xóa danh sách objects_to_render cũ để chuẩn bị cho dữ liệu mới
        for ray, value in enumerate(self.ray_casting_result):   
            # Giải nén tuple (depth, project_height, texture, offset) từ kết quả raycasting
            depth, project_height, texture, offset = value
            
            if project_height < HEIGHT:
                # Lấy một cột pixel từ texture dựa trên offset
                # - offset * (TEXTURE_SIZE - SCALE): Tính vị trí x trên texture (theo pixel)
                # - subsurface: Lấy một phần của texture (cột rộng SCALE pixel, cao TEXTURE_SIZE pixel)
                wall_column = self.textures[texture].subsurface(
                    offset * (TEXTURE_SIZE - SCALE), 0 , SCALE, TEXTURE_SIZE
                )
                
                # Điều chỉnh kích thước cột texture để phù hợp với chiều cao của bức tường trên màn hình
                # - SCALE: Chiều rộng của cột
                # - project_height: Chiều cao của cột
                wall_column = pg.transform.scale(wall_column, (SCALE, project_height))

                # Tính vị trí trên màn hình để vẽ cột tường
                # - ray * SCALE: Tọa độ x (mỗi tia tương ứng với một cột trên màn hình)
                # - HALF_HEIGHT - project_height // 2: Tọa độ y (căn giữa theo chiều dọc)
                wall_pos = (ray * SCALE, HALF_HEIGHT - project_height // 2)
            else:
                texture_height =  TEXTURE_SIZE * HEIGHT / project_height
                wall_column = self.textures[texture].subsurface(
                    offset * (TEXTURE_SIZE - SCALE), HALF_TEXTURE_SIZE- texture_height // 2,
                    SCALE, texture_height
                )
                wall_column = pg.transform.scale(wall_column, (SCALE, HEIGHT))
                wall_pos = (ray * SCALE, 0)
            # Thêm tuple (depth, wall_column, wall_pos) vào danh sách objects_to_render
            # - depth: Để sắp xếp khi vẽ
            # - wall_column: Cột texture đã được xử lý
            # - wall_pos: Vị trí trên màn hình
            self.objects_to_render.append((depth, wall_column, wall_pos))


    
    def ray_cast(self): 
        """Phương thức chính để thực hiện raycasting: bắn các tia và tính toán dữ liệu"""
        # Xóa danh sách ray_casting_result cũ để chuẩn bị cho dữ liệu mới
        self.ray_casting_result = []
        
        # Khởi tạo biến để lưu loại texture của bức tường mà tia chạm vào (theo hướng ngang và dọc)
        texture_vert, texture_hor = 2, 2 

        # Lấy vị trí thực của người chơi (tọa độ thập phân, ví dụ: (2.5, 3.7))
        ox, oy = self.game.player.pos 

        # Lấy vị trí nguyên của người chơi trên bản đồ (tọa độ ô, ví dụ: (2, 3))
        x_map, y_map = self.game.player.map_pos

        # Tính góc của tia đầu tiên: góc của người chơi trừ nửa góc nhìn (FOV) cộng một giá trị nhỏ để tránh lỗi
        ray_angle = self.game.player.angle - HALF_FOV + 0.001

        # Duyệt qua từng tia (ray), tổng cộng NUM_RAYS tia
        for ray in range(NUM_RAYS):
            # Tính sin và cos của góc tia hiện tại, dùng để tính toán giao điểm
            sin_a = sin(ray_angle)
            cos_a = cos(ray_angle)

            # Tính giao điểm ngang (horizontal intersection)
            # - Nếu sin_a > 0: Tia hướng xuống dưới, kiểm tra ô bên dưới (y_map + 1)
            # - Nếu sin_a < 0: Tia hướng lên trên, kiểm tra ô bên trên (y_map - 1e-15)
            y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-15, -1)

            # Tính khoảng cách đến giao điểm ngang đầu tiên
            depth_h = (y_hor - oy) / sin_a

            # Tính tọa độ x của giao điểm ngang
            x_hor = ox + depth_h * cos_a

            # Tính khoảng cách tăng thêm cho mỗi bước kiểm tra tiếp theo
            delta_depth = dy / sin_a
            dx = delta_depth * cos_a

            # Kiểm tra giao điểm ngang tối đa MAX_DEPTH lần
            for i in range(MAX_DEPTH):
                # Tọa độ ô mà tia giao với (theo hướng ngang)
                title_h = int(x_hor), int(y_hor)

                # Nếu ô này có trong bản đồ (tức là có bức tường), dừng kiểm tra
                if title_h in self.game.map.world_map:
                    # Lấy loại texture của bức tường tại ô này
                    texture_hor = self.game.map.world_map[title_h]
                    break
                
                # Nếu không có bức tường, tiếp tục kiểm tra ô tiếp theo
                x_hor += dx
                y_hor += dy
                depth_h += delta_depth


            # Tính giao điểm dọc (vertical intersection)
            # - Nếu cos_a > 0: Tia hướng sang phải, kiểm tra ô bên phải (x_map + 1)
            # - Nếu cos_a < 0: Tia hướng sang trái, kiểm tra ô bên trái (x_map - 1e-15)
            x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-15, -1)

            # Tính khoảng cách đến giao điểm dọc đầu tiên
            depth_vert = (x_vert - ox) / cos_a

            # Tính tọa độ y của giao điểm dọc
            y_vert = oy + depth_vert * sin_a
            
            # Tính khoảng cách tăng thêm cho mỗi bước kiểm tra tiếp theo
            delta_depth = dx / cos_a
            dy = delta_depth * sin_a

            # Kiểm tra giao điểm dọc tối đa MAX_DEPTH lần
            for i in range(MAX_DEPTH):
                # Tọa độ ô mà tia giao với (theo hướng dọc)
                title_v = int(x_vert), int(y_vert)
                
                # Nếu ô này có trong bản đồ (tức là có bức tường), dừng kiểm tra
                if title_v in self.game.map.world_map:
                    # Lấy loại texture của bức tường tại ô này
                    texture_vert = self.game.map.world_map[title_v]
                    break 
            
                # Nếu không có bức tường, tiếp tục kiểm tra ô tiếp theo
                x_vert += dx
                y_vert += dy
                depth_vert += delta_depth


            # So sánh khoảng cách đến giao điểm ngang (depth_h) và dọc (depth_vert)
            # Chọn giao điểm gần nhất để xác định bức tường mà tia chạm vào
            if depth_vert < depth_h:
                # Nếu giao điểm dọc gần hơn:
                # - Chọn khoảng cách đến giao điểm dọc làm khoảng cách cuối cùng
                # - Chọn loại texture của bức tường tại giao điểm dọc
                depth, texture = depth_vert, texture_vert

                # Lấy phần thập phân của y_vert (vị trí tương đối trên bức tường)
                y_vert %= 1 # lấy phần thập phân của y_vert 

                # Tính offset (giá trị từ 0 đến 1) để ánh xạ texture
                # - Nếu cos_a > 0 (tia hướng phải): offset = y_vert
                # - Nếu cos_a < 0 (tia hướng trái): offset = 1 - y_vert (đảo ngược)
                offset = y_vert if cos_a > 0 else (1 - y_vert) 
            else:
                # Nếu giao điểm ngang gần hơn:
                # - Chọn khoảng cách đến giao điểm ngang làm khoảng cách cuối cùng
                # - Chọn loại texture của bức tường tại giao điểm ngang
                depth, texture = depth_h, texture_hor

                # Lấy phần thập phân của x_hor (vị trí tương đối trên bức tường)
                x_hor %= 1
                
                # Tính offset (giá trị từ 0 đến 1) để ánh xạ texture
                # - Nếu sin_a > 0 (tia hướng xuống): offset = 1 - x_hor (đảo ngược)
                # - Nếu sin_a < 0 (tia hướng lên): offset = x_hor
                offset = (1 - x_hor) if sin_a > 0 else x_hor
            
            # Hiệu chỉnh khoảng cách để loại bỏ hiệu ứng "fishbowl" (méo hình)
            # Nhân depth với cos của góc lệch để đảm bảo khoảng cách chính xác
            depth *= math.cos(self.game.player.angle - ray_angle)

            # Tính chiều cao của bức tường trên màn hình (project_height)
            # - SCREEN_DIST: Khoảng cách từ người chơi đến màn hình (hằng số)
            # - depth: Khoảng cách đến bức tường
            # - 0.0001: Giá trị nhỏ để tránh chia cho 0
            project_hight = (SCREEN_DIST * 1) / (depth + 0.0001)

            # Đoạn mã vẽ cột màu đã bị comment (không dùng nữa)
            # Trước đây, vẽ cột tường bằng màu đơn sắc dựa trên khoảng cách
            # color = [200 / (1 + depth ** 5 * 0.0002)] * 3
            # pg.draw.rect(self.game.screen, color, (ray * SCALE, HALF_HEIGHT - project_hight // 2, SCALE, project_hight))
            
            # Đoạn mã vẽ tia (dùng để debug) (không dùng nữa)
            # Vẽ một đường màu vàng từ vị trí người chơi đến điểm giao
            # pg.draw.line(self.game.screen, 'yellow', (100*ox, 100*oy), (100 * ox + 100 * depth * cos_a, 100 * oy + 100 * depth * sin_a), 2)
            
            # Lưu kết quả raycasting của tia hiện tại vào self.ray_casting_result
            # Tuple chứa: (depth, project_hight, texture, offset)
            self.ray_casting_result.append((depth, project_hight, texture, offset))

            # Tăng góc của tia để chuyển sang tia tiếp theo
            # DELTA_ANGLE là góc tăng thêm giữa hai tia liên tiếp
            ray_angle += DELTA_ANGLE



    def update(self):
        """Phương thức để cập nhật raycasting trong mỗi khung hình"""
        # Gọi ray_cast để bắn các tia và tính toán dữ liệu
        self.ray_cast()
        # Gọi get_object_to_rander để tạo danh sách các đối tượng cần vẽ
        self.get_object_to_rander()