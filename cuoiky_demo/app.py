"""
WebSocket Chat Server with SSL/TLS Support
Main Application Entry Point
"""

import os
import sys
import asyncio
import websockets
import ssl
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import custom modules
from config import Config
from database import Database
from routes.auth import AuthManager
from routes.chat import ChatManager
from logger import get_logger
from utils import create_upload_folder, get_client_info, get_ssl_info, parse_json

# Initialize logger
logger = get_logger('main')

# Initialize managers
db = Database(Config.DATABASE_PATH)
auth_manager = AuthManager(Config.SECRET_KEY)
chat_manager = ChatManager()

# Global stats
stats = {
    "total_connections": 0,
    "total_messages": 0,
    "peak_concurrent": 0,
    "active_clients": 0,
    "start_time": datetime.now()
}

# Active clients mapping
active_clients = {}  # {websocket: {'user_id': int, 'username': str, 'room_id': int}}


async def broadcast_to_room(room_id: int, message: dict, exclude_websocket=None):
    """Broadcast message to all clients in a room"""
    room = chat_manager.rooms.get(room_id)
    if not room:
        return
    
    message_json = json.dumps(message)
    tasks = []
    
    for client in room.clients:
        if client != exclude_websocket:
            tasks.append(client.send(message_json))
    
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


async def handle_client(websocket, path):
    """Handle WebSocket client connection"""
    client_addr = get_client_info(websocket)
    ssl_info = get_ssl_info(websocket)
    
    logger.info(f"[+] Client connected: {client_addr['addr']} (SSL: {ssl_info['protocol']})")
    
    stats["total_connections"] += 1
    stats["active_clients"] += 1
    
    user_id = None
    username = None
    room_id = 1  # Default room
    
    try:
        async for message_str in websocket:
            try:
                message_data = parse_json(message_str)
                message_type = message_data.get('type')
                
                # Handle authentication
                if message_type == 'auth':
                    token = message_data.get('token')
                    if token:
                        payload = auth_manager.verify_token(token)
                        if payload:
                            user_id = payload.get('user_id')
                            username = payload.get('username')
                            active_clients[websocket] = {
                                'user_id': user_id,
                                'username': username,
                                'room_id': room_id
                            }
                            
                            # Add client to room
                            chat_manager.add_user_to_room(user_id, room_id)
                            room = chat_manager.rooms[room_id]
                            room.add_client(websocket)
                            
                            logger.info(f"[AUTH] User {username} (ID: {user_id}) authenticated")
                            
                            # Send message history
                            await websocket.send(json.dumps({
                                'type': 'history',
                                'room_id': room_id,
                                'messages': []  # TODO: Get from database
                            }))
                            
                            # Broadcast user joined
                            await broadcast_to_room(room_id, {
                                'type': 'system',
                                'message': f'👤 {username} vừa tham gia',
                                'timestamp': datetime.now().isoformat(),
                                'room_id': room_id
                            }, exclude_websocket=websocket)
                        else:
                            await websocket.send(json.dumps({
                                'type': 'error',
                                'message': 'Invalid or expired token'
                            }))
                
                # Handle chat message
                elif message_type == 'message' and user_id:
                    content = message_data.get('content', '').strip()
                    
                    if content and len(content) <= Config.MAX_MESSAGE_LENGTH:
                        # Save to database
                        # TODO: db.create_message(user_id, room_id, content)
                        
                        stats["total_messages"] += 1
                        
                        # Broadcast message
                        await broadcast_to_room(room_id, {
                            'type': 'message',
                            'user_id': user_id,
                            'username': username,
                            'content': content,
                            'timestamp': datetime.now().isoformat(),
                            'room_id': room_id
                        })
                        
                        logger.info(f"[MSG] {username}: {content}")
                    else:
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'message': 'Invalid message length'
                        }))
                
                # Handle typing indicator
                elif message_type == 'typing' and user_id:
                    room = chat_manager.rooms.get(room_id)
                    if room:
                        room.typing_users.add(user_id)
                        await broadcast_to_room(room_id, {
                            'type': 'typing',
                            'username': username,
                            'is_typing': True,
                            'room_id': room_id
                        })
                
                # Handle stop typing
                elif message_type == 'stop_typing' and user_id:
                    room = chat_manager.rooms.get(room_id)
                    if room:
                        room.typing_users.discard(user_id)
                        await broadcast_to_room(room_id, {
                            'type': 'typing',
                            'username': username,
                            'is_typing': False,
                            'room_id': room_id
                        })
                
                # Handle room change
                elif message_type == 'join_room' and user_id:
                    new_room_id = message_data.get('room_id', 1)
                    
                    # Leave old room
                    old_room = chat_manager.rooms.get(room_id)
                    if old_room:
                        old_room.remove_client(websocket)
                        await broadcast_to_room(room_id, {
                            'type': 'system',
                            'message': f'👤 {username} đã rời đi',
                            'timestamp': datetime.now().isoformat(),
                            'room_id': room_id
                        })
                    
                    # Join new room
                    room_id = new_room_id
                    chat_manager.add_user_to_room(user_id, room_id)
                    new_room = chat_manager.rooms[room_id]
                    new_room.add_client(websocket)
                    
                    if websocket in active_clients:
                        active_clients[websocket]['room_id'] = room_id
                    
                    # Notify new room
                    await broadcast_to_room(room_id, {
                        'type': 'system',
                        'message': f'👤 {username} vừa tham gia',
                        'timestamp': datetime.now().isoformat(),
                        'room_id': room_id
                    }, exclude_websocket=websocket)
                
                # Handle get online users
                elif message_type == 'get_users' and user_id:
                    room = chat_manager.rooms.get(room_id)
                    if room:
                        online_users = []
                        for client in room.clients:
                            if client in active_clients:
                                online_users.append(active_clients[client]['username'])
                        
                        await websocket.send(json.dumps({
                            'type': 'users_list',
                            'users': online_users,
                            'count': len(online_users),
                            'room_id': room_id
                        }))
                
                # Handle get stats
                elif message_type == 'get_stats':
                    uptime = datetime.now() - stats['start_time']
                    await websocket.send(json.dumps({
                        'type': 'stats',
                        'total_connections': stats['total_connections'],
                        'total_messages': stats['total_messages'],
                        'active_clients': stats['active_clients'],
                        'peak_concurrent': stats['peak_concurrent'],
                        'uptime': str(uptime).split('.')[0]
                    }))
            
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from {client_addr['addr']}")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"[!] Client disconnected: {client_addr['addr']}")
    except Exception as e:
        logger.error(f"Error in handle_client: {e}")
    
    finally:
        # Clean up
        stats["active_clients"] -= 1
        
        if websocket in active_clients:
            user_info = active_clients[websocket]
            username = user_info['username']
            room_id = user_info['room_id']
            
            # Remove from room
            room = chat_manager.rooms.get(room_id)
            if room:
                room.remove_client(websocket)
                
                # Notify room
                asyncio.create_task(broadcast_to_room(room_id, {
                    'type': 'system',
                    'message': f'👤 {username} đã ngắt kết nối',
                    'timestamp': datetime.now().isoformat(),
                    'room_id': room_id
                }))
            
            del active_clients[websocket]
        
        logger.info(f"Client {client_addr['addr']} cleaned up")


