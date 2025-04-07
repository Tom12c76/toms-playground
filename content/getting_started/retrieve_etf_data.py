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
        spyder['Weight'] = pd.to_numeric(spyder['Weight'].str.replace(',', ''), errors='coerce')
        spyder = spyder[spyder['Weight'] > 0]
    elif 'Weight (%)' in spyder.columns:
        spyder['Weight (%)'] = pd.to_numeric(spyder['Weight (%)'].str.replace(',', ''), errors='coerce')
        spyder = spyder[spyder['Weight (%)'] > 0]
    
    # Drop rows with Ticker = "-"
    spyder = spyder[spyder['Ticker'] != "-"]

    # Standardize column names if needed
    if 'Weight' in spyder.columns:
        spyder.rename(columns={'Weight': 'Weight (%)'}, inplace=True)
    
    # Ensure we have price and shares data
    if 'Price' not in spyder.columns:
        spyder['Price'] = spyder['Market Value'] / spyder['Shares Held'] if 'Shares Held' in spyder.columns and 'Market Value' in spyder.columns else 0
    
    if 'Shares Held' in spyder.columns and 'Shares' not in spyder.columns:
        spyder.rename(columns={'Shares Held': 'Shares'}, inplace=True)
    
    # Override the number of shares with 100 each for consistency
    spyder['Shares'] = 100
    
    # Recalculate the "Market Value" using "Price"
    spyder['Market Value'] = spyder['Shares'] * spyder['Price']
    
    # Recalculate weights
    spyder['Weight (%)'] = spyder['Market Value'] / spyder['Market Value'].sum() * 100
    
    # Sort and reset index
    spyder = spyder.sort_values('Market Value', ascending=False).reset_index(drop=True)
    
    return spyder

def get_sector_etf(ticker):
    """
    Download and process holdings for a specific sector ETF
    """
    url = f"https://www.ssga.com/us/en/intermediary/library-content/products/fund-data/etfs/us/holdings-daily-us-en-{ticker.lower()}.xlsx"
    filename = f'./data/{ticker}_holdings.xlsx'
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    try:
        # Download the file
        response = requests.get(url)
        response.raise_for_status()
        
        # Save the file locally
        with open(filename, 'wb') as file:
            file.write(response.content)
        
        # Read the portfolio Excel file, skipping the first 4 rows (typical for SPDR ETFs)
        sector_etf = pd.read_excel(filename, skiprows=4)
        
        # Get the as-of date
        try:
            date_df = pd.read_excel(filename, nrows=4)
            date_text = date_df.iloc[2, 0]
            as_of_dt = pd.to_datetime(date_text.split("As of ")[-1]).date() if "As of" in date_text else pd.Timestamp.now().date()
        except:
            as_of_dt = pd.Timestamp.now().date()
        
        # Add As Of Date and Sector ETF columns
        sector_etf['As Of Date'] = as_of_dt
        sector_etf['Sector ETF'] = ticker
        
        # Convert Weight column to float and filter rows with Weight > 0
        if 'Weight' in sector_etf.columns:
            sector_etf['Weight'] = pd.to_numeric(sector_etf['Weight'], errors='coerce')
            sector_etf = sector_etf[sector_etf['Weight'] > 0]
            sector_etf.rename(columns={'Weight': 'Weight (%)'}, inplace=True)
        elif 'Weight (%)' in sector_etf.columns:
            sector_etf['Weight (%)'] = pd.to_numeric(sector_etf['Weight (%)'], errors='coerce')
            sector_etf = sector_etf[sector_etf['Weight (%)'] > 0]
        
        # Drop rows with Ticker = "-" if any
        sector_etf = sector_etf[sector_etf['Ticker'] != "-"]
        
        # Standardize column names as needed for consistency
        if 'Shares Held' in sector_etf.columns and 'Shares' not in sector_etf.columns:
            sector_etf.rename(columns={'Shares Held': 'Shares'}, inplace=True)
        
        return sector_etf
    
    except Exception as e:
        st.error(f"Error downloading {ticker} ETF data: {str(e)}")
        return pd.DataFrame()

def download_all_sector_etfs():
    """
    Download all 11 Select Sector SPDR ETFs and return consolidated holdings
    """
    sector_tickers = ['XLU', 'XLK', 'XLRE', 'XLB', 'XLI', 'XLV', 'XLF', 'XLE', 'XLP', 'XLY', 'XLC']
    sector_names = {
        'XLU': 'Utilities',
        'XLK': 'Technology',
        'XLRE': 'Real Estate',
        'XLB': 'Materials',
        'XLI': 'Industrials',
        'XLV': 'Health Care',
        'XLF': 'Financials',
        'XLE': 'Energy',
        'XLP': 'Consumer Staples',
        'XLY': 'Consumer Discretionary',
        'XLC': 'Communication Services'
    }
    
    all_sectors = {}
    sector_holdings = pd.DataFrame()
    
    for ticker in sector_tickers:
        with st.spinner(f'Downloading {ticker} sector ETF data...'):
            sector_df = get_sector_etf(ticker)
            if not sector_df.empty:
                sector_df['Sector'] = sector_names.get(ticker, ticker)
                sector_holdings = pd.concat([sector_holdings, sector_df], ignore_index=True)
                all_sectors[ticker] = sector_df
                st.success(f"Downloaded {ticker} with {len(sector_df)} holdings")
    
    return all_sectors, sector_holdings

