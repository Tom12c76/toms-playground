import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import statsmodels.api as sm

def calculate_regression_metrics(tall):
    """
    Calculate regression metrics for each ticker against portfolio returns.
    
    Args:
        tall: Multi-index DataFrame containing ticker data with 'logret' and 'cumret'
        
    Returns:
        DataFrame containing regression metrics and performance attribution
    """
    # Get unique tickers excluding the portfolio
    tickers = [ticker for ticker in tall.index.levels[0].unique() if ticker != 'Portfolio']
    portfolio_returns = tall.loc['Portfolio']['logret']
    
    # Initialize results DataFrame
    results = []
    
    # Loop through each ticker
    for ticker in tickers:
        ticker_data = tall.loc[ticker]
        ticker_returns = ticker_data['logret']
        
        # Prepare data for regression
        valid_data = pd.DataFrame({
            'portfolio': portfolio_returns,
            'ticker': ticker_returns
        }).dropna().replace([np.inf, -np.inf], np.nan).dropna()
        
        # Skip if not enough data
        if len(valid_data) <= 2:
            continue
            
        # Add constant for statsmodels (for alpha)
        X = sm.add_constant(valid_data['portfolio'])
        y = valid_data['ticker']
        
        # Run regression
        try:
            model = sm.OLS(y, X).fit()
            
            # Extract regression statistics
            alpha = model.params['const'] * len(y)  # Annualized alpha
            beta = model.params['portfolio']
            r_squared = model.rsquared
            correl_r = np.sqrt(model.rsquared)
            p_value = model.f_pvalue
            significant = p_value < 0.05
            
            # Performance attribution
            # Calculate total performance (from cumulative returns)
            total_return = tall.loc[ticker]['cumret'].iloc[-1]
            portfolio_total_return = tall.loc['Portfolio']['cumret'].iloc[-1]
            
            # Performance from portfolio return
            perf_from_portfolio = portfolio_total_return
            
            # Performance from beta adjustment
            perf_from_beta = (beta - 1) * portfolio_total_return
            
            # Performance from alpha (annualized alpha needs to be converted to the period's alpha)
            period_length_years = len(ticker_data) / 252  # Assuming 252 trading days per year
            perf_from_alpha = alpha * period_length_years
            
            # Performance error (residual to match total return)
            perf_error = total_return - perf_from_portfolio - perf_from_beta - perf_from_alpha
            
            # Volatility attribution
            ticker_vol = ticker_returns.std() * np.sqrt(252)  # Annualized
            portfolio_vol = portfolio_returns.std() * np.sqrt(252)  # Annualized
            
            # Vol from portfolio
            vol_from_portfolio = portfolio_vol
            
            # Vol from beta adjustment
            vol_from_beta = (beta - 1) * portfolio_vol
            
            # Total vol (actual ticker volatility)
            total_vol = ticker_vol
            
            # Vol error (residual)
            vol_error = total_vol - abs(vol_from_portfolio) - abs(vol_from_beta)
            
            # Store results
            results.append({
                'Ticker': ticker,
                'Alpha': alpha,
                'Beta': beta,
                'Correlation R': correl_r,
                'Variance Explained R2': r_squared,
                'Significant': significant,
                'Perf_Portfolio': perf_from_portfolio,
                'Perf_Beta': perf_from_beta,
                'Perf_Alpha': perf_from_alpha,
                'Perf_Error': perf_error,
                'Total_Return': total_return,
                'Vol_Portfolio': vol_from_portfolio,
                'Vol_Beta': vol_from_beta,
                'Vol_Error': vol_error,
                'Total_Vol': total_vol
            })
            
        except Exception as e:
            st.warning(f"Could not calculate regression for {ticker}: {e}")
    
    # Create DataFrame from results
    df_regression = pd.DataFrame(results)
    
    if not df_regression.empty:
        # Format the DataFrame
        df_regression.set_index('Ticker', inplace=True)
        
        # Round numeric columns for better display
        numeric_cols = df_regression.select_dtypes(include=['float64']).columns
        df_regression[numeric_cols] = df_regression[numeric_cols].round(4)
    
    return df_regression

