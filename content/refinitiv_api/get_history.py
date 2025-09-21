
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import refinitiv.data as rd

def main():
    st.title("Equity Price and Dividend History")

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
        instruments = st.multiselect(
            "Instrument RICs",
            options=["MSFT.O", "ROG.S", "VOD.L", "SAP.GY", "CRDI.MI"],
            default=["MSFT.O", "ROG.S", "VOD.L"],
            help="Select one or more RICs for comparison"
        )
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=365),
            help="Select the start date for historical data"
        )
    with col2:
        currency = "EUR"
        st.text_input("Currency", value=currency, disabled=True)
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            help="Select the end date for historical data"
        )

    # --- Fetch Data Button ---
    if st.button("Fetch Equity Data", type="primary"):
        if not instruments:
            st.warning("Please select at least one instrument.")
            st.stop()

        with st.spinner("Fetching data from Refinitiv API..."):
            # --- Open Refinitiv session ---
            try:
                rd.open_session(app_key=app_key)
            except Exception as e:
                st.error(f"Failed to open Refinitiv session: {e}")
                st.stop()

            # --- 1. Fetch Price History ---
            st.subheader("Price History")
            try:
                price_data = rd.get_history(
                    universe=instruments,
                    fields=["TR.PriceClose"],
                    start=str(start_date),
                    end=str(end_date),
                    interval="daily",
                    parameters={'Curn': currency}
                )
                if price_data is None or price_data.empty:
                    st.warning("No price data returned for the selected parameters.")
                else:
                    st.success(f"Successfully retrieved price data for {len(instruments)} instruments.")
                    
                    # Format the index to show only the date
                    price_data.index = pd.to_datetime(price_data.index)

                    with st.expander("View Raw Price Data", expanded=False):
                        st.dataframe(price_data)

                    # Normalize and plot price data
                    normalized_prices = (price_data / price_data.iloc[0] * 100)
                    fig_price = go.Figure()
                    for instrument in normalized_prices.columns:
                        fig_price.add_trace(go.Scatter(
                            x=normalized_prices.index,
                            y=normalized_prices[instrument],
                            mode='lines',
                            name=instrument
                        ))
                    fig_price.update_layout(
                        title="Normalized Price Performance (Rebased to 100)",
                        xaxis_title="Date",
                        yaxis_title=f"Normalized Price ({currency})",
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig_price, use_container_width=True)

            except Exception as e:
                st.error(f"Error fetching price data: {e}")

            # --- 2. Fetch Dividend History ---
            st.subheader("Dividend History")
            try:
                # Use rd.get_data for event-based data like dividends, for all instruments at once
                consolidated_dividends = rd.get_data(
                    universe=instruments,
                    fields=["TR.DivExDate", "TR.DivUnadjustedGross"],
                    parameters={
                        'SDate': start_date.strftime('%Y-%m-%d'),
                        'EDate': end_date.strftime('%Y-%m-%d'),
                        'Curn': currency
                    }
                )

                if consolidated_dividends is None or consolidated_dividends.empty:
                    st.warning("No dividend data was successfully retrieved for the selected instruments.")
                else:
                    # Clean up the DataFrame before pivoting
                    consolidated_dividends.dropna(subset=["Dividend Ex Date", "Gross Dividend Amount"], how='all', inplace=True)
                    
                    # Rename columns for clarity
                    consolidated_dividends.rename(columns={
                        "Instrument": "Instrument RIC",
                        "Dividend Ex Date": "Ex-Date",
                        "Gross Dividend Amount": f"Dividend ({currency})"
                    }, inplace=True)

                    # Pivot the DataFrame
                    pivoted_dividends = consolidated_dividends.pivot_table(
                        index='Ex-Date',
                        columns='Instrument RIC',
                        values=f"Dividend ({currency})"
                    )

                    # Re-index to match the price data and fill NaNs
                    pivoted_dividends.index = pd.to_datetime(pivoted_dividends.index)
                    aligned_dividends = pivoted_dividends.reindex(index=price_data.index, columns=price_data.columns).fillna(0)


                    st.success(f"Successfully retrieved and aligned dividend data for {len(aligned_dividends.columns)} out of {len(instruments)} instruments.")
                    st.dataframe(aligned_dividends)

            except Exception as e:
                st.error(f"Could not retrieve dividend data. Error: {e}")

    # --- Documentation ---
    st.header("Documentation")
    st.markdown(f"""
    This page retrieves historical price and dividend data for a selection of equities using the Refinitiv Data API. All data is requested in **{currency}**.

    ### 1. Price History
    - Fetches the daily closing prices (`TR.PriceClose`) for the selected instruments.
    - Displays a chart of the normalized price performance, rebased to 100 at the start date for easy comparison.

    ### 2. Dividend History
    - Fetches the dividend ex-dividend dates (`TR.DivExDate`) and unadjusted gross dividend amounts (`TR.DivUnadjustedGross`).
    - Displays the raw dividend data in a table.

    ### Example Tickers:
    - **MSFT.O**: Microsoft Corp. (NASDAQ)
    - **ROG.S**: Roche Holding AG (SIX Swiss Exchange)
    - **VOD.L**: Vodafone Group plc (London Stock Exchange)
    - **SAP.GY**: SAP SE (Deutsche Börse Xetra)
    - **CRDI.MI**: UniCredit S.p.A. (Borsa Italiana)
    """)
    
    # --- Code Example ---
    st.header("Sample Code")
    st.code(f'''
import refinitiv.data as rd

# Initialize session
rd.open_session(app_key="YOUR_APP_KEY")

# 1. Get Price History
price_data = rd.get_history(
    universe={instruments},
    fields=["TR.PriceClose"],
    start="{start_date}",
    end="{end_date}",
    interval="daily",
    parameters={{'Curn': '{currency}'}}
)
print("--- Price History ---")
print(price_data.head())

# 2. Get Dividend History
dividend_data = rd.get_history(
    universe={instruments},
    fields=["TR.DivExDate", "TR.DivUnadjustedGross"],
    start="{start_date}",
    end="{end_date}",
    parameters={{'Curn': '{currency}'}}
)
print("\\n--- Dividend History ---")
print(dividend_data.dropna(how='all').head())
''', language='python')
