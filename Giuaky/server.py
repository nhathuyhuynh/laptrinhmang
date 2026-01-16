import socket
import threading

HOST = "127.0.0.1"
PORT = 9999
MAX_WIN = 3  # BO5

clients = {}
choices = {}
scores = {1: 0, 2: 0}
round_num = 1
lock = threading.Lock()

def check_winner(c1, c2):
    if c1 == c2:
        return 0
    if (c1 == "keo" and c2 == "bao") or \
       (c1 == "bao" and c2 == "bua") or \
       (c1 == "bua" and c2 == "keo"):
        return 1
    return 2

def send_all(msg):
    for c in clients.values():
        c.sendall((msg + "\n").encode())

def reset_game():
    global scores, round_num, choices
    scores = {1: 0, 2: 0}
    round_num = 1
    choices.clear()
    send_all("🔄 Trận đấu đã được RESET")

def handle_client(conn, pid):
    global round_num
    buffer = ""

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            buffer += data

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()

                if line == "RESET":
                    with lock:
                        reset_game()
                    continue

                with lock:
                    # mỗi người chỉ được chọn 1 lần / ván
                    if pid in choices:
                        continue

                    choices[pid] = line

                    if len(choices) < 2:
                        continue

                    p1 = choices[1]
                    p2 = choices[2]
                    winner = check_winner(p1, p2)

                    msg = f"\n🎯 VÁN {round_num}\n"
                    msg += f"Người chơi 1: {p1}\n"
                    msg += f"Người chơi 2: {p2}\n"

                    if winner == 0:
                        msg += "👉 KẾT QUẢ: HÒA\n"
                    else:
                        scores[winner] += 1
                        msg += f"👉 KẾT QUẢ: NGƯỜI CHƠI {winner} THẮNG\n"

                    msg += f"📊 TỶ SỐ: P1 {scores[1]} - {scores[2]} P2"
                    send_all(msg)

                    if scores[1] == MAX_WIN or scores[2] == MAX_WIN:
                        send_all(f"🏆 NGƯỜI CHƠI {winner} THẮNG CHUNG CUỘC (BO5)")
                        reset_game()
                    else:
                        round_num += 1
                        choices.clear()

        except:
            break

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(2)
    print("🟢 Server đang chạy...")

    # chờ đúng 2 client
    for pid in [1, 2]:
        conn, addr = server.accept()
        print("Kết nối từ:", addr)
        clients[pid] = conn

    # gửi ID sau khi đủ 2 người
    for pid, conn in clients.items():
        conn.sendall(f"PLAYER:{pid}\n".encode())

    # chạy thread
    for pid, conn in clients.items():
        threading.Thread(
            target=handle_client,
            args=(conn, pid),
            daemon=True
        ).start()

    while True:
        pass

if __name__ == "__main__":
    main()
