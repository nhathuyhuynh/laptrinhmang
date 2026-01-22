import asyncio
import websockets
import json
import hashlib
from collections import defaultdict
from datetime import datetime

# --- THƯ VIỆN GIAO DIỆN ---
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

# Cấu hình màu sắc
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "error": "bold red",
    "success": "bold green",
    "user": "bold yellow",
    "room": "bold blue"
})
console = Console(theme=custom_theme)

# Giả lập import db (Giữ nguyên logic của bạn)
# Nếu bạn chạy lỗi dòng này, hãy đảm bảo file db.py nằm cùng thư mục
try:
    from db import init_db, save_message, load_messages, check_user, create_user
    init_db()
    console.print("[success]✔ Database loaded successfully[/success]")
except ImportError:
    console.print("[error]❌ Không tìm thấy file db.py! Chạy chế độ giả lập DB...[/error]")
    # Mock functions để code chạy được nếu thiếu db.py
    def init_db(): pass
    def save_message(r, s, m): pass
    def load_messages(r): return []
    def check_user(u): return True
    def create_user(u, p): pass

clients = {}            # ws -> {username, room}
rooms = defaultdict(set)  # room -> set ws

# --- HÀM LOGGING ĐẸP ---
def log(msg, style="info"):
    time = datetime.now().strftime("%H:%M:%S")
    console.print(f"[{time}] {msg}", style=style)

def online(room):
    return len(rooms[room])

async def broadcast(room, data):
    dead = []
    for ws in rooms[room]:
        try:
            await ws.send(json.dumps(data))
        except:
            dead.append(ws)
    for ws in dead:
        rooms[room].discard(ws)

async def handler(ws):
    clients[ws] = None
    addr = ws.remote_address
    log(f"Kết nối mới từ: {addr[0]}:{addr[1]}", "info")

    try:
        async for raw in ws:
            data = json.loads(raw)
            msg_type = data["type"]

            # ========= REGISTER =========
            if msg_type == "register":
                username = data["username"]
                password = data["password"]
                
                log(f"Đăng ký: [user]{username}[/user]", "warning")
                
                hashed = hashlib.sha256(password.encode()).hexdigest()
                
                try:
                    create_user(username, hashed)
                    await ws.send(json.dumps({
                        "type": "register_ok",
                        "message": "Đăng ký thành công"
                    }))
                    log(f"Đăng ký thành công: [user]{username}[/user]", "success")
                except:
                    await ws.send(json.dumps({
                        "type": "register_fail",
                        "message": "Username đã tồn tại"
                    }))
                    log(f"Đăng ký thất bại (Trùng tên): [user]{username}[/user]", "error")

            # ========= LOGIN =========
            elif msg_type == "login":
                username = data["username"]
                room = data.get("room", "general")
                
                if check_user(username):
                    clients[ws] = {"username": username, "room": room}
                    rooms[room].add(ws)

                    await ws.send(json.dumps({
                        "type": "login_success",
                        "username": username,
                        "room": room,
                        "online": online(room),
                        "history": load_messages(room)
                    }))

                    await broadcast(room, {
                        "type": "online",
                        "online": online(room)
                    })
                    
                    log(f"User [user]{username}[/user] đã vào phòng [room]{room}[/room]", "success")
                else:
                    await ws.send(json.dumps({
                        "type": "login_fail",
                        "message": "User không tồn tại"
                    }))
                    log(f"Login thất bại: [user]{username}[/user]", "error")

            # ========= MESSAGE =========
            elif msg_type == "message":
                user = clients.get(ws)
                if not user: continue

                room = user["room"]
                sender = user["username"]
                message = data["message"]

                save_message(room, sender, message)
                
                # In tin nhắn ra terminal để theo dõi
                console.print(f" 💬 [room]{room}[/room] | [user]{sender}[/user]: {message}")

                await broadcast(room, {
                    "type": "message",
                    "sender": sender,
                    "message": message,
                    "room": room
                })

            # ========= SWITCH ROOM =========
            elif msg_type == "switch_room":
                user = clients.get(ws)
                if not user: continue

                old = user["room"]
                new = data["room"]
                if old == new: continue

                rooms[old].discard(ws)
                rooms[new].add(ws)
                user["room"] = new

                await broadcast(old, {"type": "online", "online": online(old)})
                
                await ws.send(json.dumps({
                    "type": "switched",
                    "room": new,
                    "online": online(new),
                    "history": load_messages(new)
                }))

                await broadcast(new, {"type": "online", "online": online(new)})
                log(f"[user]{user['username']}[/user] chuyển: [room]{old}[/room] ➔ [room]{new}[/room]", "warning")

    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        log(f"Lỗi: {e}", "error")
    finally:
        user = clients.get(ws)
        if user:
            room = user["room"]
            username = user["username"]
            rooms[room].discard(ws)
            await broadcast(room, {
                "type": "online",
                "online": online(room)
            })
            log(f"[user]{username}[/user] đã ngắt kết nối.", "error")
        else:
            log(f"Kết nối ẩn danh đã đóng.", "info")
        clients.pop(ws, None)

async def main():
    # Hiển thị Banner đẹp mắt khi khởi động
    banner = Text("ROCKET CHAT SERVER", justify="center", style="bold white on blue")
    stats = f"Port: [bold green]8765[/bold green] | Protocol: [bold yellow]WebSocket[/bold yellow]"
    
    console.print(Panel(banner, style="blue"))
    console.print(f"🚀 {stats}")
    console.print("[italic gray]Đang chờ kết nối... (Nhấn Ctrl+C để dừng)[/italic gray]\n")

    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold red]🛑 Server đã dừng![/bold red]")