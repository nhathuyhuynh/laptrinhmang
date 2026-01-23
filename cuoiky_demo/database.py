import sqlite3
from datetime import datetime
from typing import List, Optional, Dict
import json

class Database:
    """Database manager using SQLite"""
    
    def __init__(self, db_path: str = 'chat.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                password_hash TEXT NOT NULL,
                avatar TEXT,
                status TEXT DEFAULT 'offline',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP
            )
        ''')
        
        # Rooms table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_by INTEGER,
                is_private BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(created_by) REFERENCES users(id)
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                room_id INTEGER DEFAULT 1,
                content TEXT NOT NULL,
                message_type TEXT DEFAULT 'text',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                edited BOOLEAN DEFAULT 0,
                reply_to INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(room_id) REFERENCES rooms(id),
                FOREIGN KEY(reply_to) REFERENCES messages(id)
            )
        ''')
        
        # Room members table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS room_members (
                room_id INTEGER,
                user_id INTEGER,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(room_id, user_id),
                FOREIGN KEY(room_id) REFERENCES rooms(id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        
        # Create default room if not exists
        cursor.execute('SELECT id FROM rooms WHERE id = 1')
        if not cursor.fetchone():
            cursor.execute(
                'INSERT INTO rooms (id, name, description) VALUES (?, ?, ?)',
                (1, 'General', 'Default chat room')
            )
        
        conn.commit()
        conn.close()
    
    # User operations
    def create_user(self, username: str, password_hash: str, email: str = None) -> Optional[int]:
        """Create new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
                (username, password_hash, email)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def update_user_status(self, user_id: int, status: str):
        """Update user online status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET status = ?, last_seen = ? WHERE id = ?',
            (status, datetime.now(), user_id)
        )
        conn.commit()
        conn.close()
    
    def get_online_users(self) -> List[Dict]:
        """Get all online users"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, avatar, status FROM users WHERE status = ?', ('online',))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # Message operations
    def save_message(self, user_id: int, room_id: int, content: str, message_type: str = 'text') -> Optional[int]:
        """Save message to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO messages (user_id, room_id, content, message_type) VALUES (?, ?, ?, ?)',
            (user_id, room_id, content, message_type)
        )
        conn.commit()
        message_id = cursor.lastrowid
        conn.close()
        return message_id
    
    def get_messages(self, room_id: int, limit: int = 50) -> List[Dict]:
        """Get messages from room"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT m.*, u.username, u.avatar
            FROM messages m
            JOIN users u ON m.user_id = u.id
            WHERE m.room_id = ?
            ORDER BY m.timestamp DESC
            LIMIT ?
        ''', (room_id, limit))
        rows = cursor.fetchall()
        conn.close()
        messages = [dict(row) for row in rows]
        return list(reversed(messages))  # Chronological order
    
    def delete_message(self, message_id: int, user_id: int) -> bool:
        """Delete message (only by owner)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM messages WHERE id = ? AND user_id = ?',
            (message_id, user_id)
        )
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted
    
    # Room operations
    def create_room(self, name: str, created_by: int, description: str = None, is_private: bool = False) -> Optional[int]:
        """Create new room"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO rooms (name, description, created_by, is_private) VALUES (?, ?, ?, ?)',
                (name, description, created_by, is_private)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_rooms(self) -> List[Dict]:
        """Get all public rooms"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, u.username as creator_name,
                   (SELECT COUNT(*) FROM room_members WHERE room_id = r.id) as member_count
            FROM rooms r
            LEFT JOIN users u ON r.created_by = u.id
            WHERE r.is_private = 0
            ORDER BY r.created_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def join_room(self, room_id: int, user_id: int):
        """User joins room"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO room_members (room_id, user_id) VALUES (?, ?)',
                (room_id, user_id)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # Already a member
        finally:
            conn.close()
    
    def leave_room(self, room_id: int, user_id: int):
        """User leaves room"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM room_members WHERE room_id = ? AND user_id = ?',
            (room_id, user_id)
        )
        conn.commit()
        conn.close()