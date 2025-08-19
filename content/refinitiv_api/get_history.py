import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

def main():
    st.title("Refinitiv API - Get History")
    st.info("""
    This page demonstrates how to retrieve historical data using the Refinitiv API.
    
    You can fetch historical price data, fundamental data, and other time series 
    information for various financial instruments including stocks, bonds, 
    commodities, and indices.
    """)
    
    # Configuration section
    st.header("Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Instrument selection
        instrument = st.text_input(
            "Instrument RIC (Reuters Instrument Code)",
            value="AAPL.O",
            help="Enter the RIC for the instrument (e.g., AAPL.O for Apple)"
        )
        
        # Date range selection
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=365),
            help="Select the start date for historical data"
        )
    
    with col2:
        # Fields selection
        fields = st.multiselect(
            "Fields to retrieve",
            options=[
                "TR.PriceClose",
                "TR.PriceOpen", 
                "TR.PriceHigh",
                "TR.PriceLow",
                "TR.Volume",
                "TR.TotalReturn"
            ],
            default=["TR.PriceClose", "TR.Volume"],
            help="Select the data fields you want to retrieve"
        )
        
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            help="Select the end date for historical data"
        )
    
    # Parameters section
    st.header("Additional Parameters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        frequency = st.selectbox(
            "Frequency",
            options=["D", "W", "M", "Q", "Y"],
            index=0,
            help="Data frequency: Daily, Weekly, Monthly, Quarterly, Yearly"
        )
    
    with col2:
        currency = st.text_input(
            "Currency",
            value="USD",
            help="Currency for price data"
        )
    
    with col3:
        adjust_for = st.selectbox(
            "Adjust for",
            options=["None", "Stock Splits", "Dividends", "Both"],
            index=0,
            help="Price adjustment options"
        )
    
    # Fetch data button
    if st.button("Fetch Historical Data", type="primary"):
        with st.spinner("Fetching data from Refinitiv API..."):
            # Placeholder for actual API call
            st.info("🚧 **Demo Mode**: This is a placeholder for the actual Refinitiv API implementation.")
            
            # Generate sample data for demonstration
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            sample_data = pd.DataFrame({
                'Date': date_range,
                'Price': np.random.randn(len(date_range)).cumsum() + 100,
                'Volume': np.random.randint(1000000, 10000000, len(date_range))
            })
            
            st.success(f"Successfully retrieved {len(sample_data)} data points for {instrument}")
            
            # Display data
            st.header("Retrieved Data")
            
            # Show data table
            with st.expander("View Raw Data", expanded=False):
                st.dataframe(sample_data)
            
            # Plot the data
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=sample_data['Date'],
                y=sample_data['Price'],
                mode='lines',
                name='Price',
                line=dict(color='blue')
            ))
            
            fig.update_layout(
                title=f"Historical Price Data for {instrument}",
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Volume chart
            fig_volume = go.Figure()
            
            fig_volume.add_trace(go.Bar(
                x=sample_data['Date'],
                y=sample_data['Volume'],
                name='Volume',
                marker_color='lightblue'
            ))
            
            fig_volume.update_layout(
                title=f"Volume Data for {instrument}",
                xaxis_title="Date",
                yaxis_title="Volume",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_volume, use_container_width=True)
    
    # Code example section
    st.header("Sample Code")
    st.code("""
import refinitiv.data as rd

# Initialize session
rd.open_session()

# Get historical data
data = rd.get_history(
    universe='{instrument}',
    fields={fields},
    start='{start_date}',
    end='{end_date}',
    frequency='{frequency}'
)

print(data.head())
""".format(
    instrument=instrument,
    fields=fields,
    start_date=start_date,
    end_date=end_date,
    frequency=frequency
), language='python')
    
    # Documentation section
    st.header("Documentation")
    st.markdown("""
    ### Key Parameters:
    
    - **Universe**: The instrument identifier (RIC, ISIN, etc.)
    - **Fields**: Data fields to retrieve (price, volume, fundamentals)
    - **Start/End Date**: Date range for historical data
    - **Frequency**: Data frequency (daily, weekly, monthly, etc.)
    
    ### Common RIC Examples:
    - **AAPL.O**: Apple Inc. (NASDAQ)
    - **MSFT.O**: Microsoft Corp. (NASDAQ)
    - **^GSPC**: S&P 500 Index
    - **EUR=**: EUR/USD Exchange Rate
    
    ### Available Fields:
    - **TR.PriceClose**: Closing price
    - **TR.PriceOpen**: Opening price
    - **TR.PriceHigh**: High price
    - **TR.PriceLow**: Low price
    - **TR.Volume**: Trading volume
    - **TR.TotalReturn**: Total return index
    """)
