import asyncio
import websockets
import json
import hashlib
from collections import defaultdict
from datetime import datetime

# --- 1. KẾT NỐI DATABASE ---
# Tự động tìm file db.py, nếu không thấy sẽ chạy chế độ giả lập
try:
    import db
    db.init_db()
    print("✅ [SYSTEM] Database đã kết nối thành công!")
except ImportError:
    print("❌ [ERROR] Không tìm thấy file db.py! Đang chạy chế độ giả lập (không lưu tin nhắn lâu dài).")
    # Mock class để server không bị crash nếu thiếu file db
    class db:
        @staticmethod
        def init_db(): pass
        @staticmethod
        def save_message(r, s, m): pass
        @staticmethod
        def load_messages(r): return []
        @staticmethod
        def check_user(u): return True # Luôn cho phép đăng nhập nếu không có DB
        @staticmethod
        def create_user(u, p): pass

clients = {}            # Quản lý kết nối: ws -> {username, room}
rooms = defaultdict(set)  # Quản lý phòng: room -> set(ws)

# --- 2. HÀM HỖ TRỢ ---
def get_time():
    return datetime.now().strftime("%H:%M")

def online(room):
    return len(rooms[room])

async def broadcast(room, data):
    if room not in rooms: return
    
    # Tạo bản sao danh sách để gửi tin (tránh lỗi khi danh sách thay đổi đột ngột)
    connections = list(rooms[room]) 
    for ws in connections:
        try:
            await ws.send(json.dumps(data))
        except:
            rooms[room].discard(ws)

# --- 3. XỬ LÝ CHÍNH (HANDLER) ---
async def handler(ws):
    clients[ws] = None
    print(f"🔗 Kết nối mới từ: {ws.remote_address}")

    try:
        async for raw in ws:
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue # Bỏ qua tin nhắn rác không đúng định dạng

            mode = data["type"]

            # ========= ĐĂNG KÝ =========
            if mode == "register":
                username = data["username"]
                password = data["password"]
                hashed = hashlib.sha256(password.encode()).hexdigest()
                
                try:
                    db.create_user(username, hashed)
                    await ws.send(json.dumps({"type": "register_ok"}))
                    print(f"📝 Đăng ký mới thành công: {username}")
                except Exception as e:
                    # Thường lỗi do trùng tên
                    await ws.send(json.dumps({"type": "register_fail", "message": "Tên đã tồn tại!"}))

            # ========= ĐĂNG NHẬP =========
            elif mode == "login":
                username = data["username"]
                room = data.get("room", "general")
                
                if db.check_user(username):
                    clients[ws] = {"username": username, "room": room}
                    rooms[room].add(ws)

                    # Lấy tin nhắn cũ từ DB gửi cho user
                    history = db.load_messages(room)

                    await ws.send(json.dumps({
                        "type": "login_success",
                        "username": username,
                        "room": room,
                        "online": online(room),
                        "history": history
                    }))

                    # Báo cho cả phòng biết có người mới vào
                    await broadcast(room, {"type": "online", "online": online(room)})
                    print(f"👉 {username} đã vào phòng: {room}")
                else:
                    await ws.send(json.dumps({"type": "login_fail"}))

            # ========= TIN NHẮN (ĐÃ SỬA ĐỂ HẾT LAG) =========
            elif mode == "message":
                user_info = clients.get(ws)
                if user_info:
                    room = user_info["room"]
                    sender = user_info["username"]
                    msg = data["message"]
                    now_time = get_time()
                    
                    # --- QUAN TRỌNG: GỬI TRƯỚC (Để mượt) ---
                    await broadcast(room, {
                        "type": "message",
                        "sender": sender,
                        "message": msg,
                        "time": now_time 
                    })
                    
                    # --- IN LOG RA MÀN HÌNH ---
                    # Nếu tin nhắn quá dài (như ảnh), chỉ in ngắn gọn
                    log_msg = msg if len(msg) < 50 else "(Hình ảnh/Tin dài...)"
                    print(f"💬 [{room}] {sender}: {log_msg}") 

                    # --- LƯU SAU (Để không chặn server) ---
                    try:
                        db.save_message(room, sender, msg)
                    except Exception as e:
                        print(f"⚠️ Lỗi lưu tin nhắn vào DB: {e}")

            # ========= CHUYỂN PHÒNG =========
            elif mode == "switch_room":
                user_info = clients.get(ws)
                if user_info:
                    old_room = user_info["room"]
                    new_room = data["room"]
                    
                    if old_room != new_room:
                        # Rời phòng cũ
                        rooms[old_room].discard(ws)
                        # Vào phòng mới
                        rooms[new_room].add(ws)
                        user_info["room"] = new_room
                        
                        # Cập nhật số lượng online phòng cũ
                        await broadcast(old_room, {"type": "online", "online": online(old_room)})
                        
                        # Gửi dữ liệu phòng mới cho user
                        await ws.send(json.dumps({
                            "type": "switched",
                            "room": new_room,
                            "online": online(new_room),
                            "history": db.load_messages(new_room)
                        }))
                        
                        # Cập nhật số lượng online phòng mới
                        await broadcast(new_room, {"type": "online", "online": online(new_room)})
                        print(f"🔄 {user_info['username']} chuyển: {old_room} -> {new_room}")

    except websockets.exceptions.ConnectionClosed:
        pass # User thoát bình thường
    except Exception as e:
        print(f"⚠️ Lỗi xử lý: {e}")
    finally:
        # Dọn dẹp khi user thoát
        user_info = clients.pop(ws, None)
        if user_info:
            room = user_info["room"]
            rooms[room].discard(ws)
            await broadcast(room, {"type": "online", "online": online(room)})
            print(f"👋 {user_info['username']} đã thoát.")

# --- 4. CHẠY SERVER ---
async def main():
    print("=" * 50)
    print("🚀 SERVER CHAT ĐANG CHẠY (BẢN TỐI ƯU TỐC ĐỘ)")
    print("👉 Địa chỉ: ws://localhost:8765")
    print("👉 Bấm Ctrl + C để dừng")
    print("=" * 50)
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server đã dừng an toàn!")