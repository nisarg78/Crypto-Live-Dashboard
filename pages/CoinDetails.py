import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from data_fetcher import get_coin_details, get_crypto_history
from utils import calculate_rsi, calculate_macd, calculate_sma, calculate_ema, calculate_bollinger_bands, calculate_stochastic_oscillator

"""
This module displays detailed information and technical/AI analysis for a selected cryptocurrency.
"""
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
    index=2
)
if nav != "Coin Details":
    st.switch_page(page_map[nav])
st.title("Crypto Insights")

currency = st.session_state.get("currency", "usd")  # default to USD
refresh_interval = st.session_state.get("refresh", 180)

st.sidebar.header("⚙️ Settings")
days = st.sidebar.slider("Price History (days)", 30, 180, 60, step=10)
refresh_interval = st.sidebar.slider("Auto-Refresh (sec)", 60, 600, 180, step=60)

coin_id = st.session_state.get("selected_coin", None)
if not coin_id:
    st.error("No coin selected. Go back to Home.")
    st.stop()

@st.cache_data(ttl=refresh_interval)
def load_data(coin_id, days):
    coin = get_coin_details(coin_id)
    history = get_crypto_history(coin_id, days)
    df = pd.DataFrame(history["prices"], columns=["timestamp", "price"])
    df["Date"] = pd.to_datetime(df["timestamp"], unit="ms")
    return coin, df

