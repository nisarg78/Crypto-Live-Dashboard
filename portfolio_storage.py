import json
import os
import streamlit as st

def save_portfolio_data(portfolio, watchlist, alerts, alerts_rsi, alerts_macd, filename="portfolio_data.json"):
    data = {
        "portfolio": portfolio,
        "watchlist": watchlist,
        "alerts": alerts,
        "alerts_rsi": alerts_rsi,
        "alerts_macd": alerts_macd
    }
    with open(filename, "w") as f:
        json.dump(data, f)

def load_portfolio_data(filename="portfolio_data.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            data = json.load(f)
        return data
    return {"portfolio": [], "watchlist": [], "alerts": {}, "alerts_rsi": {}, "alerts_macd": {}}
