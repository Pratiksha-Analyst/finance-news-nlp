import os
import re
import pickle
import streamlit as st
import feedparser
from textblob import TextBlob

# -----------------------------
# Text cleaning
# -----------------------------
def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-zA-Z ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def sentiment_label(polarity: float) -> str:
    if polarity > 0.1:
        return "Positive 🙂"
    if polarity < -0.1:
        return "Negative 🙁"
    return "Neutral 😐"

# -----------------------------
# Load model artifacts once
# -----------------------------
@st.cache_resource
def load_artifacts():
    model_path = os.path.join("model", "model.pkl")
    vec_path = os.path.join("model", "vectorizer.pkl")
    model = pickle.load(open(model_path, "rb"))
    vectorizer = pickle.load(open(vec_path, "rb"))
    return model, vectorizer

def predict_topic_and_sentiment(text: str, model, vectorizer):
    cleaned = clean_text(text)
    X = vectorizer.transform([cleaned])
    topic = model.predict(X)[0]

    polarity = TextBlob(text).sentiment.polarity
    return topic, polarity

# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="Finance News NLP", page_icon="📰", layout="wide")
st.title("📰 Finance News NLP (BBC Business RSS)")
st.caption("Fetches BBC Business headlines, filters finance keywords, predicts topic + sentiment.")

# Load artifacts
try:
    model, vectorizer = load_artifacts()
except Exception:
    st.error("Missing model files. Ensure `model/model.pkl` and `model/vectorizer.pkl` exist in your GitHub repo.")
    st.stop()

feed_url = "https://feeds.bbci.co.uk/news/business/rss.xml"

finance_words_default = [
    "market", "stock", "shares", "economy", "bank", "inflation",
    "rates", "oil", "gold", "dollar", "pound"
]

finance_words = st.text_input(
    "Finance filter keywords (comma-separated)",
    value=", ".join(finance_words_default),
)
keywords = [k.strip().lower() for k in finance_words.split(",") if k.strip()]

max_items = st.slider("How many headlines to show?", 3, 20, 10)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("Live BBC finance headlines")

    if st.button("Fetch latest headlines"):
        feed = feedparser.parse(feed_url)

        if not feed.entries:
            st.warning("No headlines found. Try again later.")
        else:
            shown = 0
            for entry in feed.entries:
                title = entry.title.strip()
                title_lc = title.lower()

                # Filter to finance-only keywords
                if keywords and not any(k in title_lc for k in keywords):
                    continue

                topic, polarity = predict_topic_and_sentiment(title, model, vectorizer)
                sent = sentiment_label(polarity)

                with st.container(border=True):
                    st.markdown(f"**{title}**")
                    st.write(f"**Predicted topic:** {topic}")
                    st.write(f"**Sentiment:** {sent}  (polarity={polarity:.3f})")
                    if hasattr(entry, "link"):
                        st.write(entry.link)

                shown += 1
                if shown >= max_items:
                    break

            if shown == 0:
                st.info("No headlines matched your finance keywords. Try changing keywords.")

with col2:
    st.subheader("Try your own headline")
    user_text = st.text_area("Paste a finance headline or short news text", height=140)

    if st.button("Analyze my text"):
        if not user_text.strip():
            st.warning("Please enter some text.")
        else:
            topic, polarity = predict_topic_and_sentiment(user_text, model, vectorizer)
            sent = sentiment_label(polarity)
            st.success(f"Predicted topic: {topic}")
            st.info(f"Sentiment: {sent} (polarity={polarity:.3f})")
