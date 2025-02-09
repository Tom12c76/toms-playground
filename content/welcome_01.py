import streamlit as st

def show_landing():
    st.subheader("Welcome to my Playground")
    
    # Create two columns with ratio 1:2
    col1, col2 = st.columns([1, 2])
    
    # Left column - Image
    with col1:
        st.image("./assets/profile.jpg") 
    
    # Right column - Text
    with col2:
        st.write("""
        This is the landing page of the Portfolio Analysis App. 
        Use the sidebar to navigate to different sections.
        """)