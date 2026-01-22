import asyncio
import websockets
import json
from collections import defaultdict
from db import init_db, save_message, load_messages

init_db()

clients = {}              # ws -> {username, room}
rooms = defaultdict(set)  # room -> set ws


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

    try:
        async for raw in ws:
            data = json.loads(raw)

            # ========= LOGIN =========
            if data["type"] == "login":
                username = data["username"]
                room = data.get("room", "general")

                clients[ws] = {
                    "username": username,
                    "room": room
                }

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

            # ========= MESSAGE =========
            elif data["type"] == "message":
                user = clients.get(ws)
                if not user:
                    continue

                room = user["room"]
                sender = user["username"]
                message = data["message"]

                save_message(room, sender, message)

                await broadcast(room, {
                    "type": "message",
                    "sender": sender,
                    "message": message,
                    "room": room
                })

            # ========= SWITCH ROOM =========
            elif data["type"] == "switch_room":
                user = clients.get(ws)
                if not user:
                    continue

                old = user["room"]
                new = data["room"]
                if old == new:
                    continue

                rooms[old].discard(ws)
                rooms[new].add(ws)
                user["room"] = new

                await broadcast(old, {
                    "type": "online",
                    "online": online(old)
                })

                await ws.send(json.dumps({
                    "type": "switched",
                    "room": new,
                    "online": online(new),
                    "history": load_messages(new)
                }))

                await broadcast(new, {
                    "type": "online",
                    "online": online(new)
                })

    finally:
        user = clients.get(ws)
        if user:
            room = user["room"]
            rooms[room].discard(ws)
            await broadcast(room, {
                "type": "online",
                "online": online(room)
            })
        clients.pop(ws, None)


async def main():
    print("🚀 Server running at ws://localhost:8765")
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()

asyncio.run(main())
