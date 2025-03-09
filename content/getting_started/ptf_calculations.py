import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import inspect

def perform_calculations(ptf, df_hist):
    """
    Perform calculations using portfolio and historical data
    Returns a tuple of (portfolio history, log returns)
    """

    # Calculate historical value of each asset in the portfolio
    ptf_hist = ptf.set_index('Ticker')['Shares'] * df_hist
    
    # Calculate the historical value of the portfolio
    ptf_hist['Portfolio'] = ptf_hist.sum(axis=1)

    # Calculate the PNL history for each stock including the aggregate portfolio
    ptf_pnl = ptf_hist - ptf_hist.iloc[0]

    # Calculate the log returns of the portfolio from the historical values
    logret = np.log(ptf_hist / ptf_hist.shift(1))

    # Calculate the cumulative returns of the portfolio from the log returns
    cumret = np.exp(logret.cumsum()) - 1
    cumret.iloc[0] = 0

    # Create a new DataFrame 'tall' and add each unstacked DataFrame as a column
    tall = pd.DataFrame()
    
    tall['value'] = ptf_hist.unstack().to_frame(name='value')['value']
    tall['close'] = df_hist.unstack().to_frame(name='close')['close']
    tall['pnl'] = ptf_pnl.unstack().to_frame(name='pnl')['pnl']
    tall['logret'] = logret.unstack().to_frame(name='logret')['logret']
    tall['cumret'] = cumret.unstack().to_frame(name='cumret')['cumret']

    # Rename the second index column to 'Date'
    tall.index.names = ['Ticker', 'Date']

    return tall

def main():
    st.markdown("""
    ### Portfolio Calculations
    
    This tool analyzes the performance of your investment portfolio over time. It takes your portfolio holdings 
    and historical price data to calculate returns and visualize performance metrics.
    
    **Key features:**
    - Calculates historical value of each position in your portfolio
    - Computes portfolio-level performance metrics
    - Visualizes individual stock and overall portfolio returns
    - Compares performance against the average of your holdings
    
    ### How the Calculations Work
    
    The `perform_calculations()` function processes your portfolio data through several steps:
    
    1. **Position Valuation**: Calculates the historical value of each position by multiplying shares held by historical prices
    2. **Portfolio Aggregation**: Sums up all positions to get total portfolio value over time
    3. **Profit & Loss Tracking**: Measures how much each position has gained or lost since inception
    4. **Return Calculations**: Computes logarithmic returns for more accurate compounding analysis
    5. **Cumulative Performance**: Shows the total return of each position and the overall portfolio
    
    The results are presented in interactive charts that allow you to compare performance across your investments
    and track how your portfolio has evolved over the selected time period.
    """)
    

    has_all_data = True

    if 'ptf' in st.session_state:
        ptf = st.session_state['ptf']
    else:
        st.warning("No portfolio data available. Please upload your portfolio first.")
        has_all_data = False
        
    if 'df_hist' in st.session_state:
        df_hist = st.session_state['df_hist']
    else:
        st.warning("No historical data available. Please fetch historical data first.")
        has_all_data = False

    if has_all_data:
        tall = perform_calculations(ptf, df_hist)
        # tall.to_excel('tall.xlsx', engine='openpyxl')

        st.subheader("Cumulative Returns by Ticker")
        # Bar chart of cumulative returns
        # Create chart data from last day's returns sorted from largest to smallest
        chart_data = pd.DataFrame({
            'Ticker': tall['cumret'].unstack(level=0).iloc[-1].sort_values(ascending=False).index,
            'Return': tall['cumret'].unstack(level=0).iloc[-1].sort_values(ascending=False).values
        })
        # Calculate average return excluding the Portfolio itself
        ticker_returns = chart_data[chart_data['Ticker'] != 'Portfolio']['Return']
        avg_return = ticker_returns.mean()
        
        # Create the bar chart
        bar_chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('Ticker:N', sort=None),  # Use sort=None to preserve the dataframe order
            y=alt.Y('Return:Q', 
               axis=alt.Axis(format='%', title='Return'),  # Format y-axis as percentage with 0 decimals
               scale=alt.Scale(zero=True)),
            color=alt.condition(
            alt.datum.Ticker == 'Portfolio',
            alt.value('orange'),  # Color for 'Portfolio'
            alt.value('steelblue')  # Color for other tickers
            ),
            tooltip=[
            alt.Tooltip('Ticker:N'),
            alt.Tooltip('Return:Q', format='.2%')  # Format tooltip with 2 decimal percentage
            ]
        )
        
        # Create a horizontal rule for the average
        avg_line = alt.Chart(pd.DataFrame({'avg': [avg_return]})).mark_rule(
            strokeDash=[6, 4],
            strokeWidth=2,
            color='red'
        ).encode(
            y='avg:Q'
        )
        
        # Combine the charts
        chart = (bar_chart + avg_line).properties(height=400)
        st.altair_chart(chart, use_container_width=True)

        # Line chart showing return evolution over time
        st.subheader("Portfolio Performance Over Time")
        st.line_chart(tall['cumret'].unstack(level=0))
        # Add checkbox to view the perform_calculations function
    
    if st.checkbox('View perform_calculations() function'):
        source_code = inspect.getsource(perform_calculations)
        st.code(source_code, language='python')
        
        st.write("below you can see the resulting *tall* dataframe")
        st.dataframe(tall)

if __name__ == "__main__":
    main()
