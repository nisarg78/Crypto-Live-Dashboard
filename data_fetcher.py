import requests
import streamlit as st

@st.cache_data(ttl=300)
def get_top_coins(limit=100, currency="usd"):
    url = f"https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": currency,
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1,
        "sparkline": False,
        "price_change_percentage": "24h"
    }
    response = requests.get(url, params=params)
    coins = response.json()

    # Rename currency fields
    for coin in coins:
        coin[f"current_price_{currency}"] = coin["current_price"]
        coin[f"market_cap_{currency}"] = coin["market_cap"]
        coin[f"total_volume_{currency}"] = coin["total_volume"]

    return coins

@st.cache_data(ttl=300)
def get_coin_details(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    params = {"localization": False}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=300)
def get_crypto_history(coin_id, days=30):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
