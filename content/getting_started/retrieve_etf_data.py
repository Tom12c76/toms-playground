import streamlit as st
import requests
import pandas as pd
import inspect

def main():
    st.title("Retrieve ETF Data")
    st.write("This is the content for retrieving ETF data.")
    st.subheader("Retrieving ETF Data")
    st.info("To get things started, we need to retrieve some portfolio data. One of the simplest solutions is the Dow Jones Industrial Average ETF (DIA).")

    # URL of the file to download
    url = 'https://www.blackrock.com/uk/intermediaries/products/253713/ishares-dow-jones-industrial-average-ucits-etf/1472631233320.ajax?fileType=csv&fileName=CIND_holdings&dataType=fund'  # Update with the actual URL
    filename = './data/CIND_holdings.csv'

    # Download the file
    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful

    # Save the file locally
    with open(filename, 'wb') as file:
        file.write(response.content)

    # Load portfolio file from local directory
    portfolio_file_path = filename  # Update with your CSV file name

    # Read the portfolio CSV file
    as_of_dt = pd.read_csv(portfolio_file_path, nrows=1).columns[1]
    as_of_dt = pd.to_datetime(as_of_dt).date()
    ptf = pd.read_csv(portfolio_file_path, skiprows=2, thousands=',', decimal='.')
    ptf['As Of Date'] = as_of_dt
    ptf = ptf.dropna(subset=['Name'])
    ptf = ptf[ptf['Asset Class'] == 'Equity']
    ptf['Weight (%)'] = ptf['Market Value'] / ptf['Market Value'].sum() * 100
    ptf = ptf.drop('Notional Value', axis=1)
    ptf = ptf.sort_values('Market Value', ascending=False).reset_index(drop=True)
    st.write(ptf)
    
    # Store filtered portfolio in session state for later use
    st.session_state['ptf'] = ptf

    # Add checkbox for code viewing
    if st.checkbox('View Code'):
        # Display the function's source code
        source_code = inspect.getsource(main)
        st.code(source_code, language='python')