"""Middleware for authentication and error handling"""

import functools
import json
from logger import get_logger
from routes.auth import AuthManager

logger = get_logger('middleware')


def require_auth(f):
    """Decorator to require authentication"""
    @functools.wraps(f)
    async def decorated_function(*args, **kwargs):
        # Extract token from request (implement based on your framework)
        # This is a placeholder for Flask/Quart middleware
        return await f(*args, **kwargs)
    return decorated_function


class ErrorHandler:
    """Global error handler"""
    
    @staticmethod
    def handle_validation_error(error):
        """Handle validation errors"""
        logger.warning(f"Validation error: {error}")
        return {
            'status': 'error',
            'message': str(error),
            'code': 400
        }
    
    @staticmethod
    def handle_auth_error(error):
        """Handle authentication errors"""
        logger.warning(f"Auth error: {error}")
        return {
            'status': 'error',
            'message': 'Authentication failed',
            'code': 401
        }
    
    @staticmethod
    def handle_server_error(error):
        """Handle server errors"""
        logger.error(f"Server error: {error}")
        return {
            'status': 'error',
            'message': 'Internal server error',
            'code': 500
        }


class RateLimiter:
    """Simple rate limiter"""
    
    def __init__(self, max_requests=100, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}  # {user_id: [timestamps]}
    
    def is_allowed(self, user_id: int) -> bool:
        """Check if user is allowed to make request"""
        import time
        
        current_time = time.time()
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Remove old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if current_time - req_time < self.time_window
        ]
        
        # Check if within limit
        if len(self.requests[user_id]) < self.max_requests:
            self.requests[user_id].append(current_time)
            return True
        
        logger.warning(f"Rate limit exceeded for user {user_id}")
        return False


class CORSMiddleware:
    """CORS middleware for Flask/Quart"""
    
    @staticmethod
    def add_cors_headers(response):
        """Add CORS headers to response"""
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response


# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=100, time_window=60)
