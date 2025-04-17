import requests

import streamlit as st

# Load Hugging Face API Key from Streamlit secrets
HF_API_TOKEN = st.secrets["huggingface"]["api_token"]
MODEL = "google/flan-t5-base"

def summarize_crypto_trend(coin_name, trend_data):
    """
    Summarize the trend of a cryptocurrency using a Hugging Face model.
    Args:
        coin_name (str): The name of the cryptocurrency.
        trend_data (str): A string representing recent price data.
    Returns:
        str: AI-generated summary or error message.
    """
    prompt = (
        f"Summarize the trend of {coin_name} using this 10-day price snapshot:\n\n"
        f"{trend_data}\n\n"
        "Explain if it's bullish, bearish, or stable, and give a simple reason."
    )

    url = f"https://api-inference.huggingface.co/models/{MODEL}"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {"inputs": prompt, "options": {"wait_for_model": True}}

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()[0]["generated_text"]
        else:
            st.warning(f"Hugging Face API error: {response.status_code} - {response.text}")
            return f"⚠️ AI summary failed: {response.status_code} {response.text}"
    except Exception as e:
        st.warning(f"Hugging Face API exception: {e}")
        return f"⚠️ AI summary failed: {e}"
