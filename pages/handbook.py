import streamlit as st
from chapters.chapter1 import show_chapter1

def show_page():
    st.title("📖 Uganda Minerals Handbook")

    st.markdown("""
Welcome to the **Uganda Minerals Master Handbook**.

This handbook has been developed by **Pan Ideate Africa Ltd.**
to provide practical, scientific and industry-oriented knowledge
about Uganda's mineral resources.

Use the section selector in the sidebar to navigate through each
chapter.
    """)

    st.divider()

    show_chapter1()