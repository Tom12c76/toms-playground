import streamlit as st
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )

    st.write("# Welcome to Tom's Playgroud! 👋")

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


if __name__ == "__main__":
    run()
