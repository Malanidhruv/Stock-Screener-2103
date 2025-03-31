import streamlit as st
import pandas as pd
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from alice_client import initialize_alice, save_credentials, load_credentials
from stock_analysis import analyze_all_tokens, fetch_stock_data_up, fetch_stock_data_down
from stock_lists import STOCK_LISTS

st.set_page_config(page_title="Stock Screener", layout="wide")
st.warning("This screener is based on statistical analysis. Please conduct your own due diligence before making any trading decisions. Best viewed on **Google Chrome**.")

# Load stored credentials
user_id, api_key = load_credentials()
if not user_id or not api_key:
    with st.form("login_form"):
        st.title("Admin Login - Enter AliceBlue API Credentials")
        new_user_id = st.text_input("Enter User ID", type="password")
        new_api_key = st.text_input("Enter API Key", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            save_credentials(new_user_id, new_api_key)
            st.success("API credentials saved! Refreshing...")
            st.rerun()

try:
    alice = initialize_alice()
except Exception as e:
    st.error(f"Failed to initialize AliceBlue API: {e}")
    alice = None

@st.cache_data(ttl=300)
def fetch_screened_stocks(tokens, strategy):
    if not alice:
        return []
    
    try:
        with ThreadPoolExecutor(max_workers=10) as executor:
            if strategy == "3-5% Gainers":
                futures = {executor.submit(fetch_stock_data_up, alice, token): token for token in tokens}
            elif strategy == "3-5% Losers":
                futures = {executor.submit(fetch_stock_data_down, alice, token): token for token in tokens}
            else:
                return analyze_all_tokens(alice, tokens)
            
            results = [future.result() for future in as_completed(futures)]
            return [res for res in results if res is not None]
    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
        return []

def display_stock_data(data, strategy):
    if not data:
        st.warning(f"No stocks found for {strategy}")
        return
    
    df = pd.DataFrame(data)
    if "Name" in df.columns:
        df.insert(1, "TradingView Link", df["Name"].apply(lambda x: f'https://in.tradingview.com/chart?symbol=NSE%3A{x}'))
    
    search = st.text_input("Search Stocks:", "").upper()
    if search and "Name" in df.columns:
        df = df[df["Name"].str.contains(search, na=False, regex=False)]
    
    st.dataframe(df, use_container_width=True)

st.title("Stock Screener")
col1, col2 = st.columns(2)
with col1:
    selected_list = st.selectbox("Select Stock List:", list(STOCK_LISTS.keys()))
with col2:
    strategy = st.selectbox("Select Strategy:", ["3-5% Gainers", "3-5% Losers", "EMA, RSI & Support Zone"])

if st.button("Start Screening"):
    tokens = STOCK_LISTS.get(selected_list, [])
    if not tokens:
        st.warning(f"No stocks found for {selected_list}.")
    else:
        with st.spinner("Fetching and analyzing stocks..."):
            screened_stocks = fetch_screened_stocks(tokens, strategy)
        display_stock_data(screened_stocks, strategy)
