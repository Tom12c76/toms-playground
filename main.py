import streamlit as st

st.set_page_config(
    page_title="Portfolio Analytics",
    layout="wide"
)

# Add sidebar title
st.sidebar.title("Navigation")

# Main content
st.title("Welcome to Portfolio Analytics")
st.markdown("""
### 👈 Select a page from the sidebar menu

#### Available Sections:
- 📚 Getting Started
  - Retrieving ETF Data
  - YFinance for Stocks
  - Portfolio Calculations
- 💼 Portfolio Hacks
  - Advanced Portfolio Charts
  - TC Momentum

Choose a section from the sidebar to begin exploring the portfolio analytics tools.
""")