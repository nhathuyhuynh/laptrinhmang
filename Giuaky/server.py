import socket
import threading
import random

HOST = "127.0.0.1"
PORT = 9999
MAX_WIN = 3

# ================= STATE =================
clients = {}          # {pid: socket}
mode = None           # None | "AI" | "PVP"
choices = {}
scores = {1: 0, 2: 0}
round_num = 1
lock = threading.Lock()


# ================= GAME LOGIC =================
def check_winner(c1, c2):
    if c1 == c2:
        return 0
    if (c1 == "keo" and c2 == "bao") or \
       (c1 == "bao" and c2 == "bua") or \
       (c1 == "bua" and c2 == "keo"):
        return 1
    return 2


# ================= NETWORK =================
def send(pid, msg):
    if pid in clients:
        try:
            clients[pid].sendall((msg + "\n").encode())
        except:
            pass


def send_all(msg):
    for pid in list(clients.keys()):
        send(pid, msg)


def reset_game():
    global scores, round_num, choices
    scores = {1: 0, 2: 0}
    round_num = 1
    choices.clear()
    send_all("🔄 Trận đấu đã RESET")


def play_round():
    global round_num
    c1, c2 = choices[1], choices[2]
    winner = check_winner(c1, c2)

    msg = f"\n🎯 VÁN {round_num}\n"
    msg += f"Bạn: {c1}\n"
    msg += f"Đối thủ: {c2}\n"

    if winner == 0:
        msg += "👉 KẾT QUẢ: HÒA\n"
    else:
        scores[winner] += 1
        msg += f"👉 KẾT QUẢ: {'BẠN' if winner == 1 else 'ĐỐI THỦ'} THẮNG\n"

    msg += f"📊 TỶ SỐ: {scores[1]} - {scores[2]}"
    send_all(msg)

    if scores[1] == MAX_WIN or scores[2] == MAX_WIN:
        send_all(
            f"🏆 {'BẠN' if scores[1] == MAX_WIN else 'ĐỐI THỦ'} "
            f"THẮNG CHUNG CUỘC (BO5)"
        )
        reset_game()
    else:
        round_num += 1
        choices.clear()


# ================= CLIENT HANDLER =================
def handle_client(conn, pid):
    global mode
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

                # ===== MODE (CHỈ PLAYER 1) =====
                if line.startswith("MODE:") and pid == 1:
                    mode = line.split(":")[1]

                    # ----- AI MODE -----
                    if mode == "AI":
                        send(1, "🤖 Chế độ: CHƠI VỚI MÁY")
                        send(1, "🎮 Bắt đầu chơi!")

                        # kick player 2 nếu có
                        if 2 in clients:
                            try:
                                clients[2].sendall(
                                    "FORCE:DISCONNECT\n".encode()
                                )
                                clients[2].close()
                            except:
                                pass
                            del clients[2]

                    # ----- PVP MODE -----
                    elif mode == "PVP":
                        send(1, "👤 Chế độ: CHƠI 2 NGƯỜI")
                        send(1, "⏳ Đang chờ người chơi khác...")

                        # nếu player 2 đã có sẵn
                        if 2 in clients:
                            send(1, "MATCH:PVP_READY")
                            send(2, "MATCH:PVP_READY")

                    continue

                # ===== RESET =====
                if line == "RESET":
                    with lock:
                        reset_game()
                    continue

                # ===== GAME PLAY =====
                with lock:
                    if pid in choices:
                        continue

                    choices[pid] = line

                    # ----- AI -----
                    if mode == "AI":
                        if pid != 1:
                            continue
                        choices[2] = random.choice(["keo", "bua", "bao"])
                        play_round()

                    # ----- PVP -----
                    elif mode == "PVP" and len(choices) == 2:
                        play_round()

        except:
            break

    # ===== DISCONNECT =====
    try:
        conn.close()
    except:
        pass
    if pid in clients:
        del clients[pid]


# ================= MAIN =================
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(2)
    print("🟢 Server đang chạy...")

    pid = 1
    while True:
        conn, addr = server.accept()
        clients[pid] = conn
        conn.sendall(f"PLAYER:{pid}\n".encode())

        threading.Thread(
            target=handle_client,
            args=(conn, pid),
            daemon=True
        ).start()

        print(f"PLAYER {pid} đã kết nối")

        # nếu player 2 vào khi đang PVP
        if pid == 2 and mode == "PVP":
            send(1, "MATCH:PVP_READY")
            send(2, "MATCH:PVP_READY")

        pid += 1


if __name__ == "__main__":
    main()
