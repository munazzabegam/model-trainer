import os
import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

def train_and_save_model(df, model_dir, data_field):
    X = df[data_field]
    y = df['label']

    vectorizer = CountVectorizer()
    X_vec = vectorizer.fit_transform(X)

    model = MultinomialNB()
    model.fit(X_vec, y)

    joblib.dump(model, os.path.join(model_dir, 'model.pkl'))
    joblib.dump(vectorizer, os.path.join(model_dir, 'vectorizer.pkl'))

def load_model_and_predict(model_dir, text):
    model = joblib.load(os.path.join(model_dir, 'model.pkl'))
    vectorizer = joblib.load(os.path.join(model_dir, 'vectorizer.pkl'))

    X_vec = vectorizer.transform([text])
    return model.predict(X_vec)[0]
