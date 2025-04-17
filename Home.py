import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from data_fetcher import get_top_coins

# ✅ Page config FIRST
st.set_page_config(page_title="📈 Crypto Dashboard", layout="wide", initial_sidebar_state="collapsed")

# --- Global settings from session ---
currency = st.session_state.get("currency", "usd")
refresh_interval = st.session_state.get("refresh", 180)

# --- Currency symbol mapping ---
currency_symbols = {
    "usd": "$", "eur": "€", "inr": "₹", "gbp": "£", "cad": "C$"
}
symbol = currency_symbols.get(currency, "$")

# --- Header ---
st.markdown("""
<style>
.header-title {
    font-size: 2.2rem;
    font-weight: 700;
    margin-bottom: 1rem;
}
.toolbar {
    background-color: #f5f5f5;
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 1.5rem;
}
.coin-card {
    border: 1px solid #ddd;
    border-radius: 10px;
    padding: 1rem;
    background-color: #ffffff;
    transition: 0.2s;
    margin-bottom: 1rem;
}
.coin-card:hover {
    background-color: #f9f9f9;
    box-shadow: 0 0 10px rgba(0,0,0,0.04);
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='header-title'>📊 Cryptocurrency Dashboard</div>", unsafe_allow_html=True)

# --- Toolbar ---
st.markdown("<div class='toolbar'>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

with col1:
    search = st.text_input("🔍 Search", placeholder="e.g., Bitcoin, ETH, Solana")
with col2:
    view_mode = st.selectbox("📋 View", ["Card View", "List View"])
with col3:
    sort_by = st.selectbox("📊 Sort by", ["Popularity", "Name", "Price", "Market Cap", "24h Change"])
with col4:
    sort_order = st.radio("↕️ Order", ["Ascending", "Descending"], horizontal=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- Trend Label ---
def predict_trend(change):
    if change > 1.5:
        return "🔼 Increase"
    elif change < -1.5:
        return "🔽 Decrease"
    return "➖ Stable"

# --- Load and filter coins ---
try:
    coins = get_top_coins(100)

    if search:
        coins = [c for c in coins if search.lower() in c["name"].lower() or search.lower() in c["symbol"].lower()]

    # --- Sort ---
    sort_key = {
        "Popularity": lambda x: x["market_cap_rank"],
        "Name": lambda x: x["name"].lower(),
        "Price": lambda x: x[f"current_price_{currency}"],
        "Market Cap": lambda x: x[f"market_cap_{currency}"],
        "24h Change": lambda x: x.get("price_change_percentage_24h", 0)
    }[sort_by]

    coins = sorted(coins, key=sort_key, reverse=(sort_order == "Descending"))

    # --- Display Coins ---
    st.markdown("### 🪙 Top Coins")
    if view_mode == "Card View":
        for i in range(0, len(coins), 3):
            row = st.columns(3)
            for j in range(3):
                if i + j < len(coins):
                    coin = coins[i + j]
                    with row[j]:
                        st.markdown(f"<div class='coin-card'>", unsafe_allow_html=True)
                        st.markdown(f"### {coin['name']} ({coin['symbol'].upper()})")
                        st.write(f"💸 Price: {symbol}{coin[f'current_price_{currency}']:,.2f}")
                        st.write(f"🏦 Market Cap: {symbol}{coin[f'market_cap_{currency}']:,.0f}")
                        st.write(f"📈 24h Volume: {symbol}{coin[f'total_volume_{currency}']:,.0f}")
                        st.write(f"📊 24h Change: {predict_trend(coin.get('price_change_percentage_24h', 0))}")
                        if st.button("🔍 View Details", key=coin["id"]):
                            st.session_state.selected_coin = coin["id"]
                            st.switch_page("pages/CoinDetails.py")
                        st.markdown("</div>", unsafe_allow_html=True)
    else:
        df = pd.DataFrame(coins)
        df = df[[
            "market_cap_rank", "name", "symbol",
            f"current_price_{currency}",
            f"market_cap_{currency}",
            f"total_volume_{currency}",
            "price_change_percentage_24h"
        ]]
        df.columns = ["Rank", "Name", "Symbol", f"Price ({currency.upper()})", "Market Cap", "24h Volume", "24h Change (%)"]

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination()
        gb.configure_default_column(resizable=True)
        gb.configure_default_column(editable=False, resizable=True)
        grid_options = gb.build()

        AgGrid(df, gridOptions=grid_options, theme="streamlit", height=500)

except Exception as e:
    st.error(f"Error fetching data: {e}")
