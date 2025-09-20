
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import refinitiv.data as rd

def main():

    st.title("Refinitiv API - Get History")

    # --- Credentials ---
    try:
        app_key = st.secrets["refinitiv"]["app_key"]
        st.success("✅ Refinitiv credentials loaded")
    except KeyError as e:
        st.error(f"❌ Missing Refinitiv credential: {e}")
        st.stop()

    # --- UI: Configuration ---
    st.header("Configuration")
    col1, col2 = st.columns(2)
    with col1:
        instrument = st.text_input(
            "Instrument RIC (Reuters Instrument Code)",
            value="AAPL.O",
            help="Enter the RIC for the instrument (e.g., AAPL.O for Apple)"
        )
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=365),
            help="Select the start date for historical data"
        )
    with col2:
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

    # --- UI: Additional Parameters ---
    st.header("Additional Parameters")
    col1, col2, col3 = st.columns(3)
    with col1:
        frequency = st.selectbox(
            "Frequency",
            options=["D", "W", "M", "Q", "Y"],
            index=0,
            help="Data frequency: Daily, Weekly, Monthly, Quarterly, Yearly"
        )
        # Map UI frequency to Refinitiv interval
        interval_map = {
            "D": "daily",
            "W": "weekly",
            "M": "monthly",
            "Q": "quarterly",
            "Y": "yearly"
        }
        interval = interval_map.get(frequency, "daily")
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

    # --- Fetch Data Button ---
    if st.button("Fetch Historical Data", type="primary"):
        with st.spinner("Fetching data from Refinitiv API..."):
            # --- Open Refinitiv session ---
            try:
                rd.open_session(app_key=app_key)
            except Exception as e:
                st.error(f"Failed to open Refinitiv session: {e}")
                st.stop()

            # --- Fetch data ---
            try:
                data = rd.get_history(
                    universe=instrument,
                    fields=fields,
                    start=str(start_date),
                    end=str(end_date),
                    interval=interval
                )
                if data is None or data.empty:
                    st.warning("No data returned for the selected parameters.")
                    return
                st.success(f"Successfully retrieved {len(data)} data points for {instrument}")
            except Exception as e:
                st.error(f"Error fetching data: {e}")
                return

            # --- Display Data ---
            st.header("Retrieved Data")
            with st.expander("View Raw Data", expanded=False):
                st.dataframe(data)

            # --- Plotting ---
            if "TR.PriceClose" in data.columns:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=data["TR.PriceClose"],
                    mode='lines',
                    name='Price',
                    line=dict(color='blue')
                ))
                fig.update_layout(
                    title=f"Historical Price Data for {instrument}",
                    xaxis_title="Date",
                    yaxis_title="Price ({})".format(currency),
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)

            if "TR.Volume" in data.columns:
                fig_volume = go.Figure()
                fig_volume.add_trace(go.Bar(
                    x=data.index,
                    y=data["TR.Volume"],
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

    # --- Code Example ---
    st.header("Sample Code")
    st.code(f'''
import refinitiv.data as rd

# Initialize session
rd.open_session(app_key="YOUR_APP_KEY")

# Get historical data
data = rd.get_history(
    universe="{instrument}",
    fields={fields},
    start="{start_date}",
    end="{end_date}",
    interval="{interval}"
)
print(data.head())
''', language='python')

    # --- Documentation ---
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
