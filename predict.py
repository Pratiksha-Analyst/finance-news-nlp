import pickle
from textblob import TextBlob
from utils import clean_text

# Load saved model and vectorizer
model = pickle.load(open("model/model.pkl", "rb"))
vectorizer = pickle.load(open("model/vectorizer.pkl", "rb"))

# Function to predict topic and sentiment
def predict_news(text):
    cleaned = clean_text(text)
    vec = vectorizer.transform([cleaned])
    topic = model.predict(vec)[0]
    sentiment = TextBlob(text).sentiment.polarity  # -1 = negative, 0 = neutral, +1 = positive
    return {"topic": topic, "sentiment": round(sentiment, 3)}

# Quick test if run directly
if __name__ == "__main__":
    text = input("Enter news text: ")
    print(predict_news(text))
