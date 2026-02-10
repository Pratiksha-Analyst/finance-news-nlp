import pandas as pd
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from utils import clean_text

# -----------------------------
# Mini dataset (no CSV needed)
# -----------------------------
data = {
    "text": [
        "Stock markets rise after strong earnings",
        "Government passes new law in parliament",
        "New AI technology released",
        "Football team wins championship",
        "New movie becomes a blockbuster"
    ],
    "category": [
        "Business",
        "Politics",
        "Tech",
        "Sports",
        "Entertainment"
    ]
}

df = pd.DataFrame(data)
df["text"] = df["text"].apply(clean_text)

X_train, X_test, y_train, y_test = train_test_split(df["text"], df["category"], test_size=0.2, random_state=42)

vectorizer = TfidfVectorizer(max_features=500)
X_train_vec = vectorizer.fit_transform(X_train)

model = LogisticRegression(max_iter=200)
model.fit(X_train_vec, y_train)

os.makedirs("model", exist_ok=True)
pickle.dump(model, open("model/model.pkl", "wb"))
pickle.dump(vectorizer, open("model/vectorizer.pkl", "wb"))

print("✅ Model trained and saved.")
