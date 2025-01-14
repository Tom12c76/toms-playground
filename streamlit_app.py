import streamlit as st
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components
import importlib
import os

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

# Define the landing page
def landing_page():
    st.title("Welcome to the Portfolio Analysis App")
    st.write("This is the landing page of the Portfolio Analysis App. Use the sidebar to navigate to different sections.")

# Initialize session state
if 'page' not in st.session_state:
    st.session_state['page'] = 'landing'

# Sidebar navigation using option_menu
with st.sidebar:
    st.image("https://your-logo-url.com/logo.png", width=50)  # Add your logo
    st.title("Navigation")
    
    selected = option_menu(
        menu_title=None,
        options=[
            "Getting started",
            "Portfolio hacks",
            "Machine learning",
            "AI for reporting"
        ],
        icons=['house', 'graph-up', 'robot', 'file-earmark-text'],  # Bootstrap icons
        menu_icon="cast",
        default_index=0,
    )
    
    # Submenu based on selection
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
    "Getting started": [
        "1_Retrieve_ETF_data",
        "2_yfinance_for_stocks",
        "3_Ptf_calculations"
    ],
    "Portfolio hacks": [
        "1_Advanced_ptf_charts",
        "2_TC_Momentum",
        "3_Score_to_Port",
        "4_Automagic_AA",
        "5_n_Sharpe_portfolio",
        "6_Alpha_Beta_revisited",
        "7_Attribution_revisited",
        "8_Ptf_Blind_Date"
    ],
    "Machine learning": [
        "1_Correlation_Matrix_revisited",
        "2_Autoencoder_for_Ptf_rebal"
    ],
    "AI for reporting": [
        "1_Autogen_HTML_reports",
        "2_Talk_to_your_portfolio"
    ],
    "VizTrader for Options": [
        "1_Adv_option_charts"
    ]
}

# Sidebar navigation
st.sidebar.title("Navigation")
section = st.sidebar.selectbox("Choose a section", list(pages.keys()))

if section:
    page = st.sidebar.selectbox("Choose a page", pages[section])
    if page:
        # Convert section and page to path
        module_path = f"app_sections.{section.replace(' ', '_')}.{page}"
        try:
            # Import and run the selected page
            module = importlib.import_module(module_path)
            if hasattr(module, 'main'):
                module.main()
            else:
                st.error(f"No main() function found in {module_path}")
        except Exception as e:
            st.error(f"Error loading page: {str(e)}")
else:
    landing_page()