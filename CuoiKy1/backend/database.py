import mysql.connector
from datetime import datetime

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="chat_db"
)

def check_login(u, p):
    cur = db.cursor()
    cur.execute(
        "SELECT role FROM users WHERE username=%s AND password=%s",
        (u, p)
    )
    r = cur.fetchone()
    return r[0] if r else None

def register_user(u, p):
    cur = db.cursor()
    cur.execute(
        "INSERT INTO users (username,password) VALUES (%s,%s)",
        (u, p)
    )
    db.commit()

def save_message(u, m):
    cur = db.cursor()
    cur.execute(
        "INSERT INTO messages (username,content,time) VALUES (%s,%s,%s)",
        (u, m, datetime.now().strftime("%H:%M:%S"))
    )
    db.commit()

def load_messages():
    cur = db.cursor()
    cur.execute(
        "SELECT username,content,time FROM messages ORDER BY id DESC LIMIT 50"
    )
    return cur.fetchall()[::-1]
