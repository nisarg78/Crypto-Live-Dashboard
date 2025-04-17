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
    index=4
)
if nav != "Settings":
    st.switch_page(page_map[nav])
st.title("⚙️ App Settings")

st.markdown("Customize your experience below:")

# Currency selection
currency = st.selectbox("Default Currency", ["USD", "INR", "EUR", "CAD", "GBP"])
st.session_state.currency = currency.lower()

# Refresh time
refresh = st.slider("Auto Refresh Interval (seconds)", 30, 600, 180, step=30)
st.session_state.refresh = refresh

# Theme (you can store this too, even if not applied yet)
theme = st.selectbox("Choose Theme", ["Light", "Dark", "Auto"])
st.session_state.theme = theme


st.success("✅ Settings saved! (Note: These are not persistent across sessions yet)")