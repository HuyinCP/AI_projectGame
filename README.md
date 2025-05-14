# XÂY DỰNG GAME BẮN SÚNG 3D VÀ ỨNG DỤNG CÁC THUẬT TOÁN TÌM KIẾM CHO NPC

- HCMC University of Technology and Education
- **Môn**: Trí Tuệ Nhân Tạo
- **Giảng viên hướng dẫn**: TS. Phan Thị Huyền Trang

Được dựa trên [đây](https://www.youtube.com/watch?v=ECqUrT7IdqQ&t=2720s) và phát triển và xây dựng lại thuật toán cho NPC nhằm tối ưu các hành vi mà NPC thực hiện.
Đây là một trò chơi bắn súng góc nhìn thứ nhất (FPS) sử dụng kỹ thuật **Raycasting 3D** để mô phỏng không gian ba chiều trên mặt phẳng 2D. Điểm nổi bật của dự án là **NPC thông minh**, có khả năng **tìm đường, truy đuổi, ẩn nấp và tự học hành vi chiến thuật** thông qua các thuật toán tìm kiếm trong môn Trí Tuệ Nhân Tạo.

---

## 🧠 Các thuật toán tìm kiếm & cách hoạt động

### 🌟 A* (A-star Search) – Tìm đường hiệu quả
- **Mục tiêu**: Giúp NPC tìm đường ngắn nhất đến mục tiêu.
- **Cách hoạt động**:
  - Mỗi bước tìm kiếm dựa trên công thức
    ```python
    f(current_state) = g(current_state) + h(current_state)
    ```
    - `g(current_state)` là chi phí từ điểm bắt đầu đến vị trí hiện tại.
    - `h(current_state)` là ước lượng khoảng cách từ vị trí hiện tại đến mục vị trí mục tiêu.
  - Thuật toán tham lam bằng mở rộng các ô có `f(current_state)` nhỏ nhất trước → đảm bảo vừa nhanh vừa tối ưu.
- **Ứng dụng trong game**: NPC dùng A* để di chuyển thông minh qua bản đồ mê cung, tránh vật cản và đi đến mục tiêu hiệu quả.

---

### 🧠 Belief Map – Bản đồ niềm tin
- **Mục tiêu**: Giúp NPC tiếp tục truy vết người chơi ngay cả khi không còn nhìn thấy.
- **Cách hoạt động**:
  - Khi mất dấu người chơi, NPC lưu lại vị trí cuối cùng quan sát được.
  - Sau đó cập nhật **"niềm tin"** về vị trí mới dựa vào chuyển động trước đó.
  - NPC sẽ tìm đến các vị trí có khả năng cao người chơi xuất hiện (dựa trên belief).
- **Ứng dụng**: Giúp hành vi của NPC trở nên **thực tế và không bị ngớ ngẩn khi người chơi trốn khỏi tầm nhìn**.

---

### ⛰️ Hill Climbing – Leo đồi chiến lược
- **Mục tiêu**: Giúp NPC ra quyết định hành vi chiến thuật như tấn công, rút lui, đi tuần.
- **Cách hoạt động**:
  - Với mỗi hành động khả thi (di chuyển, tấn công, chạy trốn...), NPC tính điểm lợi ích (heuristic).
  - Hành động có lợi ích cao nhất được chọn (leo lên "đồi" giá trị).
  - Nếu không còn lựa chọn tốt hơn → dừng tại điểm cực đại cục bộ.
- **Ứng dụng**: Khi NPC còn ít máu, nó có thể chọn rút lui về chỗ hồi máu thay vì cố lao vào chiến đấu → hành vi **linh hoạt và hợp lý hơn**.

---

### 🤖 Q-Learning – Tự học hành vi qua trải nghiệm
- **Mục tiêu**: Giúp NPC học cách tìm vị trí hồi máu (khi máu yếu)
- **Cách hoạt động**:
  - NPC lưu bảng Q-Table, mỗi ô tương ứng với cặp **(trạng thái, hành động)** và giá trị kỳ vọng.
  - Công thức cập nhật:
    ```python
    Q[state][action] = Q[state][action] + α * [r + γ * max(Q[state'][action']) - Q[state][action]]
    ```
    - `state`: trạng thái hiện tại
    - `action`: hành động được chọn
    - `r`: phần thưởng nhận được sau khi thực hiện hành động
    - `state'`: trạng thái mới sau hành động
    - `α`: tốc độ học
    - `γ`: hệ số chiết khấu tương lai
  - Trạng thái gồm: máu hiện tại, khoảng cách đến người chơi, vị trí hiện tại, v.v.
- **Ứng dụng**:
  - NPC dần học được hành vi như:
    - Tìm chỗ hồi máu khi máu yếu
    - Ưu tiên tấn công khi có lợi thế
  - NPC trở nên **càng thông minh sau mỗi lần lượt tìm được vị trí hồi máu**.
---
#### 🎲 Chiến lược ε-greedy – Khám phá và khai thác của Q-Learning

Để cân bằng giữa việc **khám phá hành vi mới** và **khai thác hành vi đã học**, NPC sử dụng chiến lược **epsilon-greedy (ε-greedy)**:

- Với xác suất `ε`: chọn **hành động ngẫu nhiên** → khám phá hành vi mới.
- Với xác suất `1 - ε`: chọn **hành động tốt nhất** từ bảng Q → khai thác kinh nghiệm cũ.
- Càng về sau, xác suất khám phá (`ε`) sẽ **giảm dần**, điều này giúp NPC **ưu tiên khai thác các hành động đã học** thay vì liên tục thử hành động ngẫu nhiên.

> Lý do: Ban đầu, NPC cần khám phá nhiều hành động khác nhau để hiểu môi trường. Nhưng khi đã có đủ dữ liệu và kinh nghiệm, việc khai thác (chọn hành động tốt nhất đã học) sẽ giúp NPC tối ưu hiệu quả hơn.

- Thường sử dụng công thức giảm dần `ε` theo mỗi vòng lặp (episode):
  
```python
epsilon = max(epsilon_min, epsilon * decay_rate)
Ví dụ triển khai bằng Python:

```python
import random
if random.uniform(0, 1) < epsilon:
    action = random.choice(possible_actions)  # Khám phá
else:
    action = max(Q[state], key=Q[state].get)  # Khai thác
```
## 🔥 Tính năng nổi bật

- ✅ **Raycasting 3D**: Hiển thị không gian 3D trong môi trường 2D.
- ✅ **Hành vi NPC linh hoạt**: Biết truy đuổi, rút lui, tấn công có chiến lược. (tính năng mới so với bản cũ)
- ✅ **Học hỏi qua trải nghiệm**: NPC ngày càng thông minh trong việc tìm vị trí hồi máu nhờ Q-Learning. (tính năng mới so với bản cũ)
- ✅ **Thử thách mê cung**: Kiểm tra khả năng điều hướng và truy đuổi trong môi trường phức tạp. (tính năng mới so với bản cũ)
- ✅ **Giao diện FPS**: Điều khiển bằng chuột và bàn phím như game 8x-9x.

---

## 👨‍💻 Thành viên phát triển

| Họ và tên        | Mã sinh viên  |
|------------------|---------------|
| Nghiêm Quang Huy | 23110222      |
| Nguyễn Hoàng Hà  | 23110207      |

---

## 🧰 Yêu cầu hệ thống

- Python 3.x  
- Thư viện `pygame`

---

## 🚀 Hướng dẫn cài đặt & chạy game

### 1. Tải mã nguồn
```bash
git clone https://github.com/HuyinCP/AI_projectGame.git
```
#### Vào folder đã clone và chạy file main.py
```bash
python main.py

