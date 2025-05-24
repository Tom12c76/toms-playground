import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date, timedelta
from curl_cffi import requests  # NEW IMPORT

def get_adj_close_prices(tickers):
    # Use curl_cffi requests to impersonate Chrome
    session = requests.Session(impersonate="chrome")
    # Download historical market data for the given tickers from Yahoo Finance using the custom session
    data = yf.download(
        tickers,
        period="1y",
        auto_adjust=True,
        ignore_tz=True,
        session=session  # Pass the impersonated session
    )
    data.index = data.index.date
    adj_close_prices = data['Close']
    return adj_close_prices

def main():
    st.subheader("yfinance for Stocks")
    st.markdown("""
    **yfinance** is a Python library that allows users to access financial data from Yahoo Finance. 
    It provides a convenient way to download historical market data, retrieve stock information, 
    and perform various financial analyses.
                
    First, we will retireve the list of tickers from the portfolio we created in the previous section.
    """)

    ptf = st.session_state['ptf']
    tickers = ptf.Ticker.unique().tolist()

    st.write("List of Tickers: " + ", ".join(tickers))

    st.write("Count of tickers: " + f"{len(tickers)}")

    # Fetch adjusted close prices
    if 'df_hist' not in st.session_state:
        st.info('No adjusted close prices in session state.')
        # Button to download the adjusted close prices as a CSV file
        if st.button("Download"):
            df_hist = get_adj_close_prices(tickers)
            st.session_state['df_hist'] = df_hist
            st.rerun()
    else:
        # Button to refresh the adjusted close prices
        if st.button("Refresh"):
            df_hist = get_adj_close_prices(tickers)
            st.session_state['df_hist'] = df_hist
        df_hist = st.session_state['df_hist']
        st.dataframe(df_hist)
