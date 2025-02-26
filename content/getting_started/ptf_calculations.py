import streamlit as st
import pandas as pd
import numpy as np

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
    # This assumes that the number of shares is constant over the time period
    logret = np.log(ptf_hist / ptf_hist.shift(1))

    # Calculate the cumulative returns of the portfolio from the log returns
    cumret = np.exp(logret.cumsum()) - 1
    cumret.iloc[0] = 0

    # Create a new DataFrame 'tall' and add each unstacked DataFrame as a column
    tall = pd.DataFrame()

    tall['close'] = df_hist.unstack().to_frame(name='close')['close']
    tall['value'] = ptf_hist.unstack().to_frame(name='value')['value']
    tall['pnl'] = ptf_pnl.unstack().to_frame(name='pnl')['pnl']
    tall['logret'] = logret.unstack().to_frame(name='logret')['logret']
    tall['cumret'] = cumret.unstack().to_frame(name='cumret')['cumret']

    # Rename the second index column to 'Date'
    tall.index.names = ['Ticker', 'Date']

    return tall

def main():
    st.subheader("Ptf Calculations")
    st.markdown("This is the content for Ptf calculations.")

    has_all_data = True

    if 'ptf' in st.session_state:
        ptf = st.session_state['ptf']
    else:
        st.write("No Ptf data available.")
        has_all_data = False
        
    if 'df_hist' in st.session_state:
        df_hist = st.session_state['df_hist']
    else:
        st.write("No historical data available.")
        has_all_data = False

    if has_all_data:
        tall = perform_calculations(ptf, df_hist)
        st.dataframe(tall['cumret'].unstack(level=0))
        st.bar_chart(tall['cumret'].unstack(level=0).iloc[-1])
        st.line_chart(tall['cumret'].unstack(level=0))

if __name__ == "__main__":
    main()

