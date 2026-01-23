import asyncio
import websockets
import json
import hashlib
from datetime import datetime
from collections import defaultdict
from db import (
    init_db, save_message, load_messages, 
    verify_user, create_user, get_user_role,
    save_private_message, load_private_messages,
    get_all_users
)

# Khởi tạo
init_db()

# Biến toàn cục
clients = {}              # ws -> {username, room, role}
rooms = defaultdict(set)  # room -> set(ws)
private_chats = {}        # username -> ws

def online_in_room(room):
    """Số user online trong room"""
    return len(rooms[room])

def get_online_users(room):
    """Lấy danh sách user online trong room"""
    users = []
    for ws in rooms[room]:
        if ws in clients and clients[ws]:
            users.append(clients[ws]["username"])
    return users

async def broadcast(room, data, exclude_ws=None):
    """Gửi tin nhắn đến tất cả trong room"""
    dead = []
    for ws in rooms[room]:
        if ws == exclude_ws:
            continue
        try:
            await ws.send(json.dumps(data))
        except:
            dead.append(ws)
    
    # Xóa các connection bị hỏng
    for ws in dead:
        rooms[room].discard(ws)
        if ws in clients:
            del clients[ws]

async def send_userlist(room):
    """Gửi danh sách user online"""
    users = get_online_users(room)
    await broadcast(room, {
        "type": "userlist",
        "users": users,
        "count": len(users)
    })

