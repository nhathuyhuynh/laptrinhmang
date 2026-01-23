from typing import Dict, List, Optional
import json

class APIResponse:
    """API Response helper"""
    
    @staticmethod
    def success(data: any = None, message: str = "Success") -> str:
        """Success response"""
        return json.dumps({
            'status': 'success',
            'message': message,
            'data': data
        })
    
    @staticmethod
    def error(message: str, code: int = 400) -> str:
        """Error response"""
        return json.dumps({
            'status': 'error',
            'message': message,
            'code': code
        })
    
    @staticmethod
    def unauthorized(message: str = "Unauthorized") -> str:
        """Unauthorized response"""
        return json.dumps({
            'status': 'error',
            'message': message,
            'code': 401
        })

class MessageHandler:
    """Handle different message types"""
    
    @staticmethod
    def format_text_message(content: str, user_id: int, username: str) -> dict:
        """Format text message"""
        return {
            'type': 'message',
            'message_type': 'text',
            'content': content,
            'user_id': user_id,
            'username': username,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def format_system_message(content: str) -> dict:
        """Format system message"""
        return {
            'type': 'system',
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def format_typing_indicator(user_id: int, username: str, is_typing: bool) -> dict:
        """Format typing indicator"""
        return {
            'type': 'typing',
            'user_id': user_id,
            'username': username,
            'is_typing': is_typing
        }