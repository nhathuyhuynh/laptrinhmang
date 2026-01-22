import asyncio
import websockets
import ssl
import json
from datetime import datetime
import os

# Cấu hình
HOST = "0.0.0.0"
PORT = 8765

# SSL/TLS Configuration
USE_SSL = False  # nơi bật tắt True/False để tắt SSL
CERT_FILE = "certs/server.crt"
KEY_FILE = "certs/server.key"

# Storage
connected_clients = set()
message_history = []
client_stats = {
    "total_connections": 0,
    "total_messages": 0, 
    "peak_concurrent": 0
}

async def broadcast(message):
    """Broadcast message to all connected clients"""
    if connected_clients:
        await asyncio.gather(
            *[client.send(message) for client in connected_clients],
            return_exceptions=True
        )


async def handle_client(websocket):
    """Handle individual client connection"""
    client_addr = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
    
    # Kiểm tra SSL/TLS info
    ssl_info = ""
    try:
        if hasattr(websocket, 'transport') and websocket.transport:
            ssl_obj = websocket.transport.get_extra_info('ssl_object')
            if ssl_obj:
                ssl_version = ssl_obj.version()
                ssl_cipher = ssl_obj.cipher()
                ssl_info = f" [SSL: {ssl_version}, Cipher: {ssl_cipher[0]}]"
    except:
        pass
    
    print(f"[+] Client connected: {client_addr}{ssl_info}")
    
    connected_clients.add(websocket)
    client_stats["total_connections"] += 1
    
    if len(connected_clients) > client_stats["peak_concurrent"]:
        client_stats["peak_concurrent"] = len(connected_clients)
    
    try:
        # Send history
        if message_history:
            await websocket.send(json.dumps({
                "type": "history",
                "messages": message_history[-50:]
            }))
        
        # Send join notification
        join_msg = json.dumps({
            "type": "system",
            "message": f"🔒 Client {client_addr} joined (SSL: {'Yes' if USE_SSL else 'No'})",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "online_users": len(connected_clients),
            "stats": client_stats
        })
        await broadcast(join_msg)
        
        # Listen for messages
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_obj = {
                    "type": "message",
                    "sender": data.get("username", client_addr),
                    "message": data.get("message", ""),
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "encrypted": USE_SSL
                }
                
                message_history.append(msg_obj)
                client_stats["total_messages"] += 1
                
                await broadcast(json.dumps(msg_obj))
                print(f"[{msg_obj['timestamp']}] {msg_obj['sender']}: {msg_obj['message']}")
                
            except json.JSONDecodeError:
                pass
    
    except websockets.exceptions.ConnectionClosed:
        print(f"[!] Client disconnected: {client_addr}")
    except Exception as e:
        print(f"[!] Error with client {client_addr}: {e}")
    finally:
        connected_clients.discard(websocket)
        
        leave_msg = json.dumps({
            "type": "system",
            "message": f"Client {client_addr} left",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "online_users": len(connected_clients)
        })
        await broadcast(leave_msg)
        
        print(f"[-] Client removed: {client_addr}")
        print(f"[*] Online: {len(connected_clients)}")


async def main():
    """Main server function with SSL/TLS support"""
    print("="*80)
    print("🚀 HIGH-PERFORMANCE WEBSOCKET CHAT SERVER WITH SSL/TLS")
    print("="*80)
    
    # Tạo SSL context nếu bật SSL
    ssl_context = None
    
    if USE_SSL:
        # Kiểm tra file certificates có tồn tại không
        if not os.path.exists(CERT_FILE) or not os.path.exists(KEY_FILE):
            print(f"[!] SSL CERTIFICATE NOT FOUND!")
            print(f"[!] Looking for:")
            print(f"    - {CERT_FILE}")
            print(f"    - {KEY_FILE}")
            print(f"[*] Running without SSL/TLS...")
            ssl_context = None
        else:
            try:
                # Tạo SSL context
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ssl_context.load_cert_chain(CERT_FILE, KEY_FILE)
                
                # Optional: Cấu hình SSL nâng cao
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                print(f"[✓] SSL/TLS ENABLED")
                print(f"    Certificate: {CERT_FILE}")
                print(f"    Private Key: {KEY_FILE}")
                print(f"    Protocol: {ssl_context.protocol}")
            except Exception as e:
                print(f"[!] SSL ERROR: {e}")
                print(f"[*] Running without SSL/TLS...")
                ssl_context = None
    
    # Hiển thị thông tin server
    protocol = "wss" if ssl_context else "ws"
    print(f"[+] Host: {HOST}")
    print(f"[+] Port: {PORT}")
    print(f"[+] Protocol: {protocol}://")
    print(f"[+] URL: {protocol}://localhost:{PORT}")
    print(f"[+] Security: {'🔒 ENCRYPTED' if ssl_context else '🔓 PLAIN TEXT'}")
    print("="*80)
    
    # Khởi động server với hoặc không có SSL
    async with websockets.serve(
        handle_client, 
        HOST, 
        PORT,
        ssl=ssl_context,
        # Performance optimizations
        max_size=10 * 1024 * 1024,
        max_queue=100,
        ping_interval=20,
        ping_timeout=20
    ):
        print(f"[✓] Server running! Waiting for connections...")
        print(f"[*] SSL/TLS: {'ENABLED ✅' if ssl_context else 'DISABLED ❌'}")
        print(f"[*] Press Ctrl+C to stop\n")
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Server stopped")
        print(f"[📊] Final Stats:")
        print(f"    Total Connections: {client_stats['total_connections']}")
        print(f"    Total Messages: {client_stats['total_messages']}")
        print(f"    Peak Concurrent: {client_stats['peak_concurrent']}")