async def main():
    """Main application entry point"""
    logger.info("=" * 60)
    logger.info("WebSocket Chat Server with SSL/TLS")
    logger.info("=" * 60)
    
    # Create upload folder
    create_upload_folder()
    
    # SSL/TLS Configuration
    ssl_context = None
    if Config.USE_SSL and os.path.exists(Config.CERT_FILE) and os.path.exists(Config.KEY_FILE):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(Config.CERT_FILE, Config.KEY_FILE)
        protocol = "wss://"
        logger.info(f"✓ SSL/TLS enabled")
        logger.info(f"✓ Certificate: {Config.CERT_FILE}")
        logger.info(f"✓ Private Key: {Config.KEY_FILE}")
    else:
        protocol = "ws://"
        logger.info(f"⚠ SSL/TLS disabled")
    
    logger.info(f"✓ Starting server on {protocol}{Config.HOST}:{Config.PORT}")
    logger.info(f"✓ Database: {Config.DATABASE_PATH}")
    logger.info(f"✓ Max message length: {Config.MAX_MESSAGE_LENGTH}")
    
    # Start WebSocket server
    async with websockets.serve(handle_client, Config.HOST, Config.PORT, ssl=ssl_context):
        logger.info("✓ Server running... Press Ctrl+C to stop")
        await asyncio.Future()  # Run forever


def print_banner():
    """Print application banner"""
    banner = """
    ╔════════════════════════════════════════════════════════════╗
    ║   WebSocket Chat Server with SSL/TLS & High Performance    ║
    ║                    Made with ❤️  by Team                   ║
    ╚════════════════════════════════════════════════════════════╝
    """
    print(banner)


if __name__ == "__main__":
    print_banner()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n\n[!] Server shutting down...")
        logger.info("Goodbye! 👋")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
