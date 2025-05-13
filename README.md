# 🎮 Đồ án môn Trí Tuệ Nhân Tạo: Trò chơi Bắn Súng 3D Raycasting với AI Tìm Đường cho NPC

Đây là một game bắn súng góc nhìn thứ nhất (FPS) sử dụng kỹ thuật **Raycasting 3D** để mô phỏng không gian ba chiều trên mặt phẳng 2D. Điểm nổi bật là hệ thống **NPC thông minh**, có khả năng tự học và phản ứng linh hoạt nhờ ứng dụng các thuật toán **AI hiện đại**:

- 🌟 **A\***: Tìm đường ngắn nhất, tránh chướng ngại vật.
- 🧠 **Belief Map**: Cho phép NPC dự đoán vị trí người chơi kể cả khi không còn nhìn thấy.
- ⛰️ **Hill Climbing**: Đưa ra chiến lược hành động theo sự thay đổi niềm tin (belief).
- 🤖 **Q-Learning**: Giúp NPC học hành vi tối ưu qua trải nghiệm.

---

## 🧠 Các tính năng nổi bật

- ✅ **Raycasting 3D**: Tái hiện không gian ba chiều bằng kỹ thuật raycasting trên mặt phẳng 2D.
- ✅ **AI NPC thông minh**: Biết truy đuổi, chạy trốn, ẩn nấp theo lượng máu và tình huống chiến đấu.
- ✅ **Q-Table học hỏi**: Giúp NPC ghi nhớ và cải thiện hành vi qua từng vòng chơi.
- ✅ **Bản đồ mê cung**: Thử thách người chơi và khả năng học tập của NPC trong điều kiện không gian hẹp.
- ✅ **Điều khiển FPS cổ điển**: Hỗ trợ điều hướng bằng bàn phím và chuột mượt mà.

---

## 👨‍💻 Nhóm phát triển

| Họ và tên        | Mã sinh viên  |
|------------------|---------------|
| Nghiêm Quang Huy | 23110222      |
| Nguyễn Hoàng Hà  | 23110207      |

---

## 📦 Yêu cầu hệ thống

- Python 3.x ([Tải tại đây](https://www.python.org/downloads/))
- Thư viện `pygame` để xử lý đồ họa và sự kiện game.

---

## 🚀 Hướng dẫn cài đặt & chạy game

### 1. Tải mã nguồn dự án về

```bash
git clone https://github.com/HuyinCP/AI_projectGame.git
cd AI_projectGame
