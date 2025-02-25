import streamlit as st
import requests
import pandas as pd
import inspect

def get_etf_ptf(url):
    filename = './data/CIND_holdings.csv'

    # Download the file
    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful

    # Save the file locally
    with open(filename, 'wb') as file:
        file.write(response.content)

    # Read the portfolio CSV file
    as_of_dt = pd.read_csv(filename, nrows=1).columns[1]
    as_of_dt = pd.to_datetime(as_of_dt).date()
    ptf = pd.read_csv(filename, skiprows=2, thousands=',', decimal='.')
    ptf['As Of Date'] = as_of_dt
    ptf = ptf.dropna(subset=['Name'])
    ptf = ptf[ptf['Asset Class'] == 'Equity']

    

    ptf['Weight (%)'] = ptf['Market Value'] / ptf['Market Value'].sum() * 100
    ptf = ptf.drop('Notional Value', axis=1)
    ptf = ptf.sort_values('Market Value', ascending=False).reset_index(drop=True)
    
    return ptf

def main():
    st.subheader("ETF Data Retrieval")
    st.markdown("""
    This application retrieves and processes ETF data from a specified URL. 
    The objective is to demonstrate how to download, parse, and display portfolio data 
    for educational and analytical purposes. By using the Dow Jones Industrial Average 
    index, users can gain insights into the performance and composition of one of the 
    most well-known stock market indices. The Dow index includes 30 prominent companies 
    and provides a snapshot of the overall market performance, making it a valuable tool 
    for investors and analysts.
    """)

    # URL of the file to download
    url_CIND = 'https://www.blackrock.com/uk/intermediaries/products/253713/ishares-dow-jones-industrial-average-ucits-etf'
    url_CIND_csv = 'https://www.blackrock.com/uk/intermediaries/products/253713/ishares-dow-jones-industrial-average-ucits-etf/1472631233320.ajax?fileType=csv&fileName=CIND_holdings&dataType=fund'
    st.write(f"[Link to the webpage]({url_CIND})")
    st.write(f"[Link to the CSV file]({url_CIND_csv})")

    if st.button('Press here to read data'):
        ptf = get_etf_ptf(url_CIND_csv)
        st.session_state['ptf'] = ptf

    # Display the portfolio data if available in session state
    if 'ptf' in st.session_state:
        st.write(st.session_state['ptf'])
    else:
        st.info("No portfolio data in memory")

    if st.checkbox('View get_etf_ptf function'):
        source_code = inspect.getsource(get_etf_ptf)
        st.code(source_code, language='python')

if __name__ == "__main__":
    main()