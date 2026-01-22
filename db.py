import sqlite3

conn = sqlite3.connect("chat.db", check_same_thread=False)
cur = conn.cursor()

def init_db():
    # Bảng messages
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room TEXT,
        sender TEXT,
        message TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Bảng users
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Thêm user mặc định
    try:
        cur.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", 
                   ("admin", "admin123"))
    except:
        pass
    
    conn.commit()

def save_message(room, sender, message):
    cur.execute(
        "INSERT INTO messages (room, sender, message) VALUES (?,?,?)",
        (room, sender, message)
    )
    conn.commit()

def load_messages(room):
    cur.execute(
        "SELECT sender, message FROM messages WHERE room=? ORDER BY id",
        (room,)
    )
    rows = cur.fetchall()
    return [{"sender": r[0], "message": r[1]} for r in rows]

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
    cur.execute(
        "SELECT 1 FROM users WHERE username=? AND password=?",
        (username, password)
    )
    return cur.fetchone() is not None