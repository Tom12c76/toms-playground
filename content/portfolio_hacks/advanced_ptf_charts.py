import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from plotly.subplots import make_subplots


def main():
    st.subheader("Advanced Portfolio Charts")

    if 'ptf' in st.session_state:
        ptf = st.session_state['ptf']
    else:
        st.warning("No portfolio data found in session state. Go back!")
        #stop the script
        return

    if 'tall' in st.session_state:
        tall = st.session_state.tall
    else:
        st.warning("No calculated data found in session state. Go back!")
        #stop the script
        return
    
    # create a dropdown to select the ticker from the first level of the index
    ticker = st.selectbox("Select a ticker", tall.index.levels[0].unique())

    # use the ticker to filter the data
    tall_ticker = tall.loc[ticker]
    # get the stock name and sector from ptf dataframe
    ptf_ticker = ptf.set_index('Ticker').loc[ticker]
    
    ticker_name = ptf_ticker['Name']
    ticker_sector = ptf_ticker['Sector']

    # let's write the final cumaltive return
    ticker_tr = tall_ticker['cumret'].iloc[-1]
    # st.write(f"Final Cumulative Return: {ticker_tr:.2%}")
    ticker_vol = tall_ticker['logret'].std() * (252 ** 0.5)
    # st.write(f"Realized Volatility: {ticker_vol:.2%}")
    
    fig = make_subplots(rows=1, cols=3, 
                        shared_yaxes=True, 
                        subplot_titles=("Cumulative Returns", "TR", "Risk-Return"),
                        column_widths=[3, 0.5, 1]
                        )

    color = '#1f77b4'  # Define a color to be used for all sub-plots

    # Cumulative Returns
    fig.add_trace(
        go.Scatter(x=tall_ticker['cumret'].index, y=tall_ticker['cumret'], mode='lines', name='Cumulative Returns', line=dict(color=color)),
        row=1, col=1
    )

    # Last Cumulative Return
    fig.add_trace(
        go.Bar(x=[ticker_name], y=[ticker_tr], name='Total Return', marker=dict(color=color), text=[f"{ticker_tr:.1%}"], textposition='auto'),
        row=1, col=2
    )

    # Cumulative Returns vs Volatility
    fig.add_trace(
        go.Scatter(x=[ticker_vol], y=[ticker_tr], mode='markers', name='Cumulative Returns vs Volatility', marker=dict(color=color)),
        row=1, col=3
    )

    # Reverse the x-axis for the third subplot and set minimum value to 0
    fig.update_xaxes(autorange='reversed', row=1, col=3, rangemode='tozero', tickformat=".1%")

    fig.update_yaxes(row=1, col=1, tickformat=".1%")
    fig.update_yaxes(row=1, col=2, tickformat=".1%")
    fig.update_yaxes(row=1, col=3, tickformat=".1%")
    

    # Get rid of legend
    fig.update_layout(showlegend=False)
    fig.update_layout(height=600, width=1200, title_text=f"{ticker_name} - {ticker_sector}")
    
    st.plotly_chart(fig)

if __name__ == "__main__":
    main()

