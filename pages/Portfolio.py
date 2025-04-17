import streamlit as st
import pandas as pd
from data_fetcher import get_top_coins, get_coin_details

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
    index=1
)
if nav != "Portfolio":
    st.switch_page(page_map[nav])
st.title("💼 Portfolio & Watchlist")

# --- Persistent Storage ---
from portfolio_storage import save_portfolio_data, load_portfolio_data
if 'loaded_portfolio' not in st.session_state:
    data = load_portfolio_data()
    st.session_state["portfolio"] = data.get("portfolio", [])
    st.session_state["watchlist"] = data.get("watchlist", [])
    st.session_state["alerts"] = data.get("alerts", {})
    st.session_state["alerts_rsi"] = data.get("alerts_rsi", {})
    st.session_state["alerts_macd"] = data.get("alerts_macd", {})
    st.session_state['loaded_portfolio'] = True

def persist():
    save_portfolio_data(
        st.session_state["portfolio"],
        st.session_state["watchlist"],
        st.session_state["alerts"],
        st.session_state["alerts_rsi"],
        st.session_state["alerts_macd"]
    )

# --- Session State Setup ---
if "portfolio" not in st.session_state:
    st.session_state["portfolio"] = []  # List of dicts: {id, name, symbol, quantity, avg_price}
if "watchlist" not in st.session_state:
    st.session_state["watchlist"] = []  # List of coin ids

# --- Top Coins for Selection ---
top_coins = get_top_coins(100)
coin_options = {f"{coin['name']} ({coin['symbol'].upper()})": coin['id'] for coin in top_coins}

# --- Add to Watchlist ---
st.subheader("👀 Watchlist")
col1, col2 = st.columns([3, 1])
with col1:
    add_watch = st.selectbox("Add Coin to Watchlist", options=[c for c in coin_options if coin_options[c] not in st.session_state["watchlist"]])
with col2:
    if st.button("Add", key="add_watch"):
        st.session_state["watchlist"].append(coin_options[add_watch])
        persist()
        st.success(f"Added {add_watch} to watchlist.")

if "alerts" not in st.session_state:
    st.session_state["alerts"] = {}  # {coin_id: [thresholds]}

if st.session_state["watchlist"]:
    from news_fetcher import fetch_crypto_news, simple_sentiment
    for wid in st.session_state["watchlist"]:
        coin = get_coin_details(wid)
        st.markdown(f"**{coin['name']} ({coin['symbol'].upper()})** - Price: ${coin['market_data']['current_price']['usd']:,.2f}")
        if st.button(f"Remove {coin['symbol'].upper()}", key=f"rem_{wid}"):
            st.session_state["watchlist"].remove(wid)
            persist()
            st.experimental_rerun()
        # --- Price Alerts ---
        st.markdown("#### 🔔 Price Alerts")
        cur_price = coin['market_data']['current_price']['usd']
        alert_input = st.number_input(f"Set alert for {coin['symbol'].upper()} (USD)", min_value=0.0, value=0.0, step=0.01, key=f"alert_{wid}")
        if st.button(f"Add Alert {coin['symbol'].upper()}", key=f"add_alert_{wid}"):
            if wid not in st.session_state["alerts"]:
                st.session_state["alerts"][wid] = []
            if alert_input > 0:
                st.session_state["alerts"][wid].append(alert_input)
                persist()
                st.success(f"Alert set for {coin['symbol'].upper()} at ${alert_input:,.2f}")
        # Show active alerts and check if triggered
        triggered = []
        if wid in st.session_state["alerts"]:
            for threshold in st.session_state["alerts"][wid]:
                if (cur_price >= threshold):
                    st.warning(f"🚨 {coin['symbol'].upper()} price is ABOVE alert: ${threshold:,.2f} (Current: ${cur_price:,.2f})")
                    triggered.append(threshold)
                elif (cur_price <= threshold):
                    st.warning(f"🚨 {coin['symbol'].upper()} price is BELOW alert: ${threshold:,.2f} (Current: ${cur_price:,.2f})")
                    triggered.append(threshold)
                else:
                    st.info(f"Alert at ${threshold:,.2f} (Current: ${cur_price:,.2f})")
            # Remove triggered alerts
            st.session_state["alerts"][wid] = [t for t in st.session_state["alerts"][wid] if t not in triggered]
            persist()

        # --- RSI & MACD Alerts ---
        from utils import calculate_rsi, calculate_macd
        import pandas as pd
        # Fetch price history for RSI/MACD
        from data_fetcher import get_crypto_history
        history = get_crypto_history(wid, 60)
        df = pd.DataFrame(history["prices"], columns=["timestamp", "price"])
        rsi_series = calculate_rsi(df["price"])
        current_rsi = rsi_series.dropna().iloc[-1] if not rsi_series.dropna().empty else None
        macd_series, signal_series = calculate_macd(df["price"])
        macd_value = macd_series.iloc[-1] if not macd_series.empty else None
        # RSI Alert
        if "alerts_rsi" not in st.session_state:
            st.session_state["alerts_rsi"] = {}
        rsi_alert = st.number_input(f"Set RSI alert for {coin['symbol'].upper()}", min_value=0.0, max_value=100.0, value=0.0, step=0.1, key=f"rsi_alert_{wid}")
        if st.button(f"Add RSI Alert {coin['symbol'].upper()}", key=f"add_rsi_alert_{wid}"):
            if wid not in st.session_state["alerts_rsi"]:
                st.session_state["alerts_rsi"][wid] = []
            if rsi_alert > 0:
                st.session_state["alerts_rsi"][wid].append(rsi_alert)
                persist()
                st.success(f"RSI alert set for {coin['symbol'].upper()} at {rsi_alert:.1f}")
        rsi_triggered = []
        if wid in st.session_state["alerts_rsi"] and current_rsi is not None:
            for threshold in st.session_state["alerts_rsi"][wid]:
                if current_rsi >= threshold:
                    st.warning(f"🚨 {coin['symbol'].upper()} RSI is ABOVE alert: {threshold:.1f} (Current: {current_rsi:.1f})")
                    rsi_triggered.append(threshold)
                elif current_rsi <= threshold:
                    st.warning(f"🚨 {coin['symbol'].upper()} RSI is BELOW alert: {threshold:.1f} (Current: {current_rsi:.1f})")
                    rsi_triggered.append(threshold)
                else:
                    st.info(f"RSI alert at {threshold:.1f} (Current: {current_rsi:.1f})")
            st.session_state["alerts_rsi"][wid] = [t for t in st.session_state["alerts_rsi"][wid] if t not in rsi_triggered]
            persist()
        # MACD Alert
        if "alerts_macd" not in st.session_state:
            st.session_state["alerts_macd"] = {}
        macd_alert = st.number_input(f"Set MACD alert for {coin['symbol'].upper()}", value=0.0, step=0.01, key=f"macd_alert_{wid}")
        if st.button(f"Add MACD Alert {coin['symbol'].upper()}", key=f"add_macd_alert_{wid}"):
            if wid not in st.session_state["alerts_macd"]:
                st.session_state["alerts_macd"][wid] = []
            st.session_state["alerts_macd"][wid].append(macd_alert)
            persist()
            st.success(f"MACD alert set for {coin['symbol'].upper()} at {macd_alert:.2f}")
        macd_triggered = []
        if wid in st.session_state["alerts_macd"] and macd_value is not None:
            for threshold in st.session_state["alerts_macd"][wid]:
                if macd_value >= threshold:
                    st.warning(f"🚨 {coin['symbol'].upper()} MACD is ABOVE alert: {threshold:.2f} (Current: {macd_value:.2f})")
                    macd_triggered.append(threshold)
                elif macd_value <= threshold:
                    st.warning(f"🚨 {coin['symbol'].upper()} MACD is BELOW alert: {threshold:.2f} (Current: {macd_value:.2f})")
                    macd_triggered.append(threshold)
                else:
                    st.info(f"MACD alert at {threshold:.2f} (Current: {macd_value:.2f})")
            st.session_state["alerts_macd"][wid] = [t for t in st.session_state["alerts_macd"][wid] if t not in macd_triggered]
            persist()

        # News & Sentiment for this coin
        news = fetch_crypto_news(coin['name'], max_articles=3)
        if news:
            for article in news:
                sentiment = simple_sentiment(article['title'])
                badge = {"positive": "🟢", "negative": "🔴", "neutral": "🟡"}[sentiment]
                st.markdown(f"{badge} [{article['title']}]({article['url']})  ")
                st.caption(f"{article['source']['name']} | {article['publishedAt'][:10]} | Sentiment: {sentiment.capitalize()}")
        else:
            st.info("No recent news found for this coin.")
