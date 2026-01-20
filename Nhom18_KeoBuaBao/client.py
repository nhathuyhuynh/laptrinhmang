import socket
import tkinter as tk
import threading
from tkinter import messagebox

HOST = "127.0.0.1"
PORT = 9999

# ================= SOCKET =================
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# ================= STATE =================
player_id = None     # 1 | 2
ready = False        # đã được phép chơi chưa

# ================= GUI =================
root = tk.Tk()
root.title("🎮 Kéo - Búa - Bao | BO5")
root.geometry("520x640")
root.resizable(False, False)

# ================= UTIL =================
def send(msg):
    try:
        client.sendall((msg + "\n").encode())
    except:
        pass

def set_buttons(enable: bool):
    for b in choice_buttons:
        b.config(state=tk.NORMAL if enable else tk.DISABLED)

def log(msg):
    box.config(state="normal")
    box.insert(tk.END, msg + "\n")
    box.see(tk.END)
    box.config(state="disabled")

def force_disconnect(reason):
    messagebox.showinfo("Thông báo", reason)
    try:
        client.close()
    except:
        pass
    root.destroy()

# ================= TITLE =================
tk.Label(
    root, text="CHỌN CHẾ ĐỘ CHƠI",
    font=("Arial", 16, "bold")
).pack(pady=10)

# ================= MODE (CHỈ PLAYER 1) =================
mode_frame = tk.Frame(root)
mode_frame.pack(pady=10)

def choose_mode(mode):
    global ready

    # ❌ PLAYER 2 KHÔNG ĐƯỢC CHỌN MODE
    if player_id == 2:
        status.config(text="❌ Player 2 không được chọn chế độ")
        return

    send(f"MODE:{mode}")
    mode_frame.pack_forget()

    # ===== AI MODE =====
    if mode == "AI":
        ready = True
        set_buttons(True)
        status.config(text="🤖 Chơi với máy – Bắt đầu!")
    else:
        status.config(text="⏳ Đang chờ người chơi khác...")

tk.Button(
    mode_frame, text="🤖 Chơi với máy",
    width=24,
    command=lambda: choose_mode("AI")
).pack(pady=5)

tk.Button(
    mode_frame, text="👤 Chơi với người",
    width=24,
    command=lambda: choose_mode("PVP")
).pack(pady=5)

# ================= CHOICES =================
btn_frame = tk.Frame(root)
btn_frame.pack(pady=20)

def choose(choice):
    if not ready:
        status.config(text="⏳ Chưa sẵn sàng chơi")
        return
    send(choice)
    status.config(text="⏳ Đang chờ đối thủ...")

choice_buttons = []
for i, (txt, val) in enumerate([
    ("✌ KÉO", "keo"),
    ("✊ BÚA", "bua"),
    ("✋ BAO", "bao")
]):
    b = tk.Button(
        btn_frame,
        text=txt,
        width=12,
        height=2,
        state=tk.DISABLED,
        command=lambda v=val: choose(v)
    )
    b.grid(row=0, column=i, padx=6)
    choice_buttons.append(b)

# ================= STATUS =================
status = tk.Label(root, text="🔌 Đang kết nối server...", fg="blue")
status.pack(pady=5)

# ================= RESET =================
tk.Button(
    root,
    text="🔄 RESET",
    width=30,
    command=lambda: send("RESET")
).pack(pady=10)

# ================= LOG =================
box = tk.Text(root, height=18, width=60, state="disabled")
box.pack()

# ================= RECEIVE =================
def receive():
    global player_id, ready
    buffer = ""

    while True:
        try:
            data = client.recv(2048).decode()
            if not data:
                break
            buffer += data

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()

                # ===== PLAYER ID =====
                if line.startswith("PLAYER:"):
                    player_id = int(line.split(":")[1])

                    if player_id == 1:
                        status.config(text="👤 Bạn là PLAYER 1")
                    else:
                        # Player 2: không được chọn mode
                        mode_frame.pack_forget()
                        status.config(
                            text="👤 Bạn là PLAYER 2 – Đang chờ Player 1 chọn chế độ"
                        )

                    log(line)
                    continue

                # ===== PVP READY =====
                if line == "MATCH:PVP_READY":
                    ready = True
                    set_buttons(True)
                    status.config(text="👤 Đã tìm thấy đối thủ – Bắt đầu chơi!")
                    log("🎮 Ghép cặp PVP thành công")
                    continue

                # ===== FORCE DISCONNECT =====
                if line == "FORCE:DISCONNECT":
                    force_disconnect(
                        "Player 1 đã chọn chơi với máy.\nBạn đã bị ngắt kết nối."
                    )
                    return

                log(line)

        except:
            break

    force_disconnect("Mất kết nối tới server")

threading.Thread(target=receive, daemon=True).start()
root.mainloop()
