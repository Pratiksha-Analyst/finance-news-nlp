import streamlit as st
import requests
import feedparser

st.title("📰 Live BBC Finance News NLP Analyzer")

# BBC Business RSS Feed (finance news)
feed_url = "http://feeds.bbci.co.uk/news/business/rss.xml"

# Words to filter finance headlines
finance_words = ["market", "stock", "shares", "economy", "bank", "inflation"]

if st.button("Get Latest Finance Headlines"):
    feed = feedparser.parse(feed_url)
    count = 0

    for entry in feed.entries:
        headline = entry.title.lower()

        # Only finance-related headlines
        if any(word in headline for word in finance_words):
            st.write("###", entry.title)

            # Send headline to your local ML API
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/predict",
                    params={"text": entry.title}
                )

                if response.status_code == 200:
                    result = response.json()
                    # Show raw response (optional for debugging)
                    # st.write("Raw API response:", result)

                    # Safely get prediction & sentiment
                    category = result.get("prediction", "N/A")
                    sentiment = result.get("sentiment", "N/A")

                    st.success(f"Category: {category}")
                    st.info(f"Sentiment: {sentiment}")
                else:
                    st.error("API error: could not get prediction")
            except Exception as e:
                st.error(f"Error connecting to API: {e}")

            st.write("---")
            count += 1

        if count >= 15:  # limit to 5 finance headlines
            break

    if count == 0:
        st.warning("No finance headlines found in the feed.")
