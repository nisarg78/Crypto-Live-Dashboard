import streamlit as st
from data_fetcher import get_coin_details, get_crypto_history, get_top_coins
from data_processing import process_coin_details
import pandas as pd
import plotly.graph_objects as go
from utils import calculate_rsi, calculate_macd

# --- Sidebar Navigation ---
st.sidebar.title("Crypto Dashboard")
st.sidebar.markdown("---")
page_map = {
    "Home": "Home.py",
    "Portfolio": "pages/Portfolio.py",
    "Coin Details": "pages/CoinDetails.py",
    "Compare": "pages/Compare.py",
    "Settings": "pages/Settings.py",
    "About": "pages/About.py"
}
nav = st.sidebar.radio(
    "Navigate",
    list(page_map.keys()),
    index=3
)
if nav != "Compare":
    st.switch_page(page_map[nav])
st.title("🔍 Compare Cryptocurrencies")

currency = st.session_state.get("currency", "usd")  # default to USD
refresh_interval = st.session_state.get("refresh", 180)
# --- CSS Styling ---
st.markdown("""
<style>
.card {
    border: 1px solid #444;
    border-radius: 10px;
    padding: 20px;
    margin-top: 20px;
    background-color: #111;
}
.card h4 {
    color: #fff;
    margin-bottom: 1rem;
}
.rsi-badge {
    font-weight: bold;
    padding: 4px 8px;
    border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)

# --- Coin Selectors ---
top_coins = get_top_coins(100)
coin_options = {f"{coin['name']} ({coin['symbol'].upper()})": coin['id'] for coin in top_coins}

col_select = st.columns(2)
with col_select[0]:
    coin1_name = st.selectbox("Select First Coin", options=list(coin_options.keys()), index=0)
with col_select[1]:
    coin2_name = st.selectbox("Select Second Coin", options=list(coin_options.keys()), index=1)

coin1 = coin_options[coin1_name]
coin2 = coin_options[coin2_name]

if st.button("🔄 Compare"):
    try:
        raw1 = get_coin_details(coin1)
        raw2 = get_coin_details(coin2)

        data1 = process_coin_details(raw1)
        data2 = process_coin_details(raw2)

        df_compare = pd.DataFrame([data1, data2]).T
        df_compare.columns = [data1["Symbol"], data2["Symbol"]]
        for col in df_compare.columns:
            df_compare[col] = df_compare[col].astype(str)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"<h4>📊 Comparison: {data1['Name']} vs {data2['Name']}</h4>", unsafe_allow_html=True)
        st.dataframe(df_compare)
        st.markdown("</div>", unsafe_allow_html=True)

        # --- Price Chart ---
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h4>📉 Price Movement</h4>", unsafe_allow_html=True)

        df1 = pd.DataFrame(get_crypto_history(coin1, 60)["prices"], columns=["timestamp", "price"])
        df1["Date"] = pd.to_datetime(df1["timestamp"], unit="ms")
        df2 = pd.DataFrame(get_crypto_history(coin2, 60)["prices"], columns=["timestamp", "price"])
        df2["Date"] = pd.to_datetime(df2["timestamp"], unit="ms")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df1["Date"], y=df1["price"], mode="lines", name=f"{data1['Symbol']} Price"))
        fig.add_trace(go.Scatter(x=df2["Date"], y=df2["price"], mode="lines", name=f"{data2['Symbol']} Price"))
        fig.update_layout(xaxis_title="Date", yaxis_title="Price (USD)", height=450)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # --- Technical Analysis ---
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h4>⚙️ Basic Technicals (Last 60 Days)</h4>", unsafe_allow_html=True)

        rsi1 = calculate_rsi(df1["price"]).dropna().iloc[-1]
        rsi2 = calculate_rsi(df2["price"]).dropna().iloc[-1]
        macd1_series, sig1_series = calculate_macd(df1["price"])
        macd2_series, sig2_series = calculate_macd(df2["price"])
        macd1 = macd1_series.dropna().iloc[-1]
        sig1 = sig1_series.dropna().iloc[-1]
        macd2 = macd2_series.dropna().iloc[-1]
        sig2 = sig2_series.dropna().iloc[-1]

        def rsi_status(rsi):
            if rsi < 30:
                return "🟩 <span class='rsi-badge' style='background:#2d6a4f;'>Oversold</span>"
            elif rsi > 70:
                return "🟥 <span class='rsi-badge' style='background:#9d0208;'>Overbought</span>"
            else:
                return "🟦 <span class='rsi-badge' style='background:#577590;'>Neutral</span>"

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h4>⚙️ Based on Technical Analysis</h4>", unsafe_allow_html=True)
        st.markdown(f"**{data1['Symbol']} RSI:** {rsi1:.2f} {rsi_status(rsi1)}", unsafe_allow_html=True)
        st.markdown(f"**{data1['Symbol']} MACD:** {macd1:.2f} | Signal: {sig1:.2f}")
        st.markdown("---")
        st.markdown(f"**{data2['Symbol']} RSI:** {rsi2:.2f} {rsi_status(rsi2)}", unsafe_allow_html=True)
        st.markdown(f"**{data2['Symbol']} MACD:** {macd2:.2f} | Signal: {sig2:.2f}")
        st.markdown("</div>", unsafe_allow_html=True)

        # --- Visual RSI & MACD Comparison ---
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h4>📈 RSI & MACD Visual Comparison</h4>", unsafe_allow_html=True)

        comp_fig = go.Figure()
        comp_fig.add_trace(go.Bar(name=f"{data1['Symbol']} RSI", x=["RSI"], y=[rsi1], marker_color="skyblue"))
        comp_fig.add_trace(go.Bar(name=f"{data2['Symbol']} RSI", x=["RSI"], y=[rsi2], marker_color="deepskyblue"))
        comp_fig.add_trace(go.Bar(name=f"{data1['Symbol']} MACD", x=["MACD"], y=[macd1], marker_color="salmon"))
        comp_fig.add_trace(go.Bar(name=f"{data2['Symbol']} MACD", x=["MACD"], y=[macd2], marker_color="orangered"))
        comp_fig.update_layout(barmode='group', yaxis_title="Value", height=450)
        st.plotly_chart(comp_fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # --- Beginner-Friendly Explanation ---
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h4>📘 Beginner-Friendly Technical Analysis</h4>", unsafe_allow_html=True)

        explain_cards = {
            "📈 RSI": [
                "Shows if the coin is overbought (70+) or oversold (30−).",
                "Like checking if a coin is too hyped or ignored."
            ],
            "📊 MACD": [
                "MACD > Signal = bullish. Else = bearish.",
                "Think of it as the mood swing of the market."
            ],
            "📦 Volume": [
                "High volume = big interest from traders.",
                "Like foot traffic in a busy store."
            ],
            "🎢 Volatility": [
                "High = risk/reward, Low = stability.",
                "Rollercoaster vs calm boat ride."
            ],
            "📉 Trend Pattern": [
                "Detects up/down/sideways trends.",
                "Is the crowd walking uphill or downhill?"
            ]
        }

        exp_cols = st.columns(3)
        for i, (title, (explanation, analogy)) in enumerate(explain_cards.items()):
            with exp_cols[i % 3]:
                st.markdown(f"### {title}")
                st.markdown(f"**What it means:** {explanation}")
                st.caption(f"💡 _{analogy}_")
        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error: {e}")