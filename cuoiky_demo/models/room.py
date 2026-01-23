from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Set

@dataclass
class Room:
    """Chat room model"""
    id: int
    name: str
    description: Optional[str] = None
    created_by: int = 0
    created_at: datetime = None
    is_private: bool = False
    members: Set[int] = None
    
    def __post_init__(self):
        if self.members is None:
            self.members = set()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_private': self.is_private,
            'member_count': len(self.members)
        }
    
    def add_member(self, user_id: int):
        """Add member to room"""
        self.members.add(user_id)
    
    def remove_member(self, user_id: int):
        """Remove member from room"""
        self.members.discard(user_id)
    
    def is_member(self, user_id: int) -> bool:
        """Check if user is member"""
        return user_id in self.members