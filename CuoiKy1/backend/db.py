import sqlite3

# Kết nối database
conn = sqlite3.connect("chat.db", check_same_thread=False)
cur = conn.cursor()

def init_db():
    # Bảng messages (Lưu tin nhắn)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room TEXT,
        sender TEXT,
        message TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Bảng users (Lưu tài khoản)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Tạo user mẫu admin
    try:
        cur.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", 
                   ("admin", "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918")) # pass: admin
    except:
        pass
    
    conn.commit()

def save_message(room, sender, message):
    # Thời gian sẽ tự động được SQLite điền vào cột created_at
    cur.execute(
        "INSERT INTO messages (room, sender, message) VALUES (?,?,?)",
        (room, sender, message)
    )
    conn.commit()

def load_messages(room):
    # 🔥 SỬA: Lấy thêm cột thời gian đã được định dạng HH:MM
    cur.execute("""
        SELECT sender, message, strftime('%H:%M', created_at, 'localtime') 
        FROM messages 
        WHERE room=? 
        ORDER BY id
    """, (room,))
    
    rows = cur.fetchall()
    # Trả về có cả 'time' để Frontend hiển thị đúng giờ cũ
    return [{"sender": r[0], "message": r[1], "time": r[2]} for r in rows]

def check_user(username):
    cur.execute("SELECT 1 FROM users WHERE username=?", (username,))
    return cur.fetchone() is not None

def create_user(username, password):
    cur.execute(
        "INSERT INTO users (username, password) VALUES (?,?)",
        (username, password)
    )
    conn.commit()

def verify_user(username, password):
    # Password truyền vào phải là hash rồi (xử lý ở server.py)
    cur.execute(
        "SELECT 1 FROM users WHERE username=? AND password=?",
        (username, password)
    )
    return cur.fetchone() is not None