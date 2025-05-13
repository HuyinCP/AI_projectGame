# 🎮 Trò chơi Bắn Súng 3D Raycasting với AI Tìm Đường cho NPC

Dự án này là một game bắn súng góc nhìn thứ nhất (FPS) sử dụng kỹ thuật **Raycasting 3D** để mô phỏng môi trường 3D trên mặt phẳng 2D. Điểm nổi bật là hệ thống **NPC thông minh**, có khả năng tự học và phản ứng trước môi trường nhờ các thuật toán **AI hiện đại** như:

- 🌟 **A\***: Tìm đường ngắn nhất tránh chướng ngại vật.
- 🧠 **Belief Map**: Giúp NPC dự đoán vị trí của người chơi dù không nhìn thấy.
- ⛰️ **Hill Climbing**: Đưa ra quyết định chiến thuật theo niềm tin vị trí mục tiêu.
- 🤖 **Q-Learning**: Cho phép NPC học cách di chuyển và hành động tối ưu.

---

## 🧠 Các tính năng nổi bật

- ✅ **Raycasting 3D**: Tái hiện không gian 3D bằng kỹ thuật cổ điển trên môi trường 2D.
- ✅ **Hành vi NPC thông minh**: NPC có khả năng tự tìm đường, chạy trốn, truy đuổi hoặc ẩn nấp tùy theo lượng máu và tình huống.
- ✅ **AI học hỏi**: Sử dụng bảng Q-Table để học và ghi nhớ hành vi hiệu quả.
- ✅ **Môi trường mê cung**: Các bản đồ được thiết kế như mê cung giúp kiểm tra khả năng học tập của NPC.
- ✅ **Điều khiển FPS cổ điển**: Hỗ trợ điều hướng bằng bàn phím và chuột.

---

## 📷 Screenshot

![Game Screenshot](screenshots.png)

---

## 👨‍💻 Nhóm phát triển

| Họ và tên        | Mã sinh viên  |
|------------------|---------------|
| Nghiêm Quang Huy | 23110222      |
| Nguyễn Hoàng Hà  | 23110207      |

---

## 📦 Yêu cầu cài đặt

Trước khi chạy game, bạn cần cài đặt:

- [Python 3.x](https://www.python.org/downloads/)
- `pygame` – thư viện đồ họa và game cho Python.

### Cài đặt thư viện phụ thuộc

Mở terminal hoặc CMD và chạy:

```bash
pip install pygame
