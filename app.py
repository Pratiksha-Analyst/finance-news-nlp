from fastapi import FastAPI
from predict import predict_news  # this must match your predict.py

app = FastAPI(title="Financial News NLP API")  # <-- the variable must be named app

@app.get("/")
def home():
    return {"message": "API is running"}

@app.post("/predict")
def predict(text: str):
    result = predict_news(text)
    return result


