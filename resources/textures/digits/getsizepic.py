from PIL import Image

# Đường dẫn tới ảnh
image_path = "resources/textures/digits/0.png"

# Mở ảnh và lấy kích thước
with Image.open(image_path) as img:
    width, height = img.size
    print(f"Kích thước ảnh: {width}x{height}")