def map_spy_to_sectors(spy_df, sector_holdings):
    """
    Map SPY holdings to their corresponding sectors based on sector ETF holdings
    """
    # Create a mapping of tickers to sectors
    ticker_to_sector = {}
    for _, row in sector_holdings.iterrows():
        ticker_to_sector[row['Ticker']] = row['Sector ETF']
    
    # Add sector information to SPY holdings
    spy_df['Sector ETF'] = spy_df['Ticker'].map(ticker_to_sector)
    
    # For any missing sectors, try to fill with sector information if available in SPY data
    if 'Sector' in spy_df.columns:
        # Create a sector name to ETF ticker mapping
        sector_name_to_etf = {
            'Utilities': 'XLU',
            'Information Technology': 'XLK',
            'Real Estate': 'XLRE',
            'Materials': 'XLB',
            'Industrials': 'XLI',
            'Health Care': 'XLV',
            'Financials': 'XLF',
            'Energy': 'XLE',
            'Consumer Staples': 'XLP',
            'Consumer Discretionary': 'XLY',
            'Communication Services': 'XLC'
        }
        
        # Fill missing Sector ETF values
        missing_sector_mask = spy_df['Sector ETF'].isna()
        spy_df.loc[missing_sector_mask, 'Sector ETF'] = spy_df.loc[missing_sector_mask, 'Sector'].map(sector_name_to_etf)
    
    return spy_df

def create_synthetic_sector_portfolio(spy_df):
    """
    Create a synthetic portfolio using sector ETFs instead of individual stocks
    """
    if 'Sector ETF' not in spy_df.columns or spy_df['Sector ETF'].isna().all():
        st.error("Cannot create synthetic portfolio: No sector information available")
        return pd.DataFrame()
    
    # Group by Sector ETF and sum the weights
    sector_weights = spy_df.groupby('Sector ETF')['Weight (%)'].sum().reset_index()
    
    # Normalize the weights to make sure they sum to 100%
    sector_weights['Weight (%)'] = sector_weights['Weight (%)'] / sector_weights['Weight (%)'].sum() * 100
    
    # Sort by weight descending
    sector_weights = sector_weights.sort_values('Weight (%)', ascending=False).reset_index(drop=True)
    
    # Add descriptive sector names
    sector_names = {
        'XLU': 'Utilities',
        'XLK': 'Technology',
        'XLRE': 'Real Estate',
        'XLB': 'Materials',
        'XLI': 'Industrials',
        'XLV': 'Health Care',
        'XLF': 'Financials',
        'XLE': 'Energy',
        'XLP': 'Consumer Staples',
        'XLY': 'Consumer Discretionary',
        'XLC': 'Communication Services'
    }
    
    sector_weights['Sector Name'] = sector_weights['Sector ETF'].map(sector_names)
    
    # Calculate shares and market value (assuming $100,000 portfolio and $100/share price for simplicity)
    total_investment = 100000
    sector_weights['Price'] = 100  # Simplified assumption
    sector_weights['Market Value'] = sector_weights['Weight (%)'] / 100 * total_investment
    sector_weights['Shares'] = sector_weights['Market Value'] / sector_weights['Price']
    
    # Rearrange columns for better readability
    sector_weights = sector_weights[['Sector ETF', 'Sector Name', 'Weight (%)', 'Price', 'Shares', 'Market Value']]
    
    return sector_weights

