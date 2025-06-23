import sqlite3
from flask import request

DB_FILE = 'visitors.db'

# إنشاء الجدول لو لم يكن موجودًا
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visitors (
            ip TEXT PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# تسجيل الزائر الفريد
def count_unique_visitor():
    ip = request.remote_addr
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM visitors WHERE ip = ?', (ip,))
    exists = cursor.fetchone()
    if not exists:
        cursor.execute('INSERT INTO visitors (ip) VALUES (?)', (ip,))
        conn.commit()
    conn.close()

# عرض العدد الإجمالي
def get_visitor_count():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM visitors')
    count = cursor.fetchone()[0]
    conn.close()
    return count
