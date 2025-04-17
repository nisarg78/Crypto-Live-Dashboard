import requests
import streamlit as st

def fetch_crypto_news(coin_name, max_articles=5):
    """
    Fetch latest news headlines for a given cryptocurrency using NewsAPI.org.
    (You need to add your NewsAPI key to Streamlit secrets as newsapi.api_key)
    """
    api_key = st.secrets["newsapi"]["api_key"]
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": coin_name,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": max_articles,
        "apiKey": api_key
    }
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        return resp.json().get("articles", [])
    else:
        st.warning(f"NewsAPI error: {resp.status_code} - {resp.text}")
    return []

def simple_sentiment(text):
    """
    Very basic sentiment analyzer: returns 'positive', 'negative', or 'neutral'.
    """
    positive_words = ["up", "bull", "gain", "rise", "surge", "record", "all-time high", "adopt", "win", "partnership", "growth"]
    negative_words = ["down", "bear", "loss", "drop", "crash", "hack", "scam", "lawsuit", "ban", "decline"]
    text_l = text.lower()
    if any(w in text_l for w in positive_words):
        return "positive"
    if any(w in text_l for w in negative_words):
        return "negative"
    return "neutral"
