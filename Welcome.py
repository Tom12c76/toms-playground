import streamlit as st
from streamlit.logger import get_logger

import plotly.express as px
import pandas as pd

LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="🎮",
    )

    st.write("# Welcome to my playgroud 🎮")

    st.sidebar.success("Select a demo above.")

    st.markdown(
        """
Welcome to my personal web app! I'm Thomas Castri, a senior portfolio manager
with over 25 years in finance, specializing in institutional asset management
and private banking. This platform highlights my expertise in Python programming,
machine learning, and AI, featuring projects that integrate Eikon market data,
Streamlit, and visualization tools like Plotly and Altair. 
              
Explore my work to see how I blend financial acumen with technological innovation.
        """
    )

    # Sample data
    data = {
        'Company': ['Zurich', 'UniCredit', 'Lehman Brothers', 'Generali Group', 'Family Office', 'DB Wealth Management'],
        'Start': ['2000-06-01', '2001-08-28', '2002-08-01', '2004-03-01', '2018-03-01', '2021-09-01'],
        'End': ['2001-08-28', '2002-08-01', '2004-03-01', '2018-03-01', '2021-09-01', '2024-12-31']
    }

    # Create DataFrame
    df = pd.DataFrame(data)

    # Convert dates to datetime format
    df['Start'] = pd.to_datetime(df['Start'])
    df['End'] = pd.to_datetime(df['End'])

    # Create timeline figure
    company_order = df['Company'][::-1].tolist()
    fig = px.timeline(df, x_start="Start", x_end="End", y="Company", title="Professional Experience Timeline", 
                     category_orders={"Company": company_order})

    # Display in Streamlit
    st.plotly_chart(fig)

if __name__ == "__main__":
    run()
