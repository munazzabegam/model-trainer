import sqlite3

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS dataset (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            label TEXT,
            feedback TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_data(db_path, text, label, feedback=None):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('INSERT INTO dataset (text, label, feedback) VALUES (?, ?, ?)', (text, label, feedback))
    conn.commit()
    conn.close()

def fetch_data(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT text, label FROM dataset')
    rows = c.fetchall()
    conn.close()
    return rows
