import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from plotly.subplots import make_subplots

def fig_ab(tall_ticker, tall_ptf, ticker_name, ticker_sector):
    """
    Create a figure comparing a specific ticker to the portfolio benchmark.
    
    Parameters:
    -----------
    tall_ticker : DataFrame
        Time series data for the selected ticker
    tall_ptf : DataFrame
        Time series data for the portfolio benchmark
    ticker_name : str
        Name of the selected ticker
    ticker_sector : str
        Sector of the selected ticker
        
    Returns:
    --------
    plotly.graph_objects.Figure
        The complete comparison figure with 3 subplots
    """
    # Calculate key metrics
    ticker_tr = tall_ticker['cumret'].iloc[-1]
    ticker_vol = tall_ticker['logret'].std() * (252 ** 0.5)
    
    ptf_tr = tall_ptf['cumret'].iloc[-1]
    ptf_vol = tall_ptf['logret'].std() * (252 ** 0.5)
    
    # Calculate outperformance (ticker cumret - portfolio cumret)
    # Align both series by date
    ticker_cumret = tall_ticker['cumret']
    ptf_cumret = tall_ptf['cumret']
    
    # Calculate outperformance
    outperformance = ticker_cumret - ptf_cumret
    
    fig = make_subplots(rows=2, cols=3, 
                        shared_yaxes=True,
                        shared_xaxes=True, 
                        subplot_titles=("Outperformance", "XS", "", "Cumulative Returns", "TR", "Risk-Return"),
                        column_widths=[3, 0.5, 1],
                        row_heights=[1, 2],
                        vertical_spacing=0.05
                        )

    ticker_color = '#1f77b4'  # Color for selected ticker
    ptf_color = '#A9A9A9'     # Grey color for portfolio benchmark
    
    # Outperformance - Add outperformance line
    fig.add_trace(
        go.Scatter(x=outperformance.index, y=outperformance, 
                  mode='lines', name='Outperformance', line=dict(color=ticker_color)),
        row=1, col=1
    )

    # Last Cumulative Return - Add both ticker and portfolio benchmark
    fig.add_trace(
        go.Bar(x=[ticker_name], 
              y=[ticker_tr - ptf_tr], 
              name='XS Return', 
              marker=dict(color=[ticker_color]), 
              text=[f"{ticker_tr-ptf_tr:.1%}"], 
              textposition='auto'),
        row=1, col=2
    )
    
    # Cumulative Returns - Add ticker line
    fig.add_trace(
        go.Scatter(x=tall_ticker['cumret'].index, y=tall_ticker['cumret'], 
                  mode='lines', name=ticker_name, line=dict(color=ticker_color)),
        row=2, col=1
    )
    
    # Cumulative Returns - Add portfolio benchmark line
    fig.add_trace(
        go.Scatter(x=tall_ptf['cumret'].index, y=tall_ptf['cumret'], 
                  mode='lines', name='Portfolio', line=dict(color=ptf_color)),
        row=2, col=1
    )

    # Last Cumulative Return - Add both ticker and portfolio benchmark
    fig.add_trace(
        go.Bar(x=[ticker_name, 'Portfolio'], 
              y=[ticker_tr, ptf_tr], 
              name='Total Return', 
              marker=dict(color=[ticker_color, ptf_color]), 
              text=[f"{ticker_tr:.1%}", f"{ptf_tr:.1%}"], 
              textposition='auto'),
        row=2, col=2
    )

    # Risk-Return Scatterplot - Add both ticker and portfolio benchmark
    fig.add_trace(
        go.Scatter(x=[ticker_vol, ptf_vol], 
                  y=[ticker_tr, ptf_tr], 
                  mode='markers+text', 
                  marker=dict(color=[ticker_color, ptf_color], size=[12, 10]),
                  text=[ticker_name, 'Portfolio'],
                  textposition='top center'),
        row=2, col=3
    )

    # Reverse the x-axis for the third subplot and set minimum value to 0
    fig.update_xaxes(autorange='reversed', row=2, col=3, rangemode='tozero', tickformat=".1%")

    fig.update_yaxes(row=1, col=1, tickformat=".1%", title="XS Returns")
    fig.update_yaxes(row=2, col=1, tickformat=".1%", title="Cumulative Returns")
    fig.update_yaxes(row=2, col=2, tickformat=".1%")
    fig.update_yaxes(row=2, col=3, tickformat=".1%")
    fig.update_xaxes(row=2, col=3, tickformat=".1%", title="Volatility")
    
    # Add a horizontal reference line at portfolio return level
    # fig.add_hline(y=ptf_tr, line=dict(color=ptf_color, dash="dash"), row=2, col=1)
    
    # Get the max date and find last year's date
    year_end_dt = pd.Timestamp(year=tall_ticker.index.max().year-1, month=12, 
                                  day=31)
    # draw a vline at the last date of the previous year
    fig.add_vline(x=year_end_dt, line=dict(color=ptf_color, width=0.75), row=2, col=1)




    # Update layout with improved styling
    fig.update_layout(
        showlegend=False,
        height=600, 
        width=1200, 
        title_text=f"{ticker_name} - {ticker_sector}",
        # title_x=0.5,
        template="plotly_white"
    )
    
    return fig

def main():
    
    st.subheader("Alpha & Beta Revisited")

    if 'ptf' in st.session_state:
        ptf = st.session_state['ptf']
    else:
        st.warning("No portfolio data found in session state. Go back!")
        return

    if 'tall' in st.session_state:
        tall = st.session_state.tall
    else:
        st.warning("No calculated data found in session state. Go back!")
        return
    
    tall_ptf = tall.loc['Portfolio']
    
    # create a dropdown to select the ticker from the first level of the index
    ticker = st.selectbox("Select a ticker", tall.index.levels[0].unique())

    # use the ticker to filter the data
    tall_ticker = tall.loc[ticker]
    # get the stock name and sector from ptf dataframe
    ptf_ticker = ptf.set_index('Ticker').loc[ticker]
    
    ticker_name = ptf_ticker['Name']
    ticker_sector = ptf_ticker['Sector']

    # Create the comparison figure using the dedicated function
    fig = fig_ab(tall_ticker, tall_ptf, ticker_name, ticker_sector)
    
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