async def handler(ws, path):
    """Xử lý kết nối WebSocket"""
    clients[ws] = None
    
    try:
        async for raw in ws:
            try:
                data = json.loads(raw)
            except:
                continue
            
            # ========= REGISTER =========
            if data["type"] == "register":
                username = data.get("username", "").strip()
                password = data.get("password", "").strip()
                
                if not username or not password:
                    await ws.send(json.dumps({
                        "type": "error",
                        "message": "Username và password không được để trống"
                    }))
                    continue
                
                if len(username) < 3:
                    await ws.send(json.dumps({
                        "type": "error",
                        "message": "Username phải có ít nhất 3 ký tự"
                    }))
                    continue
                
                try:
                    create_user(username, password)
                    await ws.send(json.dumps({
                        "type": "register_ok",
                        "message": "Đăng ký thành công!"
                    }))
                except:
                    await ws.send(json.dumps({
                        "type": "error",
                        "message": "Username đã tồn tại"
                    }))

            # ========= LOGIN =========
            elif data["type"] == "login":
                username = data.get("username", "").strip()
                password = data.get("password", "").strip()
                room = data.get("room", "general")
                
                if not username or not password:
                    await ws.send(json.dumps({
                        "type": "login_fail",
                        "message": "Vui lòng nhập username và password"
                    }))
                    continue
                
                # Xác thực user
                if verify_user(username, password):
                    role = get_user_role(username)
                    clients[ws] = {
                        "username": username,
                        "room": room,
                        "role": role
                    }
                    rooms[room].add(ws)
                    private_chats[username] = ws
                    
                    # Gửi thông tin đăng nhập thành công
                    await ws.send(json.dumps({
                        "type": "login_success",
                        "username": username,
                        "role": role,
                        "room": room,
                        "online": online_in_room(room),
                        "history": load_messages(room),
                        "all_users": get_all_users()
                    }))
                    
                    # Thông báo user mới online
                    await broadcast(room, {
                        "type": "system",
                        "message": f"🎉 {username} đã tham gia phòng"
                    }, exclude_ws=ws)
                    
                    # Gửi danh sách user online
                    await send_userlist(room)
                    
                else:
                    await ws.send(json.dumps({
                        "type": "login_fail",
                        "message": "Sai username hoặc password"
                    }))

            # ========= PUBLIC MESSAGE =========
            elif data["type"] == "message":
                if not clients.get(ws):
                    continue
                
                user = clients[ws]
                room = user["room"]
                sender = user["username"]
                message = data.get("message", "").strip()
                
                if not message:
                    continue
                
                # Lưu tin nhắn
                msg_id = save_message(room, sender, message)
                
                # Gửi đến mọi người trong room
                await broadcast(room, {
                    "type": "message",
                    "sender": sender,
                    "message": message,
                    "room": room,
                    "time": datetime.now().strftime("%H:%M"),
                    "id": msg_id
                })

            # ========= PRIVATE MESSAGE =========
            elif data["type"] == "private_message":
                if not clients.get(ws):
                    continue
                
                sender = clients[ws]["username"]
                receiver = data.get("to", "").strip()
                message = data.get("message", "").strip()
                
                if not message or not receiver:
                    continue
                
                # Lưu tin nhắn riêng
                save_private_message(sender, receiver, message)
                
                # Gửi cho người nhận nếu online
                if receiver in private_chats:
                    try:
                        await private_chats[receiver].send(json.dumps({
                            "type": "private_message",
                            "from": sender,
                            "message": message,
                            "time": datetime.now().strftime("%H:%M")
                        }))
                    except:
                        pass
                
                # Gửi xác nhận cho người gửi
                await ws.send(json.dumps({
                    "type": "private_sent",
                    "to": receiver,
                    "message": message,
                    "time": datetime.now().strftime("%H:%M")
                }))

            # ========= SWITCH ROOM =========
            elif data["type"] == "switch_room":
                if not clients.get(ws):
                    continue
                
                user = clients[ws]
                old_room = user["room"]
                new_room = data.get("room", "general")
                
                if old_room == new_room:
                    continue
                
                # Rời phòng cũ
                rooms[old_room].discard(ws)
                
                # Thông báo rời phòng
                await broadcast(old_room, {
                    "type": "system",
                    "message": f"👋 {user['username']} đã rời phòng"
                })
                
                # Vào phòng mới
                user["room"] = new_room
                rooms[new_room].add(ws)
                
                # Gửi lịch sử tin nhắn phòng mới
                await ws.send(json.dumps({
                    "type": "room_switched",
                    "room": new_room,
                    "online": online_in_room(new_room),
                    "history": load_messages(new_room)
                }))
                
                # Thông báo vào phòng mới
                await broadcast(new_room, {
                    "type": "system",
                    "message": f"🎉 {user['username']} đã tham gia phòng"
                })
                
                # Cập nhật danh sách user cả 2 phòng
                await send_userlist(old_room)
                await send_userlist(new_room)

            # ========= GET USERS =========
            elif data["type"] == "get_users":
                await ws.send(json.dumps({
                    "type": "all_users",
                    "users": get_all_users()
                }))

            # ========= TYPING =========
            elif data["type"] == "typing":
                if not clients.get(ws):
                    continue
                
                user = clients[ws]
                await broadcast(user["room"], {
                    "type": "typing",
                    "user": user["username"],
                    "is_typing": data.get("is_typing", False)
                }, exclude_ws=ws)

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Xử lý khi client disconnect
        user = clients.get(ws)
        if user:
            username = user["username"]
            room = user["room"]
            
            # Xóa khỏi room
            rooms[room].discard(ws)
            
            # Xóa khỏi private chats
            if username in private_chats:
                del private_chats[username]
            
            # Thông báo user offline
            await broadcast(room, {
                "type": "system",
                "message": f"👋 {username} đã rời khỏi"
            })
            
            # Cập nhật danh sách user
            await send_userlist(room)
        
        # Xóa client
        if ws in clients:
            del clients[ws]

async def main():
    """Khởi chạy server"""
    print("=" * 50)
    print("🚀 WebSocket Chat Server")
    print("📡 Đang chạy tại ws://localhost:8765")
    print("📊 Database: chat.db")
    print("=" * 50)
    
    # SỬA DÒNG NÀY - ĐÂY LÀ CÁCH SỬA ĐƠN GIẢN NHẤT
    async with websockets.serve(lambda ws, path: handler(ws, path), "0.0.0.0", 8765):
        await asyncio.Future()  # Chạy mãi mãi

if __name__ == "__main__":
    asyncio.run(main())