from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    """User model"""
    id: int
    username: str
    email: Optional[str] = None
    password_hash: str = ""
    avatar: Optional[str] = None
    status: str = "offline"  # online, offline, away
    created_at: datetime = None
    last_seen: datetime = None
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar': self.avatar,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }
    
    def to_public_dict(self):
        """Convert to public dictionary (without sensitive data)"""
        return {
            'id': self.id,
            'username': self.username,
            'avatar': self.avatar,
            'status': self.status
        }