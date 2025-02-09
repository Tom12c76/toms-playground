import sys
sys.dont_write_bytecode = True

import streamlit as st
from streamlit_option_menu import option_menu
import importlib

# Custom CSS
st.markdown("""
<style>
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .nav-link {
        padding: 0.5rem 1rem;
        color: #495057;
        border-radius: 0.25rem;
        margin: 0.2rem 0;
        transition: all 0.2s;
    }
    .nav-link:hover {
        background-color: #e9ecef;
        color: #212529;
    }
    .nav-link.active {
        background-color: #0d6efd;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation using option_menu
with st.sidebar:
    st.title("Navigation")
    
    selected = option_menu(
        menu_title=None,
        options=[
            "Welcome to my playground",
            "Getting started",
            "Portfolio hacks",
            "Machine learning",
            "AI for reporting"
        ],
        icons=['house', 'gear', 'graph-up', 'robot', 'file-earmark-text'],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important"},
            "nav-link": {"font-size": "14px", "text-align": "left", "margin": "0px"}
        }
    )
    
    # Submenu based on selection
    sub_selected = None
    if selected == "Getting started":
        sub_selected = option_menu(
            menu_title=None,
            options=["Retrieve ETF data", "yfinance for stocks", "Ptf calculations"],
            icons=['database', 'cash-stack', 'calculator'],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important"},
                "nav-link": {"font-size": "14px", "text-align": "left", "margin": "0px"}
            }
        )
    elif selected == "Portfolio hacks":
        sub_selected = option_menu(
            menu_title=None,
            options=["Advanced ptf charts", "TC Momentum", "Score to Port",
                     "Automagic AA", "n Sharpe portfolio", "Alpha Beta revisited",
                     "Attribution revisited", "Ptf Blind Date"],
            icons=['bar-chart', 'arrow-up-right', 'stars',
                   'magic', 'graph-up', 'calculator',
                   'pie-chart', 'shuffle'],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important"},
                "nav-link": {"font-size": "14px", "text-align": "left", "margin": "0px"}
            }
        )

# Define the page structure
pages = {
    "Welcome to my playground": "content.welcome",
    "Getting started": {
        "Retrieve ETF data": "content.getting_started.retrieve_etf_data",
        "yfinance for stocks": "content.getting_started.yfinance_for_stocks",
        "Ptf calculations": "content.getting_started.ptf_calculations"
    },
    "Portfolio hacks": {
        "Advanced ptf charts": "content.portfolio_hacks.advanced_ptf_charts",
        "TC Momentum": "content.portfolio_hacks.tc_momentum",
        "Score to Port": "content.portfolio_hacks.score_to_port",
        "Automagic AA": "content.portfolio_hacks.automagic_aa",
        "n Sharpe portfolio": "content.portfolio_hacks.n_sharpe_portfolio",
        "Alpha Beta revisited": "content.portfolio_hacks.alpha_beta_revisited",
        "Attribution revisited": "content.portfolio_hacks.attribution_revisited",
        "Ptf Blind Date": "content.portfolio_hacks.ptf_blind_date"
    },
    "Machine learning": {
        "Correlation Matrix revisited": "content.machine_learning.correlation_matrix_revisited",
        "Autoencoder for Ptf rebal": "content.machine_learning.autoencoder_for_ptf_rebal"
    },
    "AI for reporting": {
        "Autogen HTML reports": "content.ai_for_reporting.autogen_html_reports",
        "Talk to your portfolio": "content.ai_for_reporting.talk_to_your_portfolio"
    }
}

# Load the appropriate page content
if selected in pages:
    if isinstance(pages[selected], dict) and sub_selected:
        module_name = pages[selected].get(sub_selected)
    else:
        module_name = pages[selected]
    
    if module_name:
        module = importlib.import_module(module_name)
        if hasattr(module, 'main'):
            module.main()
