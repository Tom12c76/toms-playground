import streamlit as st

def main():
    st.title("Score to Portfolio")

    # Try to load portfolio data from session state (like advanced_ptf_charts)
    ptf = st.session_state.get('ptf')
    if ptf is not None:
        st.success("Portfolio data loaded successfully!")
        st.dataframe(ptf)
    else:
        st.warning("No portfolio data found in session state. Go back!")
        return

    # Try to load historical data (tall) from session state
    tall = st.session_state.get('tall')
    if tall is not None:
        # st.success("Historical data loaded successfully!")
        # st.dataframe(tall)

        # --- Create logret DataFrame: tickers as columns, date as index ---
        logret = tall.reset_index().pivot(index='Date', columns='Ticker', values='logret')
        # st.subheader("Log Returns (logret) DataFrame")
        # st.dataframe(logret)

        # --- Create cumret: first row zeros, then cumsum of logret ---
        import numpy as np
        cumret = logret.copy()
        cumret.iloc[0] = 0  # set first row to zeros
        cumret = cumret.cumsum()
        # st.subheader("Cumulative Log Returns (cumret)")
        # st.dataframe(cumret)

        # --- Convert cumulative log returns to linear returns ---
        linear_ret = np.exp(cumret) - 1
        st.subheader("Cumulative Linear Returns")
        st.line_chart(linear_ret)

        # --- Calculate risk-adjusted linear return for each stock ---
        # Risk-adjusted return (annualized) = sum(logret) / (std(logret) * sqrt(252)) for each column (stock)
        risk_adj_logret = logret.sum() / (logret.std() * np.sqrt(252))
        # Convert to linear risk-adjusted return: exp(risk_adj_logret) - 1
        risk_adj_linear_ret = np.exp(risk_adj_logret) - 1
        st.subheader("Risk-Adjusted Linear Return (per stock)")
        st.dataframe(risk_adj_linear_ret.rename('Risk-Adj Linear Ret'))

        # --- Calculate z-score and associated probability for each stock ---
        from scipy.stats import norm
        z_scores = risk_adj_logret
        probabilities = norm.cdf(z_scores)
        z_prob_df = z_scores.to_frame('Z-Score')
        z_prob_df['Probability'] = probabilities
        st.subheader("Z-Score and Associated Probability (per stock)")
        st.dataframe(z_prob_df)
    else:
        st.warning("No historical data found in session state. Go back!")
        return