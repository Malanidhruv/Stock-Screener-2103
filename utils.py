import streamlit as st
import pandas as pd

def generate_tradingview_link(stock_name):
    """Generate a TradingView link for a given stock."""
    return f'<a href="https://in.tradingview.com/chart?symbol=NSE%3A{stock_name}" target="_blank">{stock_name}</a>'

def print_stocks_up(stocks):
    """Prints the stocks that gained 3-5% with TradingView links."""
    print("\nStocks that were 3-5% up yesterday:")
    print(f"{'Name':<20} {'Token':<10} {'Close':<10} {'Change (%)':<10}")
    print('-' * 50)
    
    for stock in stocks:
        link = f"https://in.tradingview.com/chart?symbol=NSE%3A{stock['Name']}"
        print(f"{stock['Name']:<20} {stock['Token']:<10} {stock['Close']:<10.2f} {stock['Change (%)']:<10.2f}  {link}")
    
    print('-' * 50)

def print_stocks_down(stocks):
    """Prints the stocks that lost 3-5% with TradingView links."""
    print("\nStocks that were 3-5% down yesterday:")
    print(f"{'Name':<20} {'Token':<10} {'Close':<10} {'Change (%)':<10}")
    print('-' * 50)
    
    for stock in stocks:
        link = f"https://in.tradingview.com/chart?symbol=NSE%3A{stock['Name']}"
        print(f"{stock['Name']:<20} {stock['Token']:<10} {stock['Close']:<10.2f} {stock['Change (%)']:<10.2f}  {link}")
    
    print('-' * 50)

def display_buy_candidates(signals):
    """Displays the top 10 buy candidates in a Streamlit app with clickable links."""
    st.subheader("🚀 Top 10 Buy Candidates (Sorted by Strength)")
    
    # Sort first by Strength (highest first), then by Distance% (lowest first)
    sorted_signals = sorted(signals, key=lambda x: (-x['Strength'], x['Distance%']))
    
    # Select the top 10 candidates after sorting
    top_candidates = sorted_signals[:10]
    
    if top_candidates:
        df = pd.DataFrame(top_candidates)
        
        # Apply the function to create hyperlinks
        df['Name'] = df['Name'].apply(generate_tradingview_link)

        # Select relevant columns
        df = df[['Name', 'Price', 'Support', 'Strength', 'Distance%', 'RSI', 'Trend']]
        
        # Display dataframe with HTML rendering enabled
        st.markdown(df.to_html(escape=False), unsafe_allow_html=True)
    else:
        st.write("No buy candidates found.")
