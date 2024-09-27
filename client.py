# client.py
import socket
import threading

# กำหนดที่อยู่และพอร์ตของเซิร์ฟเวอร์
HOST = '127.0.0.1'  # localhost
PORT = 65432        # พอร์ตเดียวกับเซิร์ฟเวอร์

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                break
            print(data)
        except:
            break

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
        except ConnectionRefusedError:
            print("Cannot connect to the server. Make sure the server is running.")
            return
        
        # เริ่ม Thread สำหรับรับข้อความจากเซิร์ฟเวอร์
        thread = threading.Thread(target=receive_messages, args=(s,))
        thread.daemon = True
        thread.start()
        
        while True:
            message = input()
            if message.lower() == "exit":
                break
            s.sendall(message.encode())

if __name__ == "__main__":
    main()
