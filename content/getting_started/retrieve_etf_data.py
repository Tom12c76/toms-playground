import streamlit as st
import requests
import pandas as pd
import inspect
import os

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

    # Override the number of shares with 100 each
    ptf['Shares'] = 100

    # Recalculate the "Market Value" using "Price"
    ptf['Market Value'] = ptf['Shares'] * ptf['Price']

    ptf['Weight (%)'] = ptf['Market Value'] / ptf['Market Value'].sum() * 100
    ptf = ptf.drop('Notional Value', axis=1)
    ptf = ptf.sort_values('Market Value', ascending=False).reset_index(drop=True)
    
    return ptf

def get_spy_etf(url):
    filename = './data/SPY_holdings.xlsx'
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Download the file
    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful

    # Save the file locally
    with open(filename, 'wb') as file:
        file.write(response.content)

    # Read the portfolio Excel file, skipping the first 4 rows
    spyder = pd.read_excel(filename, skiprows=4)  # Skip header rows
    
    # Get the as-of date from the third row, first column
    try:
        date_df = pd.read_excel(filename, nrows=4)
        date_text = date_df.iloc[2, 0]  # Third row, first column likely contains date
        as_of_dt = pd.to_datetime(date_text.split("As of ")[-1]).date() if "As of" in date_text else pd.Timestamp.now().date()
    except:
        as_of_dt = pd.Timestamp.now().date()
    
    # Add As Of Date column
    spyder['As Of Date'] = as_of_dt
    
    # Convert Weight column to float and filter rows with Weight > 0
    if 'Weight' in spyder.columns:
        spyder['Weight'] = pd.to_numeric(spyder['Weight'], errors='coerce')
        spyder = spyder[spyder['Weight'] > 0]
    elif 'Weight (%)' in spyder.columns:
        spyder['Weight (%)'] = pd.to_numeric(spyder['Weight (%)'], errors='coerce')
        spyder = spyder[spyder['Weight (%)'] > 0]
    
    # Drop rows with Ticker = "-"
    spyder = spyder[spyder['Ticker'] != "-"]

    st.dataframe(spyder)

    # Standardize column names if needed
    if 'Weight' in spyder.columns:
        spyder.rename(columns={'Weight': 'Weight (%)'}, inplace=True)
    
    # Ensure we have price and shares data
    if 'Price' not in spyder.columns:
        spyder['Price'] = spyder['Market Value'] / spyder['Shares Held'] if 'Shares Held' in spyder.columns and 'Market Value' in spyder.columns else 0
    
    # Override the number of shares with 100 each for consistency
    spyder['Shares'] = 100
    
    # Recalculate the "Market Value" using "Price"
    spyder['Market Value'] = spyder['Shares'] * spyder['Price']
    
    # Recalculate weights
    spyder['Weight (%)'] = spyder['Market Value'] / spyder['Market Value'].sum() * 100
    
    # Sort and reset index
    spyder = spyder.sort_values('Market Value', ascending=False).reset_index(drop=True)
    
    return spyder

def main():
    st.subheader("ETF Data Retrieval")
    st.markdown("""
    This application retrieves and processes ETF data from specified URLs. 
    The objective is to demonstrate how to download, parse, and display portfolio data 
    for educational and analytical purposes. The Dow Jones Industrial Average 
    index is used as the main portfolio, while the S&P 500 index serves as a benchmark.
    """)

    # URL of the files to download
    url_CIND = 'https://www.blackrock.com/uk/intermediaries/products/253713/ishares-dow-jones-industrial-average-ucits-etf'
    url_CIND_csv = 'https://www.blackrock.com/uk/intermediaries/products/253713/ishares-dow-jones-industrial-average-ucits-etf/1472631233320.ajax?fileType=csv&fileName=CIND_holdings&dataType=fund'
    url_SPY = 'https://www.ssga.com/us/en/intermediary/etfs/spdr-sp-500-etf-trust-spy'
    url_SPY_xlsx = 'https://www.ssga.com/us/en/intermediary/library-content/products/fund-data/etfs/us/holdings-daily-us-en-spy.xlsx'
    
    st.write(f"Main Portfolio: [iShares Dow Jones Industrial Average UCITS ETF]({url_CIND})")
    st.write(f"Benchmark: [SPDR S&P 500 ETF Trust (SPY)]({url_SPY})")
    
    if st.button('Press here to fetch portfolio and benchmark data'):
        with st.spinner('Downloading portfolio data...'):
            # Get main portfolio (CIND)
            ptf = get_etf_ptf(url_CIND_csv)
            st.session_state['ptf'] = ptf
            
            # Get benchmark portfolio (SPY)
            spyder = get_spy_etf(url_SPY_xlsx)
            st.session_state['spyder'] = spyder
            
            st.success('Both portfolios successfully downloaded!')

    # Display the portfolio data if available in session state
    col1, col2 = st.columns(2)
    
    # Main Portfolio (CIND)
    with col1:
        st.subheader("Main Portfolio (CIND)")
        if 'ptf' in st.session_state:
            ptf = st.session_state['ptf']
            st.write(ptf.head(10))  # Show only top 10 for cleaner display
            total_market_value = ptf['Market Value'].sum()
            st.metric(label="Total Market Value", value=f"$ {total_market_value:,.0f}")
            st.write(f"Total holdings: {len(ptf)} stocks")
            if st.checkbox('Show full CIND portfolio'):
                st.write(ptf)
        else:
            st.info("No main portfolio data loaded yet")
    
    # Benchmark Portfolio (SPY)
    with col2:
        st.subheader("Benchmark Portfolio (SPY)")
        if 'spyder' in st.session_state:
            spyder = st.session_state['spyder']
            st.write(spyder.head(10))  # Show only top 10 for cleaner display
            total_market_value = spyder['Market Value'].sum()
            st.metric(label="Total Market Value", value=f"$ {total_market_value:,.0f}")
            st.write(f"Total holdings: {len(spyder)} stocks")
            if st.checkbox('Show full SPY portfolio'):
                st.write(spyder)
        else:
            st.info("No benchmark data loaded yet")

    # Function code viewers
    with st.expander("View ETF data functions"):
        if st.checkbox('View get_etf_ptf function (CIND)'):
            source_code = inspect.getsource(get_etf_ptf)
            st.code(source_code, language='python')
            
        if st.checkbox('View get_spy_etf function (SPY)'):
            source_code = inspect.getsource(get_spy_etf)
            st.code(source_code, language='python')

if __name__ == "__main__":
    main()