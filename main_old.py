import streamlit as st
from app_sections._1_Getting_started import (
    _0_Retrieving_ETF_Data,
    _1_yfinance_for_stocks,
    _2_Ptf_calculations
)
from app_sections._2_Portfolio_hacks import (
    _1_Advanced_ptf_charts,
    _2_TC_Momentum,
    _3_Score_to_Port,
    _4_Automagic_AA,
    _5_n_Sharpe_portfolio,
    _6_Alpha_Beta_revisited,
    _7_Attribution_revisited,
    _8_Ptf_Blind_Date
)
from app_sections._3_Machine_learning import (
    _1_Correlation_Matrix_revisited,
    _2_Autoencoder_for_Ptf_rebal
)
from app_sections._4_AI_for_reporting import (
    _1_Autogen_HTML_reports,
    _2_Talk_to_your_portfolio
)
from app_sections._5_VizTrader_for_Options import (
    _1_Adv_option_charts
)

# Define pages for each section with titles and icons
sections = {
    "📚 Getting Started": [
        st.Page(_0_Retrieving_ETF_Data.etf_data, title="Retrieving ETF Data", icon="📊"),
        st.Page(_1_yfinance_for_stocks.stock_data, title="YFinance for Stocks", icon="📈"),
        st.Page(_2_Ptf_calculations.portfolio_calcs, title="Portfolio Calculations", icon="🧮")
    ],
    "💼 Portfolio Hacks": [
        st.Page(_1_Advanced_ptf_charts.advanced_charts, title="Advanced Portfolio Charts", icon="📊"),
    #     st.Page(_2_TC_Momentum.momentum, title="TC Momentum", icon="📈"),
    #     st.Page(_3_Score_to_Port.score_portfolio, title="Score to Portfolio", icon="🎯"),
    #     st.Page(_4_Automagic_AA.auto_allocation, title="Automagic Asset Allocation", icon="🎲"),
    #     st.Page(_5_n_Sharpe_portfolio.n_sharpe, title="N-Sharpe Portfolio", icon="📊"),
    #     st.Page(_6_Alpha_Beta_revisited.alpha_beta, title="Alpha Beta Revisited", icon="📈"),
    #     st.Page(_7_Attribution_revisited.attribution, title="Attribution Revisited", icon="🎯"),
    #     st.Page(_8_Ptf_Blind_Date.blind_date, title="Portfolio Blind Date", icon="💘")
    # ],
    # "🤖 Machine Learning": [
    #     st.Page(_1_Correlation_Matrix_revisited.correlation, title="Correlation Matrix", icon="🔄"),
    #     st.Page(_2_Autoencoder_for_Ptf_rebal.autoencoder, title="Autoencoder for Rebalancing", icon="🧠")
    # ],
    # "🎯 AI for Reporting": [
    #     st.Page(_1_Autogen_HTML_reports.html_reports, title="Autogen HTML Reports", icon="📄"),
    #     st.Page(_2_Talk_to_your_portfolio.portfolio_chat, title="Talk to Your Portfolio", icon="💬")
    # ],
    # "📊 VizTrader Options": [
    #     st.Page(_1_Adv_option_charts.option_charts, title="Advanced Option Charts", icon="📈")
    ]
}

# Flatten the sections into a list of pages
pages = [page for section in sections.values() for page in section]

# Set up navigation
pg = st.navigation(pages=pages, position="sidebar", expanded=True)

# Run the selected page
pg.run()