def fig_ab(ptf, tall, ticker):
    # Extract ticker-specific data
    tall_ticker = tall.loc[ticker]
    tall_ptf = tall.loc['Portfolio']
    
    # Get ticker name and sector from ptf dataframe
    ptf_ticker = ptf.set_index('Ticker').loc[ticker]
    ticker_name = ptf_ticker['Name']
    ticker_sector = ptf_ticker['Sector']
   
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
                        shared_xaxes=False, 
                        subplot_titles=("Daily Log Rtn", "XS", "", "Cumulative Returns", "TR", "Risk-Return"),
                        column_widths=[3, 0.5, 1],
                        row_heights=[1, 2],
                        vertical_spacing=0.05
                        )

    ticker_color = '#1f77b4'  # Color for selected ticker
    ptf_color = '#A9A9A9'     # Grey color for portfolio benchmark
    
    st.write(tall_ticker['logret'])

    # Outperformance - Add outperformance line
    fig.add_trace(
        go.Scatter(x=tall_ticker.index, y=tall_ticker['logret'], 
                  mode='markers', name='Log Rtn', line=dict(color=ticker_color)),
        row=1, col=1
    )

    # let's calculate the mean of tall_ticker['logret']
    ticker_mean = tall_ticker['logret'].mean()
    # Add a horizontal line at the mean
    fig.add_hline(y=ticker_mean, line=dict(color='red', dash="dash"), row=1, col=1)

    # calculate the standard deviation of tall_ticker['logret']
    ticker_std = tall_ticker['logret'].std()

    # now let's create a normal distribution with the same mean and std
    x = pd.Series([ticker_mean + i * ticker_std / 5 for i in range(-50, 51)])
    y = (1 / (ticker_std * (2 * 3.14159) ** 0.5)) * \
        pd.Series([2.71828 ** (-0.5 * ((i - ticker_mean) / ticker_std) ** 2) for i in x])
    
    # Add the normal distribution to the plot in line=1, row=2
    fig.add_trace(
        go.Scatter(x=y, y=x, mode='lines', name='Normal Distribution', line=dict(color='red')),
        row=1, col=2
    )

    # let's add a histogram of the log returns
    fig.add_trace(
        go.Histogram(y=tall_ticker['logret'], nbinsy=50, name='Log Rtn', marker=dict(color=ticker_color)),
        row=1, col=2
    )
    
    # let's add a scatterplot of the log returns
    fig.add_trace(
        go.Scatter(x=tall_ptf['logret'], y=tall_ticker['logret'], mode='markers', name='Log Rtn', marker=dict(color=ticker_color)),
        row=1, col=3
    )

    # let's draw the regression line across the scatterplot
    # First, filter out NaN and infinite values from both series to prevent LinAlgError
    valid_data = pd.DataFrame({
        'x': tall_ptf['logret'],
        'y': tall_ticker['logret']
    }).dropna().replace([np.inf, -np.inf], np.nan).dropna()
    
    # Check if we have enough data to perform the regression
    if len(valid_data) > 1:
        try:
            # Calculate the slope and intercept of the regression line
            slope, intercept = np.polyfit(valid_data['x'], valid_data['y'], 1)
            
            # Create the x values for the regression line
            x_range = pd.Series([valid_data['x'].min(), valid_data['x'].max()])
            # Calculate the y values for the regression line
            y_range = slope * x_range + intercept
            
            # Add the regression line to the plot
            fig.add_trace(
                go.Scatter(x=x_range, y=y_range, mode='lines', name='Regression Line', line=dict(color='red')),
                row=1, col=3
            )
            
            # Optional: Display beta (slope) value
            fig.add_annotation(
                x=valid_data['x'].min() + (valid_data['x'].max() - valid_data['x'].min()) * 0.1,
                y=valid_data['y'].max() - (valid_data['y'].max() - valid_data['y'].min()) * 0.1,
                text=f"Beta: {slope:.2f}",
                showarrow=False,
                row=1, col=3
            )
            
        except np.linalg.LinAlgError as e:
            st.warning(f"Could not calculate regression: {e}")
        except Exception as e:
            st.warning(f"Error in regression calculation: {e}")
    else:
        st.warning("Not enough valid data points to calculate regression line")

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
    
    # Add tabs for different analyses
    tab1, tab2 = st.tabs(["Single Ticker Analysis", "Regression Analysis"])
    
    with tab1:
        # create a dropdown to select the ticker from the first level of the index
        ticker = st.selectbox("Select a ticker", tall.index.levels[0].unique())

        # Create the comparison figure using the updated function
        fig = fig_ab(ptf, tall, ticker)
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Regression Analysis for All Tickers")
        
        # Calculate regression metrics for all tickers
        with st.spinner("Calculating regression metrics for all tickers..."):
            df_regression = calculate_regression_metrics(tall)
        
        if df_regression is not None and not df_regression.empty:
            # Display the regression metrics
            st.write("### Regression Metrics")
            st.dataframe(df_regression[['Alpha', 'Beta', 'Correlation R', 'Variance Explained R2', 'Significant']])
            
            # Display the performance attribution
            st.write("### Performance Attribution")
            perf_cols = ['Perf_Portfolio', 'Perf_Beta', 'Perf_Alpha', 'Perf_Error', 'Total_Return']
            st.dataframe(df_regression[perf_cols])
            
            # Display the volatility attribution
            st.write("### Volatility Attribution")
            vol_cols = ['Vol_Portfolio', 'Vol_Beta', 'Vol_Error', 'Total_Vol']
            st.dataframe(df_regression[vol_cols])
            
            # Save dataframe in session state for other modules to use
            st.session_state.df_regression = df_regression
            
            # Option to download the data
            csv = df_regression.to_csv()
            st.download_button(
                label="Download regression data as CSV",
                data=csv,
                file_name='regression_analysis.csv',
                mime='text/csv',
            )
        else:
            st.warning("Could not calculate regression metrics. Make sure your data has enough valid points.")

if __name__ == "__main__":
    main()
