# model_manager.py
import pandas as pd
import os
from database import get_all_data_for_export # IMPORTANT: Now uses the combined data function
from model_trainer import train_and_save_model, load_model_and_predict

BASE_MODELS_DIR = "models" 

def get_model_dir(model_name):
    safe_name = model_name.lower().replace(' ', '_').replace('/', '_')
    return os.path.join(BASE_MODELS_DIR, safe_name)

def train_model_from_db(model_id, model_name, data_field):
    """
    Fetches ALL data (original + confirmed feedback) from the DB, 
    prepares a DataFrame, and triggers training.
    """
    data_tuples = get_all_data_for_export(model_id) # Uses combined data

    if not data_tuples:
        print(f"No data found for model ID {model_id}. Training aborted.")
        return False

    # Data is (Input Text, Label, Source). We map the first two elements.
    data_for_df = [(text, label) for text, label, source in data_tuples]
    
    df = pd.DataFrame(data_for_df, columns=['data_value', 'label'])
    
    # Rename 'data_value' to match the model's required 'data_field'
    df.rename(columns={'data_value': data_field}, inplace=True)
    
    model_dir = get_model_dir(model_name)
    
    try:
        train_and_save_model(df, model_dir, data_field)
        return True
    except ValueError as e:
        print(f"Training failed (Data Error): {e}")
        return False
    except Exception as e:
        print(f"Error during training for model '{model_name}': {e}")
        return False

def predict_model(model_name, text):
    model_dir = get_model_dir(model_name)
    
    try:
        return load_model_and_predict(model_dir, text)
    except FileNotFoundError:
        return "Model not trained yet."
    except Exception as e:
        return f"Prediction Error: {e}"