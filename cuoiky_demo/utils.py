"""Utility functions"""
import os
import json
from typing import Any, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation error"""
    pass


def validate_username(username: str) -> bool:
    """Validate username format"""
    if not isinstance(username, str):
        raise ValidationError("Username must be string")
    
    if len(username) < 3 or len(username) > 20:
        raise ValidationError("Username must be between 3 and 20 characters")
    
    if not username.replace('_', '').replace('-', '').isalnum():
        raise ValidationError("Username can only contain alphanumeric characters, hyphens, and underscores")
    
    return True


def validate_email(email: str) -> bool:
    """Validate email format"""
    if not isinstance(email, str):
        raise ValidationError("Email must be string")
    
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError("Invalid email format")
    
    return True


def validate_password(password: str) -> bool:
    """Validate password strength"""
    if not isinstance(password, str):
        raise ValidationError("Password must be string")
    
    if len(password) < 6:
        raise ValidationError("Password must be at least 6 characters")
    
    return True


def validate_message(message: str) -> bool:
    """Validate message content"""
    if not isinstance(message, str):
        raise ValidationError("Message must be string")
    
    if len(message) == 0 or len(message.strip()) == 0:
        raise ValidationError("Message cannot be empty")
    
    if len(message) > 5000:
        raise ValidationError("Message too long (max 5000 characters)")
    
    return True


def create_upload_folder():
    """Create upload folder if not exists"""
    upload_folder = 'static/uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        logger.info(f"Created upload folder: {upload_folder}")


def is_allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in allowed_extensions


def get_file_size_mb(file_size_bytes: int) -> float:
    """Convert bytes to MB"""
    return file_size_bytes / (1024 * 1024)


def parse_json(data: str) -> Dict[str, Any]:
    """Parse JSON string safely"""
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return {}


def format_timestamp(dt: datetime = None) -> str:
    """Format datetime to ISO format"""
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()


def get_client_info(websocket) -> Dict[str, str]:
    """Extract client connection info"""
    try:
        remote_addr = websocket.remote_address[0]
        remote_port = websocket.remote_address[1]
        return {
            'ip': remote_addr,
            'port': str(remote_port),
            'addr': f"{remote_addr}:{remote_port}"
        }
    except Exception as e:
        logger.error(f"Error getting client info: {e}")
        return {'ip': 'unknown', 'port': 'unknown', 'addr': 'unknown'}


def get_ssl_info(websocket) -> Dict[str, str]:
    """Extract SSL/TLS information"""
    try:
        if hasattr(websocket, 'transport') and websocket.transport:
            ssl_obj = websocket.transport.get_extra_info('ssl_object')
            if ssl_obj:
                return {
                    'protocol': ssl_obj.version(),
                    'cipher': ssl_obj.cipher()[0] if ssl_obj.cipher() else 'unknown'
                }
    except Exception as e:
        logger.error(f"Error getting SSL info: {e}")
    
    return {'protocol': 'none', 'cipher': 'none'}
