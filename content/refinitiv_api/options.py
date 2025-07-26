import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

def main():
    st.title("Refinitiv API - Options Data")
    st.info("""
    This page demonstrates how to retrieve options data using the Refinitiv API.
    
    You can fetch options chains, implied volatility, Greeks, and other 
    derivatives data for various underlying instruments.
    """)
    
    # Configuration section
    st.header("Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Underlying instrument
        underlying = st.text_input(
            "Underlying Instrument RIC",
            value="AAPL.O",
            help="Enter the RIC for the underlying instrument"
        )
        
        # Option type
        option_type = st.selectbox(
            "Option Type",
            options=["Call", "Put", "Both"],
            index=2,
            help="Type of options to retrieve"
        )
        
        # Expiration date
        expiry_date = st.date_input(
            "Expiration Date",
            value=datetime.now() + timedelta(days=30),
            help="Options expiration date"
        )
    
    with col2:
        # Strike range
        strike_min = st.number_input(
            "Minimum Strike Price",
            value=150.0,
            step=5.0,
            help="Minimum strike price for options chain"
        )
        
        strike_max = st.number_input(
            "Maximum Strike Price", 
            value=200.0,
            step=5.0,
            help="Maximum strike price for options chain"
        )
        
        # Moneyness filter
        moneyness = st.selectbox(
            "Moneyness Filter",
            options=["All", "ITM", "ATM", "OTM"],
            index=0,
            help="Filter options by moneyness"
        )
    
    # Data fields section
    st.header("Data Fields")
    
    col1, col2 = st.columns(2)
    
    with col1:
        price_fields = st.multiselect(
            "Price Fields",
            options=[
                "TR.BIDPRICE",
                "TR.ASKPRICE", 
                "TR.LASTPRICE",
                "TR.SETTLEMENTPRICE"
            ],
            default=["TR.BIDPRICE", "TR.ASKPRICE"],
            help="Price-related fields"
        )
    
    with col2:
        greek_fields = st.multiselect(
            "Greeks & Risk Fields",
            options=[
                "TR.IMPVOL",
                "TR.DELTA",
                "TR.GAMMA", 
                "TR.THETA",
                "TR.VEGA",
                "TR.RHO"
            ],
            default=["TR.IMPVOL", "TR.DELTA"],
            help="Options Greeks and risk metrics"
        )
    
    # Fetch data button
    if st.button("Fetch Options Data", type="primary"):
        with st.spinner("Fetching options data from Refinitiv API..."):
            # Placeholder for actual API call
            st.info("🚧 **Demo Mode**: This is a placeholder for the actual Refinitiv API implementation.")
            
            # Generate sample options data
            strikes = np.arange(strike_min, strike_max + 5, 5)
            
            sample_options = []
            for strike in strikes:
                for opt_type in (['Call', 'Put'] if option_type == "Both" else [option_type]):
                    sample_options.append({
                        'Strike': strike,
                        'Type': opt_type,
                        'Bid': max(0, np.random.uniform(0.5, 10.0)),
                        'Ask': max(0, np.random.uniform(0.5, 10.0)) + 0.1,
                        'Last': max(0, np.random.uniform(0.5, 10.0)),
                        'ImpliedVol': np.random.uniform(0.15, 0.45),
                        'Delta': np.random.uniform(-1, 1) if opt_type == 'Put' else np.random.uniform(0, 1),
                        'Gamma': np.random.uniform(0, 0.1),
                        'Theta': np.random.uniform(-0.1, 0),
                        'Vega': np.random.uniform(0, 0.3),
                        'Volume': np.random.randint(0, 1000),
                        'OpenInterest': np.random.randint(0, 5000)
                    })
            
            options_df = pd.DataFrame(sample_options)
            
            st.success(f"Successfully retrieved {len(options_df)} options contracts for {underlying}")
            
            # Display options chain
            st.header("Options Chain")
            
            # Filter controls
            col1, col2 = st.columns(2)
            with col1:
                show_volume = st.checkbox("Show Volume > 0 only", value=False)
            with col2:
                sort_by = st.selectbox("Sort by", options=['Strike', 'Volume', 'ImpliedVol'], index=0)
            
            # Apply filters
            display_df = options_df.copy()
            if show_volume:
                display_df = display_df[display_df['Volume'] > 0]
            
            display_df = display_df.sort_values(sort_by)
            
            # Format display
            display_df['Bid'] = display_df['Bid'].round(2)
            display_df['Ask'] = display_df['Ask'].round(2)
            display_df['Last'] = display_df['Last'].round(2)
            display_df['ImpliedVol'] = (display_df['ImpliedVol'] * 100).round(1)
            display_df['Delta'] = display_df['Delta'].round(3)
            display_df['Gamma'] = display_df['Gamma'].round(4)
            display_df['Theta'] = display_df['Theta'].round(4)
            display_df['Vega'] = display_df['Vega'].round(3)
            
            st.dataframe(display_df, use_container_width=True)
            
            # Visualizations
            st.header("Options Analysis")
            
            # Implied Volatility Smile
            st.subheader("Implied Volatility Smile")
            
            calls_data = options_df[options_df['Type'] == 'Call']
            puts_data = options_df[options_df['Type'] == 'Put']
            
            fig_iv = go.Figure()
            
            if not calls_data.empty:
                fig_iv.add_trace(go.Scatter(
                    x=calls_data['Strike'],
                    y=calls_data['ImpliedVol'] * 100,
                    mode='lines+markers',
                    name='Calls',
                    line=dict(color='green')
                ))
            
            if not puts_data.empty:
                fig_iv.add_trace(go.Scatter(
                    x=puts_data['Strike'],
                    y=puts_data['ImpliedVol'] * 100,
                    mode='lines+markers',
                    name='Puts',
                    line=dict(color='red')
                ))
            
            fig_iv.update_layout(
                title="Implied Volatility by Strike Price",
                xaxis_title="Strike Price",
                yaxis_title="Implied Volatility (%)",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_iv, use_container_width=True)
            
            # Greeks visualization
            if not options_df.empty:
                st.subheader("Options Greeks")
                
                greek_choice = st.selectbox(
                    "Select Greek to visualize",
                    options=['Delta', 'Gamma', 'Theta', 'Vega']
                )
                
                fig_greek = go.Figure()
                
                if not calls_data.empty:
                    fig_greek.add_trace(go.Scatter(
                        x=calls_data['Strike'],
                        y=calls_data[greek_choice],
                        mode='lines+markers',
                        name=f'Calls {greek_choice}',
                        line=dict(color='green')
                    ))
                
                if not puts_data.empty:
                    fig_greek.add_trace(go.Scatter(
                        x=puts_data['Strike'],
                        y=puts_data[greek_choice],
                        mode='lines+markers',
                        name=f'Puts {greek_choice}',
                        line=dict(color='red')
                    ))
                
                fig_greek.update_layout(
                    title=f"{greek_choice} by Strike Price",
                    xaxis_title="Strike Price",
                    yaxis_title=greek_choice,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_greek, use_container_width=True)
    
    # Code example section
    st.header("Sample Code")
    st.code("""
import refinitiv.data as rd

# Initialize session
rd.open_session()

# Get options chain
options_data = rd.get_data(
    universe='{underlying}',
    fields=[
        'TR.BIDPRICE',
        'TR.ASKPRICE', 
        'TR.IMPVOL',
        'TR.DELTA',
        'TR.GAMMA'
    ],
    parameters={{
        'SDate': '{expiry_date}',
        'StrikeMin': {strike_min},
        'StrikeMax': {strike_max},
        'OptionType': '{option_type}'
    }}
)

print(options_data.head())
""".format(
    underlying=underlying,
    expiry_date=expiry_date,
    strike_min=strike_min,
    strike_max=strike_max,
    option_type=option_type
), language='python')
    
    # Documentation section
    st.header("Documentation")
    st.markdown("""
    ### Key Parameters:
    
    - **Underlying**: The underlying instrument RIC
    - **Strike Range**: Minimum and maximum strike prices
    - **Expiration Date**: Options expiration date
    - **Option Type**: Call, Put, or Both
    - **Moneyness**: ITM (In-the-Money), ATM (At-the-Money), OTM (Out-of-the-Money)
    
    ### Available Fields:
    
    **Price Fields:**
    - **TR.BIDPRICE**: Bid price
    - **TR.ASKPRICE**: Ask price
    - **TR.LASTPRICE**: Last traded price
    - **TR.SETTLEMENTPRICE**: Settlement price
    
    **Greeks & Risk Metrics:**
    - **TR.IMPVOL**: Implied volatility
    - **TR.DELTA**: Price sensitivity to underlying
    - **TR.GAMMA**: Delta sensitivity to underlying
    - **TR.THETA**: Time decay
    - **TR.VEGA**: Volatility sensitivity
    - **TR.RHO**: Interest rate sensitivity
    
    ### Common Use Cases:
    - Options chain analysis
    - Implied volatility smile construction
    - Greeks-based risk management
    - Options screening and filtering
    """)
