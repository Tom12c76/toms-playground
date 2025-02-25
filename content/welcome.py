import streamlit as st

def main():
    col1, col2 = st.columns([1, 3])

    with col1:
        st.write("")
        st.image("assets/profile.jpg", )

    with col2:
        st.subheader("Welcome to TC's playground")
        st.write("*Quick intro ofobjective and purpose here*")

    st.write("About me")
    st.write("My experiance and skills")
    st.write("Projects")
    st.write("Contact me")
    

if __name__ == "__main__":
    main()