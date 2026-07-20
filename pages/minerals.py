import streamlit as st
from knowledge.minerals import get_info
from chapters.chapter1 import show_chapter1


def show_page():

    st.title("🧪 Minerals & Chemistry - TEST")

    st.info("Explore Uganda's mineral resources and industrial chemistry.")

    st.divider()

    st.markdown(get_info())
    

  