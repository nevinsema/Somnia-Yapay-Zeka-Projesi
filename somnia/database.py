import sqlite3
from datetime import datetime
import hashlib

DATABASE_NAME = "somnia.db"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_db():
    return sqlite3.connect(DATABASE_NAME, check_same_thread=False)

def create_tables():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        username        TEXT UNIQUE,
        password_hash   TEXT,
        sec_question    TEXT,
        sec_answer_hash TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sleep_history (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id         INTEGER,
        date            TEXT,
        bed_time        TEXT,
        wake_time       TEXT,
        sleep_efficiency REAL,
        sleep_minutes   INTEGER,
        predicted_eff   REAL,
        
        caffeine        INTEGER,
        alcohol         INTEGER,
        smoking         INTEGER,
        exercise        INTEGER,
        
        ideal_bedtime   INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()

def register_user(username, password, sec_q, sec_a):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password_hash, sec_question, sec_answer_hash) VALUES (?, ?, ?, ?)", 
                    (username, hash_password(password), sec_q, hash_password(sec_a)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_login(username, password):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()
    if row and row[1] == hash_password(password):
        return row[0]
    return None

def get_security_question(username):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT sec_question FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def check_security_answer(username, answer):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT sec_answer_hash FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()
    if row and row[0] == hash_password(answer):
        return True
    return False

def update_password(username, new_pw):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET password_hash=? WHERE username=?", (hash_password(new_pw), username))
    conn.commit()
    conn.close()

def insert_sleep_record(user_id, bed_time, wake_time, sleep_efficiency, sleep_minutes, 
                        predicted_eff, caffeine, alcohol, smoking, exercise, ideal_bedtime):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO sleep_history (
        user_id, date, bed_time, wake_time, sleep_efficiency,
        sleep_minutes, predicted_eff,
        caffeine, alcohol, smoking, exercise, ideal_bedtime
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        bed_time,
        wake_time,
        sleep_efficiency,
        sleep_minutes,
        predicted_eff,
        caffeine,
        alcohol,
        smoking,
        exercise,
        ideal_bedtime,
    ))
    conn.commit()
    conn.close()

def fetch_all_records(user_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT date, bed_time, wake_time, sleep_efficiency,
               predicted_eff, caffeine, alcohol, smoking, exercise
        FROM sleep_history
        WHERE user_id = ?
        ORDER BY date DESC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_model_stats(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM sleep_history WHERE user_id = ?", (user_id,))
    count = cur.fetchone()[0]
    
    cur.execute("""
        SELECT sleep_efficiency, predicted_eff 
        FROM sleep_history 
        WHERE user_id = ? 
        ORDER BY id DESC LIMIT 1
    """, (user_id,))
    last_row = cur.fetchone()
    conn.close()
    
    if last_row:
        loss = abs(last_row[0] - last_row[1])
        return {
            "total_records": count,
            "last_real": last_row[0],
            "last_pred": last_row[1],
            "loss": loss,
            "has_data": True
        }
    else:
        return {"has_data": False}

def get_last_sleep_detail(user_id):
    """Chatbot ve Ana Sayfa önerisi için detaylı veri çeker."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT sleep_efficiency, sleep_minutes, caffeine, alcohol, smoking, exercise, wake_time
        FROM sleep_history
        WHERE user_id = ?
        ORDER BY id DESC LIMIT 1
    """, (user_id,))
    row = cur.fetchone()
    conn.close()
    return row