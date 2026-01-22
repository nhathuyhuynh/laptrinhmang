import sqlite3

conn = sqlite3.connect("chat.db", check_same_thread=False)
cur = conn.cursor()

def init_db():
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room TEXT,
        sender TEXT,
        message TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
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
