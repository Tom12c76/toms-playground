import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


def create_stock_comparison_figure(tall, ptf, ticker):
    """
    Create a figure comparing a specific ticker to the portfolio benchmark.
    
    Parameters:
    -----------
    tall : DataFrame
        Time series data for all tickers including portfolio
    ptf : DataFrame
        Portfolio configuration dataframe
    ticker : str
        Ticker symbol to analyze
        
    Returns:
    --------
    plotly.graph_objects.Figure
        The complete comparison figure with multiple subplots
    """
    # Extract the required data
    tall_ptf = tall.loc['Portfolio']
    tall_ticker = tall.loc[ticker]
    
    # Get ticker information
    ptf_ticker = ptf.set_index('Ticker').loc[ticker]
    ticker_name = ptf_ticker['Name']
    ticker_sector = ptf_ticker['Sector']
    
    # Calculate key metrics
    ticker_tr = tall_ticker['cumret'].iloc[-1]
    ticker_vol = tall_ticker['logret'].std() * (252 ** 0.5)
    
    ptf_tr = tall_ptf['cumret'].iloc[-1]
    ptf_vol = tall_ptf['logret'].std() * (252 ** 0.5)

    # Calculate outperformance (ticker cumret - portfolio cumret)
    ticker_cumret = tall_ticker['cumret']
    ptf_cumret = tall_ptf['cumret']

    # Calculate outperformance
    outperformance = ticker_cumret - ptf_cumret
    
    # Calculate excess return
    excess_return = ticker_tr - ptf_tr

    # Find the minimum and maximum excess returns to fix the plot range
    cumret = tall['cumret'].reset_index().pivot(index='Date', columns='Ticker', values='cumret')   
    excess_returns = cumret.sub(cumret['Portfolio'], axis=0).drop('Portfolio', axis=1)

    logret = tall['logret'].reset_index().pivot(index='Date', columns='Ticker', values='logret')
    vol = logret.std() * (252 ** 0.5)

    # let's calculate the total return from the log returns for all tickers
    tr = np.exp(logret.sum())-1
    
    # Calculate the correlation between ticker and portfolio
    corr = logret[ticker].corr(logret['Portfolio'])

    # Calculate the final weight of the ticker in the portfolio
    ticker_in_ptf_final_weight = tall_ticker.iloc[-1]['value']/tall_ptf.iloc[-1]['value']
    # how much of ticker do i need to go short to get the portfolio performance without the ticker?
    short_ticker_weight = ticker_in_ptf_final_weight/(1 - ticker_in_ptf_final_weight)
    
    # Calculate efficient frontier points for different weight combinations
    # Extend range to include negative weights (short positions) and ensure zero weight is included
    weights = np.linspace(-short_ticker_weight, 1, 30)
    if 0 not in weights:
        weights = np.sort(np.append(weights, 0))
    ef = pd.DataFrame(weights, columns=['w_ticker'])

    ef['w_portfolio'] = 1 - ef['w_ticker']
    ef['v_ticker'] = ticker_vol
    ef['v_portfolio'] = ptf_vol
    # let's add a column that shows the allocation to ticker in the portfolio
    ef['w_ticker_in_ptf'] = ef['w_ticker'] + ef['w_portfolio'] * ticker_in_ptf_final_weight
    
    # Calculate portfolio variance and resulting risk/return for each weight combination
    # Portfolio variance = w1σ1^2 + w2σ2^2 + 2w1w2Cov
    # Cov = p(1,2)σ1σ2, where p(1,2)=correlation
    ef['v_p'] = np.sqrt(
        ef.w_ticker * ef.v_ticker ** 2 + 
        ef.w_portfolio * ef.v_portfolio ** 2 + 
        2 * ef.w_ticker * ef.w_portfolio * corr * ef.v_ticker * ef.v_portfolio
    )

    # Calculate expected return for each weight combination
    ef['r_p'] = ef.w_ticker * ticker_tr + ef.w_portfolio * ptf_tr
    
    # Find the point where total weight in ticker is zero
    zero_exposure_idx = np.abs(ef['w_ticker_in_ptf']).idxmin()
    zero_exposure_point = ef.iloc[zero_exposure_idx]

    # Create a color scheme for the plot
    ticker_color = '#1f77b4'  # Color for selected ticker
    ptf_color = '#A9A9A9'     # Grey color for portfolio benchmark

    # Create a figure with subplots        
    fig = make_subplots(rows=2, cols=3, 
                        shared_yaxes=True,
                        shared_xaxes=True, 
                        subplot_titles=("Excess Return", "XS", "", "Total Return", "TR", "Risk-Return"),
                        column_widths=[3, 0.5, 1],
                        row_heights=[1, 2],
                        vertical_spacing=0.05
                        )
    
    # Outperformance - Add outperformance line
    fig.add_trace(
        go.Scatter(x=outperformance.index, y=outperformance, 
                  mode='lines', name='Outperformance', line=dict(color=ticker_color)),
        row=1, col=1
    )

    # Outperformance - Add outperformance bar chart
    fig.add_trace(
        go.Bar(
            x=[ticker],
            y=[excess_return],
            name='XS Return',
            marker_color=ticker_color,
            text=f"{excess_return:.1%}",
            textposition='auto'
        ),
        row=1, col=2
    )
     
    # Cumulative Returns - Add portfolio benchmark line
    fig.add_trace(
        go.Scatter(x=tall_ptf['cumret'].index, y=tall_ptf['cumret'], 
                  mode='lines', name='Portfolio', line=dict(color=ptf_color)),
        row=2, col=1
    )
   
    # Cumulative Returns - Add ticker line
    fig.add_trace(
        go.Scatter(x=tall_ticker['cumret'].index, y=tall_ticker['cumret'], 
                  mode='lines', name=ticker_name, line=dict(color=ticker_color)),
        row=2, col=1
    )
    
    # Last Cumulative Return - Add both ticker and portfolio benchmark
    fig.add_trace(
        go.Bar(x=[ticker, 'Ptf'], 
              y=[ticker_tr, ptf_tr], 
              name='Total Return', 
              marker=dict(color=[ticker_color, ptf_color]), 
              text=[f"{ticker_tr:.1%}", f"{ptf_tr:.1%}"], 
              textposition='auto'),
        row=2, col=2
    )

    # Risk-Return Scatterplot - Add all tickers
    fig.add_trace(
        go.Scatter(x=vol.drop([ticker, 'Portfolio']), 
                  y=tr.drop([ticker, 'Portfolio']), 
                  mode='markers', 
                  name='',
                  marker=dict(color=ptf_color, size=8, opacity=0.4),
                  text=vol.drop([ticker, 'Portfolio']).index,
                  hovertemplate='%{text}<br>Vol: %{x:.1%}<br>Return: %{y:.1%}'),
        row=2, col=3
    )
        
    # Add a vertical line for the portfolio benchmark
    fig.add_vline(x=ptf_vol, line=dict(color=ptf_color, width=0.75, dash='dash'), row=2, col=3)
    # Add a horizontal line for the portfolio benchmark
    fig.add_hline(y=ptf_tr, line=dict(color=ptf_color, width=0.75, dash='dash'), row=2, col=3) 
    
    # Add efficient frontier line showing different weight combinations
    fig.add_trace(
        go.Scatter(x=ef['v_p'],
                  y=ef['r_p'],
                  mode='lines',
                  name='Efficient Frontier',
                  line=dict(color=ticker_color, dash='dot', width=1),
                  hovertemplate='Risk: %{x:.1%}<br>Return: %{y:.1%}<br>Weight: %{customdata:.1%}<extra></extra>',
                  customdata=ef['w_ticker']),
        row=2, col=3
    )

    # Add a simple vertical line marker at the point of zero exposure
    fig.add_trace(
        go.Scatter(
            x=[zero_exposure_point['v_p']],
            y=[zero_exposure_point['r_p']],
            mode='markers',
            marker=dict(
                symbol='line-ns',
                size=10,
                line=dict(width=2, color=ticker_color)
            ),
            name='Zero Exposure',
            showlegend=False,
            hoverinfo='text',
            hovertext=f"Zero Exposure: {zero_exposure_point['v_p']:.1%}"
        ),
        row=2, col=3
    )

    # Risk-Return Scatterplot - Add both ticker and portfolio benchmark
    fig.add_trace(
        go.Scatter(x=[ticker_vol, ptf_vol], 
                  y=[ticker_tr, ptf_tr], 
                  mode='markers+text', 
                  marker=dict(
                      color=[ticker_color, ptf_color], 
                      size=[12, 10],
                      symbol=['circle', 'square']
                  ),
                  text=[ticker, ''],
                  textposition='top center'),
        row=2, col=3
    )
    
    # Update x-axis and y-axis properties
    fig.update_xaxes(autorange='reversed', row=2, col=3, rangemode='tozero', tickformat=".1%")
    fig.update_yaxes(row=1, col=1, tickformat=".1%", title="XS Returns", 
                     range=[excess_returns.min().min(), excess_returns.max().max()])
    fig.update_yaxes(row=2, col=1, tickformat=".1%", title="Cumulative Returns", 
                     range=[tall['cumret'].min(), tall['cumret'].max()])
    fig.update_yaxes(row=2, col=2, tickformat=".1%")
    fig.update_yaxes(row=2, col=3, tickformat=".1%")
    fig.update_xaxes(row=2, col=3, tickformat=".1%", title="Volatility")
    
    # Get the max date and find last year's date
    year_end_dt = pd.Timestamp(year=tall_ticker.index.max().year-1, month=12, day=31)
    # draw a vline at the last date of the previous year
    fig.add_vline(x=year_end_dt, line=dict(color=ptf_color, width=0.75), row=2, col=1)

    # Update layout with improved styling
    fig.update_layout(
        showlegend=False,
        height=600, 
        width=1200, 
        title_text=f"[{ticker}] {ticker_name} - {ticker_sector}",
        template="plotly_white"
    )
    
    return fig

def main():

    st.subheader("Advanced Portfolio Charts")

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

    # Get all available sectors from the portfolio data
    available_sectors = sorted(ptf['Sector'].unique().tolist())
    
    # Create two columns for filters
    col1, col2 = st.columns(2)
    
    # Create a multi-select for sectors in the first column
    with col1:
        selected_sectors = st.multiselect("Filter by sector", available_sectors)
        
    # Filter tickers by selected sectors if any are selected
    if selected_sectors:
        filtered_ptf = ptf[ptf['Sector'].isin(selected_sectors)]
        available_tickers = filtered_ptf['Ticker'].unique().tolist()
    else:
        # If no sectors selected, show all tickers
        available_tickers = tall.index.levels[0].unique().tolist()
    
    # Create a dropdown to select the ticker from the filtered list in the second column
    with col2:
        ticker = st.selectbox("Select a ticker", available_tickers)
    

    # Create the comparison figure using the dedicated function with simplified parameters
    fig = create_stock_comparison_figure(tall, ptf, ticker)
    
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