else:
    st.info("Your watchlist is empty.")

# --- Portfolio Section ---
st.subheader("📊 Simulated Portfolio")
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    add_port = st.selectbox("Add Coin to Portfolio", options=[c for c in coin_options if coin_options[c] not in [p['id'] for p in st.session_state['portfolio']]])
with col2:
    qty = st.number_input("Quantity", min_value=0.0, value=0.0, step=0.01, key="qty_port")
with col3:
    avg_price = st.number_input("Avg Buy Price ($)", min_value=0.0, value=0.0, step=0.01, key="avgp_port")

if st.button("Add to Portfolio", key="add_port"):
    if qty > 0 and avg_price > 0:
        cid = coin_options[add_port]
        coin = get_coin_details(cid)
        st.session_state["portfolio"].append({
            "id": cid,
            "name": coin['name'],
            "symbol": coin['symbol'].upper(),
            "quantity": qty,
            "avg_price": avg_price
        })
        persist()
        st.success(f"Added {add_port} to portfolio.")
    else:
        st.warning("Quantity and Avg Buy Price must be greater than 0.")

if st.session_state["portfolio"]:
    data = []
    for pos in st.session_state["portfolio"]:
        coin = get_coin_details(pos['id'])
        cur_price = coin['market_data']['current_price']['usd']
        value = pos['quantity'] * cur_price
        pnl = (cur_price - pos['avg_price']) * pos['quantity']
        data.append({
            "Coin": f"{pos['name']} ({pos['symbol']})",
            "Quantity": pos['quantity'],
            "Avg Buy Price": pos['avg_price'],
            "Current Price": cur_price,
            "Value": value,
            "P&L": pnl
        })
    df = pd.DataFrame(data)
    st.dataframe(df.style.applymap(lambda v: 'color: green' if isinstance(v, float) and v > 0 else ('color: red' if isinstance(v, float) and v < 0 else ''), subset=['P&L']))
    for i, pos in enumerate(st.session_state["portfolio"]):
        if st.button(f"Remove {pos['symbol']}", key=f"rem_port_{i}"):
            st.session_state["portfolio"].pop(i)
            persist()
            st.experimental_rerun()
else:
    st.info("Your portfolio is empty.")
