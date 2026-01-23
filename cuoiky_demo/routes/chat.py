import json
from typing import Set, Dict
from datetime import datetime

class ChatRoom:
    """Chat room manager"""
    
    def __init__(self, room_id: int, name: str):
        self.room_id = room_id
        self.name = name
        self.clients: Set = set()
        self.typing_users: Set[int] = set()
    
    def add_client(self, websocket):
        """Add client to room"""
        self.clients.add(websocket)
    
    def remove_client(self, websocket):
        """Remove client from room"""
        self.clients.discard(websocket)
    
    async def broadcast(self, message: str, exclude=None):
        """Broadcast message to all clients in room"""
        import asyncio
        tasks = []
        for client in self.clients:
            if client != exclude:
                tasks.append(client.send(message))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_client_count(self) -> int:
        """Get number of clients in room"""
        return len(self.clients)

class ChatManager:
    """Manage multiple chat rooms"""
    
    def __init__(self):
        self.rooms: Dict[int, ChatRoom] = {}
        self.user_rooms: Dict[int, int] = {}  # user_id: room_id
        
        # Create default room
        self.create_room(1, "General")
    
    def create_room(self, room_id: int, name: str) -> ChatRoom:
        """Create new chat room"""
        room = ChatRoom(room_id, name)
        self.rooms[room_id] = room
        return room
    
    def get_room(self, room_id: int) -> ChatRoom:
        """Get chat room by ID"""
        return self.rooms.get(room_id)
    
    def join_room(self, room_id: int, user_id: int, websocket):
        """User joins a room"""
        room = self.get_room(room_id)
        if room:
            room.add_client(websocket)
            self.user_rooms[user_id] = room_id
            return True
        return False
    
    def leave_room(self, user_id: int, websocket):
        """User leaves current room"""
        room_id = self.user_rooms.get(user_id)
        if room_id:
            room = self.get_room(room_id)
            if room:
                room.remove_client(websocket)
            del self.user_rooms[user_id]
    
    def get_user_room(self, user_id: int) -> ChatRoom:
        """Get room that user is currently in"""
        room_id = self.user_rooms.get(user_id)
        if room_id:
            return self.get_room(room_id)
        return None