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
            "AI for reporting",
            "Refinitiv API"
        ],
        icons=['house', 'gear', 'graph-up', 'robot', 'file-earmark-text', 'cloud-download'],
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
                     "Automagic AA", "p Sharpe portfolio", "Alpha Beta revisited",
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
        # now let's create a sub_selected for the Machine Learning Section:
    elif selected == "Machine learning":
        sub_selected = option_menu(
            menu_title=None,
            options=["Correlation Matrix revisited", "PCA analysis", "Autoencoder for Ptf rebal", "Clustering"],
            icons=['bi-grid-3x3-gap', 'graph-up', 'shuffle', 'bi-diagram-3'],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important"},
                "nav-link": {"font-size": "14px", "text-align": "left", "margin": "0px"}
            }
        )
    elif selected == "AI for reporting":
        sub_selected = option_menu(
            menu_title=None,
            options=["News Summaries", "Autogen HTML reports", "Talk to your portfolio", "Fund Profile Generator"],
            icons=['file-earmark-text', 'chat-dots', 'bi-megaphone', 'bank'],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important"},
                "nav-link": {"font-size": "14px", "text-align": "left", "margin": "0px"}
            }
        )
    elif selected == "Refinitiv API":
        sub_selected = option_menu(
            menu_title=None,
            options=["get_history", "options"],
            icons=['clock-history', 'list-ul'],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important"},
                "nav-link": {"font-size": "14px", "text-align": "left", "margin": "0px"}
            }
        )

# Add to your navigation menu
with st.sidebar:
    if st.checkbox("🔐 Admin Mode", help="For credential management"):
        st.subheader("Secrets Status")
        
        # Check which secrets are configured
        secrets_status = {}
        try:
            secrets_status["Google Gemini"] = "✅" if "google" in st.secrets else "❌"
            secrets_status["Refinitiv"] = "✅" if "refinitiv" in st.secrets else "❌"
        except:
            secrets_status = {"Error": "❌ No secrets file found"}
        
        for service, status in secrets_status.items():
            st.write(f"{service}: {status}")

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
        "p Sharpe portfolio": "content.portfolio_hacks.p_sharpe_portfolio",
        "Alpha Beta revisited": "content.portfolio_hacks.alpha_beta_revisited",
        "Attribution revisited": "content.portfolio_hacks.attribution_revisited",
        "Ptf Blind Date": "content.portfolio_hacks.ptf_blind_date"
    },
    "Machine learning": {
        "Correlation Matrix revisited": "content.machine_learning.correlation_matrix_revisited",
        "Autoencoder for Ptf rebal": "content.machine_learning.autoencoder_for_ptf_rebal",
        "PCA analysis": "content.machine_learning.pca_analysis",
        "Clustering": "content.machine_learning.clustering"
    },
    "AI for reporting": {
        "News Summaries": "content.ai_for_reporting.news_summaries",
        "Autogen HTML reports": "content.ai_for_reporting.autogen_html_reports",
        "Talk to your portfolio": "content.ai_for_reporting.talk_to_your_portfolio",
        "Fund Profile Generator": "content.ai_for_reporting.fund_profile_generator"
    },
    "Refinitiv API": {
        "get_history": "content.refinitiv_api.get_history",
        "options": "content.refinitiv_api.options"
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