def main():
    st.subheader("ETF Data Retrieval and Sector Analysis")
    st.markdown("""
    This application retrieves and processes ETF data from specified URLs. 
    The objective is to demonstrate how to download, parse, and analyze portfolio data.
    It includes:
    1. Downloading the Dow Jones Industrial Average ETF and S&P 500 ETF data
    2. Downloading the 11 Select Sector SPDR ETFs
    3. Creating a synthetic portfolio by sector allocation
    """)

    # URL of the files to download
    url_CIND = 'https://www.blackrock.com/uk/intermediaries/products/253713/ishares-dow-jones-industrial-average-ucits-etf'
    url_CIND_csv = 'https://www.blackrock.com/uk/intermediaries/products/253713/ishares-dow-jones-industrial-average-ucits-etf/1472631233320.ajax?fileType=csv&fileName=CIND_holdings&dataType=fund'
    url_SPY = 'https://www.ssga.com/us/en/intermediary/etfs/spdr-sp-500-etf-trust-spy'
    url_SPY_xlsx = 'https://www.ssga.com/us/en/intermediary/library-content/products/fund-data/etfs/us/holdings-daily-us-en-spy.xlsx'
    
    st.write(f"Main Portfolio: [iShares Dow Jones Industrial Average UCITS ETF]({url_CIND})")
    st.write(f"Benchmark: [SPDR S&P 500 ETF Trust (SPY)]({url_SPY})")
    
    tabs = st.tabs(["ETF Data", "Sector Analysis", "Synthetic Portfolio"])
    
    with tabs[0]:
        if st.button('Fetch portfolio and benchmark data'):
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
    
    with tabs[1]:
        st.subheader("Sector ETF Analysis")
        
        if st.button('Download Sector ETF Data'):
            if 'spyder' not in st.session_state:
                st.error("Please download the SPY data first in the ETF Data tab")
            else:
                # Download all sector ETFs
                all_sectors, sector_holdings = download_all_sector_etfs()
                st.session_state['all_sectors'] = all_sectors
                st.session_state['sector_holdings'] = sector_holdings
                
                # Map SPY holdings to sectors
                spy_with_sectors = map_spy_to_sectors(st.session_state['spyder'].copy(), sector_holdings)
                st.session_state['spy_with_sectors'] = spy_with_sectors
                
                st.success(f"Downloaded data for all sector ETFs with {len(sector_holdings)} total holdings")
        
        # Display sector data if available
        if 'all_sectors' in st.session_state:
            sector_options = list(st.session_state['all_sectors'].keys())
            selected_sector = st.selectbox('Select Sector ETF to view', sector_options)
            
            if selected_sector:
                sector_data = st.session_state['all_sectors'][selected_sector]
                st.write(f"Showing top 10 holdings for {selected_sector}:")
                st.write(sector_data.head(10))
                
                total_holdings = len(sector_data)
                st.metric("Total Holdings", total_holdings)
                
                if st.checkbox(f'Show full {selected_sector} portfolio'):
                    st.write(sector_data)
        
        # Display SPY with sector mappings
        if 'spy_with_sectors' in st.session_state:
            st.subheader("SPY Holdings with Sector Mappings")
            spy_sectors = st.session_state['spy_with_sectors']
            
            # Show sector distribution
            sector_distribution = spy_sectors.groupby('Sector ETF')['Weight (%)'].sum().sort_values(ascending=False)
            st.bar_chart(sector_distribution)
            
            # Show top holdings with their sectors
            st.write("Top SPY holdings with their sector ETFs:")
            st.write(spy_sectors[['Ticker', 'Name', 'Weight (%)', 'Sector ETF']].head(10))
            
            mapped_count = spy_sectors['Sector ETF'].notna().sum()
            total_count = len(spy_sectors)
            st.write(f"Successfully mapped {mapped_count} out of {total_count} holdings to sectors ({mapped_count/total_count:.1%})")
            
            if st.checkbox('Show full SPY with sectors'):
                st.write(spy_sectors)
    
    with tabs[2]:
        st.subheader("Synthetic Sector ETF Portfolio")
        
        if 'spy_with_sectors' in st.session_state:
            # Create synthetic portfolio
            synthetic_portfolio = create_synthetic_sector_portfolio(st.session_state['spy_with_sectors'])
            st.session_state['synthetic_portfolio'] = synthetic_portfolio
            
            st.write("Instead of buying all 500+ stocks in the S&P 500, you can create a synthetic portfolio using these sector ETFs:")
            st.write(synthetic_portfolio)
            
            # Visualize the sector weights
            st.subheader("Sector Allocation")
            st.bar_chart(synthetic_portfolio.set_index('Sector ETF')['Weight (%)'])
            
            # Display a pie chart
            import plotly.express as px
            fig = px.pie(synthetic_portfolio, values='Weight (%)', names='Sector Name', 
                         title='Synthetic Portfolio Sector Allocation')
            st.plotly_chart(fig)
            
            # Allow downloading the synthetic portfolio
            csv = synthetic_portfolio.to_csv(index=False)
            st.download_button(
                label="Download Synthetic Portfolio CSV",
                data=csv,
                file_name="synthetic_sector_portfolio.csv",
                mime="text/csv",
            )
        else:
            st.info("Please download sector data in the Sector Analysis tab first")

    # Function code viewers
    with st.expander("View ETF data functions"):
        if st.checkbox('View get_etf_ptf function (CIND)'):
            source_code = inspect.getsource(get_etf_ptf)
            st.code(source_code, language='python')
            
        if st.checkbox('View get_spy_etf function (SPY)'):
            source_code = inspect.getsource(get_spy_etf)
            st.code(source_code, language='python')
            
        if st.checkbox('View get_sector_etf function'):
            source_code = inspect.getsource(get_sector_etf)
            st.code(source_code, language='python')
            
        if st.checkbox('View create_synthetic_sector_portfolio function'):
            source_code = inspect.getsource(create_synthetic_sector_portfolio)
            st.code(source_code, language='python')

if __name__ == "__main__":
    main()