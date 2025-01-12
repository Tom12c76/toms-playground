import streamlit as st
import importlib

# Define the structure of the chapters and pages
chapters = {
    "Getting Started": [
        "0_Retrieving_ETF_Data",
        "1_yfinance_for_stocks",
        "2_Ptf_calculations"
    ],
    "Portfolio Hacks": [
        "1_Advanced_ptf_charts",
        "2_TC_Momentum",
        "3_Score_to_Port",
        "4_Automagic_AA",
        "5_n-Sharpe_portfolio",
        "6_Alpha_Beta_revisited",
        "7_Attribution_revisited",
        "8_Ptf_Blind_Date"
    ],
    "Machine Learning": [
        "1_Correlation_Matrix_revisited",
        "2_Autoencoder_for_Ptf_rebal"
    ],
    "AI for Reporting": [
        "1_Autogen_HTML_reports",
        "2_Talk_to_your_portfolio"
    ],
    "VizTrader for Options": [
        "1_Adv_option_charts"
    ]
}

# Mapping of chapter names to folder names
chapter_folders = {
    "Getting Started": "0_Getting_started",
    "Portfolio Hacks": "1_Portfolio_hacks",
    "Machine Learning": "2_Machine_learning",
    "AI for Reporting": "3_AI_for_reporting",
    "VizTrader for Options": "4_VizTrader_for_Options"
}

# Sidebar for navigation
st.sidebar.title("Navigation")
selected_chapter = st.sidebar.selectbox("Select Chapter", list(chapters.keys()))
selected_page = st.sidebar.selectbox("Select Page", chapters[selected_chapter])

# Dynamically import the selected page module
chapter_folder = chapter_folders[selected_chapter]
module_name = f"pages.{chapter_folder}.{selected_page}"
page = importlib.import_module(module_name)
page.main()
