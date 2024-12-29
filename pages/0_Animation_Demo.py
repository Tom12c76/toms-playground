import pandas as pd
import requests, os
import streamlit as st
from streamlit.hello.utils import show_code

def get_indu():

    # URL of the file to download
    CIND_url = (
        'https://www.blackrock.com/uk/intermediaries/products/253713/'
        'ishares-dow-jones-industrial-average-ucits-etf/1472631233320.ajax'
        '?fileType=csv&fileName=CIND_holdings&dataType=fund'
    )

    # Download the file
    response = requests.get(CIND_url)
    response.raise_for_status()  # Check if the request was successful

    # Create the data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Save the file locally
    with open('data/CIND.csv', 'wb') as file:
        file.write(response.content)

    # Load portfolio file from local directory
    portfolio_file_path = 'data/CIND.csv'  # Update with your CSV file name

    # Read the portfolio CSV file
    as_of_dt = pd.read_csv(portfolio_file_path, nrows=1).columns[1]
    as_of_dt = pd.to_datetime(as_of_dt).date()
    ptf = pd.read_csv(portfolio_file_path, skiprows=2, thousands=',', decimal='.')
    ptf['As Of Date'] = as_of_dt
    ptf = ptf.dropna(subset=['Name'])
    ptf = ptf[ptf['Asset Class'] == 'Equity']
    ptf['Weight (%)'] = ptf['Market Value'] / ptf['Market Value'].sum() * 100
    ptf = ptf.drop('Notional Value', axis=1)
    st.dataframe(ptf)

    # Store filtered portfolio in session state for later use
    st.session_state['ptf'] = ptf

    return None

st.set_page_config(page_title="First things first", page_icon="📹")

st.markdown("## Retrieve the Portfolio")
st.sidebar.header("Animation Demo")

st.info(
    """
To kick off things we need to define a portfolio to work with.
I like to use the
**iShares Dow Jones Industrial Average UCITS ETF (CIND)**
as it's a simple and well-known portfolio. It only holds 30 stocks
and the price history of the underlying stocks is easy to retrieve.
Remember that the Dow Industrial Average holds an equal amount of shares of each stock!
This means that the stock with the highest price will have the
highest weight in the portfolio.
To replicate the portfolio we can buy either 1 or 10 or 100 shares
of each stock and we're good to go. Or we can just use the amounts that
are in the actual ETF.
"""
)


get_indu()

show_code(get_indu)