try:
    coin, df = load_data(coin_id, days)
    st.title(f"📈 {coin['name']} ({coin['symbol'].upper()})")

    st.subheader("📉 Price Movement")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=df["price"], mode="lines", name="Price"))
    fig.update_layout(title=f"{days}-Day Price Chart", xaxis_title="Date", yaxis_title="Price (USD)")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 Technical Indicators")

        # --- RSI ---
    rsi = calculate_rsi(df["price"])
    current_rsi = rsi.dropna().iloc[-1]
    st.markdown("### 📈 RSI (Relative Strength Index)")
    st.markdown(f"**RSI: {current_rsi:.2f}**")
    if current_rsi > 70:
        st.markdown("🟥 RSI Analysis: Overbought. Consider caution.")
    elif current_rsi < 30:
        st.markdown("🟩 RSI Analysis: Oversold. Might be a buying opportunity.")
    else:
        st.markdown("🟦 RSI Analysis: Neutral. Hold position.")
    rsi_fig = go.Figure()
    rsi_fig.add_trace(go.Scatter(x=df["Date"], y=rsi, mode="lines", name="RSI"))
    rsi_fig.add_hline(y=70, line_color="red", line_dash="dash")
    rsi_fig.add_hline(y=30, line_color="green", line_dash="dash")
    rsi_fig.update_layout(title="RSI Over Time", yaxis_title="RSI", xaxis_title="Date", height=300)
    st.plotly_chart(rsi_fig, use_container_width=True)

    # --- MACD ---
    macd, signal = calculate_macd(df["price"])
    macd_value = macd.iloc[-1]
    signal_value = signal.iloc[-1]
    macd_diff = macd_value - signal_value
    st.markdown("### 📊 MACD (Moving Average Convergence Divergence)")
    st.markdown(f"**MACD: {macd_value:.4f} | Signal: {signal_value:.4f}**")
    if abs(macd_diff) < 0.001:
        st.markdown("⚪ MACD Analysis: Neutral — MACD and signal are almost equal.")
    elif macd_diff > 0:
        st.markdown("🟢 MACD is above the signal line → bullish momentum.")
    else:
        st.markdown("🔴 MACD is below the signal line → bearish momentum.")
    macd_fig = go.Figure()
    macd_fig.add_trace(go.Scatter(x=df["Date"], y=macd, mode="lines", name="MACD", line=dict(color="orange")))
    macd_fig.add_trace(go.Scatter(x=df["Date"], y=signal, mode="lines", name="Signal", line=dict(color="blue", dash="dot")))
    macd_fig.update_layout(title="MACD Over Time", yaxis_title="MACD", xaxis_title="Date", height=300)
    st.plotly_chart(macd_fig, use_container_width=True)

    # --- SMA & EMA ---
    sma = calculate_sma(df["price"])
    ema = calculate_ema(df["price"])
    st.markdown("### 📏 SMA & EMA (Moving Averages)")
    ma_fig = go.Figure()
    ma_fig.add_trace(go.Scatter(x=df["Date"], y=df["price"], mode="lines", name="Price", line=dict(color="gray")))
    ma_fig.add_trace(go.Scatter(x=df["Date"], y=sma, mode="lines", name="SMA", line=dict(color="blue")))
    ma_fig.add_trace(go.Scatter(x=df["Date"], y=ema, mode="lines", name="EMA", line=dict(color="purple", dash="dot")))
    ma_fig.update_layout(title="SMA & EMA Over Time", yaxis_title="Price", xaxis_title="Date", height=300)
    st.plotly_chart(ma_fig, use_container_width=True)

    # --- Bollinger Bands ---
    sma_bb, upper_band, lower_band = calculate_bollinger_bands(df["price"])
    st.markdown("### 📉 Bollinger Bands")
    bb_fig = go.Figure()
    bb_fig.add_trace(go.Scatter(x=df["Date"], y=df["price"], mode="lines", name="Price", line=dict(color="gray")))
    bb_fig.add_trace(go.Scatter(x=df["Date"], y=upper_band, mode="lines", name="Upper Band", line=dict(color="green", dash="dot")))
    bb_fig.add_trace(go.Scatter(x=df["Date"], y=lower_band, mode="lines", name="Lower Band", line=dict(color="red", dash="dot")))
    bb_fig.add_trace(go.Scatter(x=df["Date"], y=sma_bb, mode="lines", name="SMA", line=dict(color="blue")))
    bb_fig.update_layout(title="Bollinger Bands", yaxis_title="Price", xaxis_title="Date", height=300)
    st.plotly_chart(bb_fig, use_container_width=True)

    # --- Stochastic Oscillator ---
    stoch_k = calculate_stochastic_oscillator(df["price"])
    st.markdown("### ⚡ Stochastic Oscillator")
    stoch_fig = go.Figure()
    stoch_fig.add_trace(go.Scatter(x=df["Date"], y=stoch_k, mode="lines", name="%K (Stochastic)"))
    stoch_fig.add_hline(y=80, line_color="red", line_dash="dash")
    stoch_fig.add_hline(y=20, line_color="green", line_dash="dash")
    stoch_fig.update_layout(title="Stochastic Oscillator", yaxis_title="%K", xaxis_title="Date", height=300)
    st.plotly_chart(stoch_fig, use_container_width=True)

    # Key Metrics
    # --- News & Sentiment ---
    from news_fetcher import fetch_crypto_news, simple_sentiment
    st.subheader("📰 Latest News & Sentiment")
    news = fetch_crypto_news(coin['name'])
    if news:
        for article in news:
            sentiment = simple_sentiment(article['title'])
            badge = {"positive": "🟢", "negative": "🔴", "neutral": "🟡"}[sentiment]
            st.markdown(f"{badge} [{article['title']}]({article['url']})  ")
            st.caption(f"{article['source']['name']} | {article['publishedAt'][:10]} | Sentiment: {sentiment.capitalize()}")
    else:
        st.info("No recent news found for this coin.")

    st.subheader("📌 Key Metrics")
    metrics = {
        "💰 Current Price": f"${coin['market_data']['current_price']['usd']:,.2f}",
        "🏦 Market Cap": f"${coin['market_data']['market_cap']['usd']:,.0f}",
        "🔁 24h Volume": f"${coin['market_data']['total_volume']['usd']:,.0f}",
        "🔄 Circulating Supply": f"{coin['market_data']['circulating_supply']:,.0f}",
        "💎 Max Supply": f"{coin['market_data'].get('max_supply', '∞')}",
        "🚀 All-Time High": f"${coin['market_data']['ath']['usd']:,.2f}"
    }
    cols = st.columns(3)
    for i, (label, value) in enumerate(metrics.items()):
        with cols[i % 3]:
            st.metric(label, value)

    # Technical Analysis Recommendation
    tech_icon = "🟡"
    tech_text = "Hold"
    tech_reason = "RSI and MACD suggest a neutral state."
    if current_rsi > 70:
        tech_icon = "🔴"
        tech_text = "Sell"
        tech_reason = f"RSI is {current_rsi:.2f} (Overbought), MACD is below signal → bearish trend."
    elif current_rsi < 30:
        tech_icon = "🟢"
        tech_text = "Buy"
        tech_reason = f"RSI is {current_rsi:.2f} (Oversold), may rebound soon."
    elif macd_diff > 0.001:
        tech_icon = "🟢"
        tech_text = "Buy"
        tech_reason = "MACD is above the signal → bullish trend."
    elif macd_diff < -0.001:
        tech_icon = "🔴"
        tech_text = "Sell"
        tech_reason = "MACD is below the signal → bearish trend."

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"<h4>⚙️ Based on Technical Analysis: {tech_icon} <b>{tech_text}</b></h4>", unsafe_allow_html=True)
    st.caption(f"💬 {tech_reason}")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Beginner-Friendly Technical Analysis ---
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

    # AI Suggestion with explanation
    st.subheader("🤖 AI Summary & Suggestion")
    ai_icon = "🟡"
    ai_text = "Hold"
    ai_reason = "AI didn't detect a strong trend."
    trend_10day = (df['price'].iloc[-1] - df['price'].iloc[-10]) / df['price'].iloc[-10] * 100
    st.markdown(f"📊 10-Day Price Change: **{trend_10day:.2f}%**")

    try:
        ai_prompt = f"""
Crypto: {coin['name']}
Last 10 days of price data:\n{df.tail(10).to_string(index=False)}
Task: Summarize the recent price trend and recommend a short-term action.
Explain your reasoning in 1-2 lines.
"""

        hf_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
        headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
        resp = requests.post(hf_url, headers=headers, json={"inputs": ai_prompt})

        if resp.status_code == 200:
            summary = resp.json()[0]["generated_text"]
            # Extract just the last part (after the prompt text)
            cleaned = summary.split("Explain your reasoning in 1-2 lines.")[-1].strip()

            st.markdown("### 🤖 AI Summary")
            st.success(f"**{cleaned}**")
            lower_summary = summary.lower()
            if any(w in lower_summary for w in ["fall", "drop", "correction", "down"]):
                ai_icon = "🔴"
                ai_text = "Sell"
                ai_reason = "AI detected a possible decline over recent days."
            elif any(w in lower_summary for w in ["rise", "bullish", "increase", "uptrend"]):
                ai_icon = "🟢"
                ai_text = "Buy"
                ai_reason = "AI summary suggests a bullish trend."
            elif any(w in lower_summary for w in ["flat", "sideways", "stable"]):
                ai_icon = "🟡"
                ai_text = "Hold"
                ai_reason = "AI indicates a stable or sideways trend."

            st.markdown(f"### 🤖 Based on AI Summary: {ai_icon} **{ai_text}**")
            st.caption(f"💬 {ai_reason}")
        else:
            raise Exception("AI API failed")

    except Exception as e:
        st.warning("⚠️ AI failed to respond.")
        st.info("Fallback: Suggest holding position based on RSI and MACD.")

    # Final Recommendation
    st.subheader("🧠 Final Recommendation")
    st.markdown(f"- 📊 Technical Analysis recommends: {tech_icon} **{tech_text}**")
    st.markdown(f"- 🤖 AI Analysis suggests: {ai_icon} **{ai_text}**")

    if tech_text == ai_text:
        st.success(f"✅ Both sources agree: **You should {tech_text} it.**")
    else:
        st.info("⚖️ Mixed signals detected. Consider waiting or using additional indicators.")

except Exception as e:
    st.error(f"❌ Failed to load coin data: {e}")