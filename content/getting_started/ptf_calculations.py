import streamlit as st
import pandas as pd
import numpy as np

def perform_calculations(ptf, df_hist):
    """
    Perform calculations using portfolio and historical data
    Returns a tuple of (portfolio history, log returns)
    """
    # Calculate historical value
    ptf_hist = ptf.set_index('Ticker')['Shares'] * df_hist
    ptf_hist['Portfolio'] = ptf_hist.sum(axis=1)

    logret = np.log(ptf_hist / ptf_hist.shift(1))

    return ptf_hist, logret

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
        ptf_hist, logret = perform_calculations(ptf, df_hist)
        st.write("Ptf Hist")
        st.dataframe(ptf_hist.unstack().to_frame(name='close'))
        st.write("Logret")
        st.dataframe(logret.unstack().to_frame(name='logret'))

