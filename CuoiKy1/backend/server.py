import asyncio, websockets, json

rooms = {}      # room -> set(ws)
clients = {}    # ws -> username

async def broadcast(room, data):
    for ws in list(rooms.get(room, [])):
        try:
            await ws.send(json.dumps(data))
        except:
            pass

async def handler(ws):
    try:
        async for raw in ws:
            data = json.loads(raw)

            # ===== LOGIN =====
            if data["type"] == "login":
                username = data["username"]
                room = data.get("room", "general")

                clients[ws] = username
                rooms.setdefault(room, set()).add(ws)

                print(f"✅ {username} joined {room}")

                await ws.send(json.dumps({
                    "type": "login_success",
                    "username": username,
                    "room": room
                }))

            # ===== MESSAGE =====
            elif data["type"] == "message":
                if ws not in clients:
                    print("❌ Message from unauthenticated ws")
                    continue

                username = clients[ws]
                room = next(r for r, s in rooms.items() if ws in s)

                print(f"📩 {username}@{room}: {data['message']}")

                await broadcast(room, {
                    "type": "message",
                    "sender": username,
                    "message": data["message"]
                })

    finally:
        username = clients.pop(ws, None)
        if username:
            for r in rooms.values():
                r.discard(ws)
            print(f"❌ {username} disconnected")

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("🚀 Server running at ws://localhost:8765")
        await asyncio.Future()

asyncio.run(main())
