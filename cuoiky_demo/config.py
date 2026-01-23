import os
from datetime import timedelta

class Config:
    """Application configuration"""
    
    # Server
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8765))
    
    # SSL/TLS
    USE_SSL = os.getenv('USE_SSL', 'False').lower() == 'true'
    CERT_FILE = os.getenv('CERT_FILE', 'certs/server.crt')
    KEY_FILE = os.getenv('KEY_FILE', 'certs/server.key')
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'chat.db')
    
    # Authentication
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    TOKEN_EXPIRY = timedelta(days=7)
    
    # File Upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'doc', 'docx'}
    
    # Chat
    MAX_MESSAGE_LENGTH = 5000
    MESSAGE_HISTORY_LIMIT = 50
    
    @staticmethod
    def allowed_file(filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS