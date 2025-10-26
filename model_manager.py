import os
import pandas as pd
import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from database import fetch_data

def train_model(model_folder):
    db_path = os.path.join(model_folder, "data.db")
    data = fetch_data(db_path)
    if not data:
        return "No data to train!"

    texts, labels = zip(*data)
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(texts)

    model = MultinomialNB()
    model.fit(X, labels)

    joblib.dump((vectorizer, model), os.path.join(model_folder, "model.pkl"))

    df = pd.DataFrame(data, columns=["text", "label"])
    df.to_excel(os.path.join(model_folder, "dataset.xlsx"), index=False)

    return "Model trained successfully!"

def predict(model_folder, text):
    model_path = os.path.join(model_folder, "model.pkl")
    if not os.path.exists(model_path):
        return "Model not trained yet!"
    
    vectorizer, model = joblib.load(model_path)
    X = vectorizer.transform([text])
    prediction = model.predict(X)[0]
    return prediction
