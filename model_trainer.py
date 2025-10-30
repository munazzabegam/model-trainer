# model_trainer.py
import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

def train_and_save_model(df: pd.DataFrame, model_dir: str, data_field: str):
    """
    Trains a Multinomial Naive Bayes model using the specified data_field column.
    """
    
    if df.empty:
        raise ValueError("Cannot train model: Input DataFrame is empty.")

    X = df[data_field].astype(str)
    y = df['label']

    vectorizer = CountVectorizer()
    X_vec = vectorizer.fit_transform(X)

    model = MultinomialNB()
    model.fit(X_vec, y)

    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(model, os.path.join(model_dir, 'model.pkl'))
    joblib.dump(vectorizer, os.path.join(model_dir, 'vectorizer.pkl'))

def load_model_and_predict(model_dir: str, text: str):
    """
    Loads a saved model and vectorizer to make a prediction.
    """
    
    model_path = os.path.join(model_dir, 'model.pkl')
    vectorizer_path = os.path.join(model_dir, 'vectorizer.pkl')

    if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
        raise FileNotFoundError(f"Model or vectorizer not found in {model_dir}.")

    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)

    X_vec = vectorizer.transform([text])
    
    return model.predict(X_vec)[0]