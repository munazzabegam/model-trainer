import sqlite3

DB_NAME = "data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            data_field TEXT,
            labels TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_model_metadata(name, data_field, labels):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO models (name, data_field, labels) VALUES (?, ?, ?)",
        (name, data_field, labels)
    )
    model_id = c.lastrowid
    conn.commit()
    conn.close()
    return model_id

def get_all_models():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM models")
    models = c.fetchall()
    conn.close()
    return models

def get_model_details(model_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM models WHERE id=?", (model_id,))
    model = c.fetchone()
    conn.close()
    return model
