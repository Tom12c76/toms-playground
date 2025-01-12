import pandas as pd
import requests, os
import streamlit as st
from streamlit.hello.utils import show_code
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

my_colors = px.colors.qualitative.G10 * 10

def create_portfolio_analysis_plot(ptf: pd.DataFrame) -> go.Figure:
    """
    Create a portfolio analysis plot with three subplots:
    - Bar chart of portfolio weights (top left)
    - Waterfall chart of cumulative weights (top right)
    - Box plot of weight distribution (bottom left)
    
    Args:
        ptf (pd.DataFrame): Portfolio dataframe with columns ['Name', 'Weight (%)']
    
    Returns:
        go.Figure: Plotly figure object with configured subplots
    """
    # Create subplot layout
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Portfolio Weights", "Cumulative Weights", None),
        specs=[[{}, {}], [{}, None]],
        vertical_spacing=0.02,
        horizontal_spacing=0.05,
        row_heights=[0.9, 0.1]
    )

    # Add bar chart
    fig.add_trace(
        go.Bar(
            x=ptf['Weight (%)'],
            y=ptf['Name'],
            orientation='h',
            text=ptf['Weight (%)'].round(1).astype(str) + '%',
            textposition='outside',
            showlegend=False,
            marker_color=my_colors[0]
        ),
        row=1, col=1
    )


    # Add waterfall chart
    fig.add_trace(
        go.Waterfall(
            x=ptf['Weight (%)'],
            y=ptf['Name'],
            orientation='h',
            text=ptf['Weight (%)'].cumsum().round(1).astype(str) + '%',
            textposition='outside',
            measure=['relative'] * len(ptf),
            connector={"visible": False},
            showlegend=False,
            increasing={"marker": {"color": my_colors[0]}},
        ),
        row=1, col=2
    )
    
    # Find the index of the first value where cumulative weight exceeds 50%
    for idx in [ptf['Weight (%)'].cumsum().gt(50).idxmax(),
                ptf['Weight (%)'].cumsum().gt(80).idxmax()]:
        fig.add_trace(go.Scatter(
            x=[0, ptf['Weight (%)'].cumsum().iloc[idx-1]],
            y=[ptf['Name'].iloc[idx]] * 2,
            mode='lines+text',
            line={'color': 'grey', 'width':1.5},
            text=[f'Top {idx+1} stocks', ''],
            textposition='top right',
            showlegend=False
        ), row=1, col=2)

    # Add box plot
    fig.add_trace(
        go.Box(
            x=ptf['Weight (%)'],
            name='Weight Distribution',
            boxpoints='all',
            showlegend=False,
            marker_color=my_colors[0]
        ),
        row=2, col=1
    )

    # Update layout
    fig.update_layout(
        height=1000,
        showlegend=False,
        yaxis={'autorange': 'reversed'},
        yaxis2={'autorange': 'reversed'},
    )

    # Sync axes
    fig.update_xaxes(row=1, col=1, showticklabels=False)
    fig.update_xaxes(row=1, col=2, showticklabels=False)
    fig.update_xaxes(matches='x', row=2, col=1, showticklabels=False)

    fig.update_yaxes(matches='y', row=1, col=2, showticklabels=False)

    return fig

def get_indu():

    # URL of the file to download
    CIND_url = (
        'https://www.blackrock.com/uk/intermediaries/products/253713/'
        'ishares-dow-jones-industrial-average-ucits-etf/1472631233320.ajax'
        '?fileType=csv&fileName=CIND_holdings&dataType=fund'
    )

    # Download the file
    response = requests.get(CIND_url)
    response.raise_for_status()  # Check if the request was successful

    # Create the data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Save the file locally
    with open('data/CIND.csv', 'wb') as file:
        file.write(response.content)

    # Load portfolio file from local directory
    portfolio_file_path = 'data/CIND.csv'  # Update with your CSV file name

    # Read the portfolio CSV file
    as_of_dt = pd.read_csv(portfolio_file_path, nrows=1).columns[1]
    as_of_dt = pd.to_datetime(as_of_dt).date()
    ptf = pd.read_csv(portfolio_file_path, skiprows=2, thousands=',', decimal='.')
    ptf['As Of Date'] = as_of_dt
    ptf = ptf.dropna(subset=['Name'])
    ptf = ptf[ptf['Asset Class'] == 'Equity']
    ptf['Weight (%)'] = ptf['Market Value'] / ptf['Market Value'].sum() * 100
    ptf = ptf.drop('Notional Value', axis=1)
    ptf = ptf.sort_values('Weight (%)', ascending=False)
    
    st.dataframe(
        ptf.set_index('Ticker'),
        hide_index=False,
        column_config={
            "Weight (%)": st.column_config.NumberColumn(
                format="%.2f%%"
            ),
            "Market Value": st.column_config.NumberColumn(
                format="%.0f"
            )
        },
        height=500,  # Set a fixed height
        use_container_width=True  # Make dataframe use full width
    )

    st.info(
        """
        The portfolio consists of 30 stocks. The weight of each stock is determined by the market value of the stock.
        The stock with the highest market value has the highest weight in the portfolio.
        """
    )

    # Usage in main code:
    fig = create_portfolio_analysis_plot(ptf)
    st.plotly_chart(fig)

    return None

st.set_page_config(page_title="First things first", page_icon="📹")

st.markdown("## Retrieve the Portfolio")
st.sidebar.header("Animation Demo")

st.info(
    """
To kick off things we need to define a portfolio to work with.
I like to use the
**iShares Dow Jones Industrial Average UCITS ETF (CIND)**
as it's a simple and well-known portfolio. It only holds 30 stocks
and the price history of the underlying stocks is easy to retrieve.
Remember that the Dow Industrial Average holds an equal amount of shares of each stock!
This means that the stock with the highest price will have the
highest weight in the portfolio.
To replicate the portfolio we can buy either 1 or 10 or 100 shares
of each stock and we're good to go. Or we can just use the amounts that
are in the actual ETF.
"""
)

get_indu()

show_code(get_indu)

# Store filtered portfolio in session state for later use
st.session_state['ptf'] = ptf