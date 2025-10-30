# database.py
import sqlite3

DB_NAME = "data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Table 1: Model Metadata
    c.execute("""
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            data_field TEXT,   
            labels TEXT        
        )
    """)
    # Table 2: Original Model Data
    c.execute("""
        CREATE TABLE IF NOT EXISTS model_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id INTEGER NOT NULL,
            data_value TEXT NOT NULL,
            label TEXT NOT NULL,
            FOREIGN KEY (model_id) REFERENCES models (id)
        )
    """)
    # Table 3: Prediction and Feedback (NEW)
    c.execute("""
        CREATE TABLE IF NOT EXISTS prediction_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id INTEGER NOT NULL,
            input_text TEXT NOT NULL,
            predicted_label TEXT,
            is_correct INTEGER,       
            true_label TEXT,          
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (model_id) REFERENCES models (id)
        )
    """)
    conn.commit()
    conn.close()

def save_model_metadata(name, data_field, labels):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO models VALUES (NULL, ?, ?, ?)",
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

def save_model_data(model_id, data_value, label):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO model_data (model_id, data_value, label) VALUES (?, ?, ?)",
        (model_id, data_value, label)
    )
    conn.commit()
    conn.close()

def get_data_for_model(model_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT data_value, label FROM model_data WHERE model_id=?", (model_id,))
    data = c.fetchall()
    conn.close()
    return data

# NEW FUNCTION: Log the initial prediction
def log_prediction(model_id, input_text, predicted_label):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO prediction_feedback (model_id, input_text, predicted_label) VALUES (?, ?, ?)",
        (model_id, input_text, predicted_label)
    )
    prediction_id = c.lastrowid
    conn.commit()
    conn.close()
    return prediction_id 

# NEW FUNCTION: Update the prediction with user feedback
def update_prediction_feedback(prediction_id, is_correct, true_label):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "UPDATE prediction_feedback SET is_correct=?, true_label=? WHERE id=?",
        (is_correct, true_label, prediction_id)
    )
    conn.commit()
    conn.close()

# NEW/UPDATED FUNCTION: Get ALL data (training + feedback) for export/retraining
def get_all_data_for_export(model_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # 1. Collect all original training data
    c.execute("SELECT data_value, label, 'Original Training' FROM model_data WHERE model_id=?", (model_id,))
    original_data = c.fetchall()

    # 2. Collect all good feedback data (where a true label was provided for retraining)
    # We use true_label as the label for retraining purposes
    c.execute("SELECT input_text, true_label, 'User Feedback' FROM prediction_feedback WHERE model_id=? AND true_label IS NOT NULL", (model_id,))
    feedback_data = c.fetchall()

    conn.close()
    # Combine the data for export/retraining
    return original_data + feedback_data

def delete_all_data():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Delete data
    c.execute("DELETE FROM model_data")
    c.execute("DELETE FROM models")
    c.execute("DELETE FROM prediction_feedback") # DELETE NEW TABLE DATA
    
    # Reset primary key counters
    c.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='models'")
    c.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='model_data'")
    c.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='prediction_feedback'")

    conn.commit()
    conn.close()