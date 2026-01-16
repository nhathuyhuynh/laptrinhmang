import socket
import tkinter as tk
import threading

HOST = "127.0.0.1"
PORT = 9999

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

player_id = None

# ================= GUI =================
root = tk.Tk()
root.title("🎮 Kéo - Búa - Bao | BO5")
root.geometry("520x580")
root.resizable(False, False)

player_label = tk.Label(root, text="Đang kết nối...", font=("Arial", 12, "bold"), fg="gray")
player_label.pack(pady=5)

title = tk.Label(root, text="TRÒ CHƠI KÉO - BÚA - BAO", font=("Arial", 18, "bold"))
title.pack()

sub = tk.Label(root, text="Chế độ BO5 – Thắng 3 ván", fg="gray")
sub.pack(pady=5)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=15)

def send_choice(choice):
    client.sendall((choice + "\n").encode())
    status_label.config(text=f"Bạn đã chọn: {choice.upper()}", fg="#0066cc")

tk.Button(btn_frame, text="✌ KÉO", width=14, height=2,
          command=lambda: send_choice("keo")).grid(row=0, column=0, padx=6)

tk.Button(btn_frame, text="✊ BÚA", width=14, height=2,
          command=lambda: send_choice("bua")).grid(row=0, column=1, padx=6)

tk.Button(btn_frame, text="✋ BAO", width=14, height=2,
          command=lambda: send_choice("bao")).grid(row=0, column=2, padx=6)

status_label = tk.Label(root, text="Chọn nước đi", fg="gray")
status_label.pack()

def reset_game():
    client.sendall("RESET\n".encode())

tk.Button(root, text="🔄 RESET TRẬN ĐẤU", width=32,
          command=reset_game).pack(pady=8)

result_box = tk.Text(root, height=16, width=60, state="disabled", bg="#fafafa")
result_box.pack(pady=10)

# ================= SOCKET THREAD =================
def receive_data():
    global player_id
    buffer = ""

    while True:
        try:
            data = client.recv(2048).decode()
            buffer += data

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()

                if line.startswith("PLAYER:"):
                    player_id = line.split(":")[1]
                    player_label.config(
                        text=f"Bạn là người chơi {player_id}",
                        fg="green"
                    )
                else:
                    result_box.config(state="normal")
                    result_box.insert(tk.END, line + "\n")
                    result_box.see(tk.END)
                    result_box.config(state="disabled")
        except:
            break

threading.Thread(target=receive_data, daemon=True).start()
root.mainloop()
