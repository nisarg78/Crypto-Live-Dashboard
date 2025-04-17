import streamlit as st

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
    index=5
)
if nav != "About":
    st.switch_page(page_map[nav])
st.title("ℹ️ About Crypto Insights")

currency = st.session_state.get("currency", "usd")  # default to USD
refresh_interval = st.session_state.get("refresh", 180)

st.markdown("""
Welcome to **Crypto Insights** — your intelligent crypto companion!

This dashboard provides:
- 📈 Real-time price tracking
- 🤖 AI-generated market summaries
- 🔍 In-depth technical analysis
- 🧠 Beginner-friendly explanations

Built with ❤️ using [Streamlit](https://streamlit.io), powered by data from CoinGecko and analysis from Hugging Face AI.

---
**Made for educational and strategic research. Not financial advice.**

---
**Author:** Nisarg Zaveri
""")
