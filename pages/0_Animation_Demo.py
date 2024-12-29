import pandas as pd
import streamlit as st
from streamlit.hello.utils import show_code


def get_indu():

    #url_csindu = "https://www.blackrock.com/uk/intermediaries/products/253713/ishares-dow-jones-industrial-average-ucits-etf/1527484370694.ajax?fileType=xls&fileName=iShares-Dow-Jones-Industrial-Average-UCITS-ETF-USD-Acc_fund&dataType=fund"
    url_csindu = "https://www.blackrock.com/uk/intermediaries/products/253713/ishares-dow-jones-industrial-average-ucits-etf/1527484370694.ajax"
    df = pd.read_excel(url_csindu, skiprows=7, engine='openpyxl')

    st.write(df)

    return None

st.set_page_config(page_title="First things first", page_icon="📹")
st.markdown("# Animation Demo")
st.sidebar.header("Animation Demo")
st.write(
    """This app shows how you can use Streamlit to build cool animations.
It displays an animated fractal based on the the Julia Set. Use the slider
to tune different parameters."""
)

get_indu()

show_code(animation_demo)
