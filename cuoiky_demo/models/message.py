from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Message:
    """Message model"""
    id: Optional[int] = None
    user_id: int = 0
    room_id: int = 1
    content: str = ""
    message_type: str = "text"  # text, image, file, system
    timestamp: datetime = None
    edited: bool = False
    reply_to: Optional[int] = None
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'room_id': self.room_id,
            'content': self.content,
            'message_type': self.message_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'edited': self.edited,
            'reply_to': self.reply_to
        }