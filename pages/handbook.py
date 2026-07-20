import streamlit as st
from chapters.chapter1 import show_chapter1

def show_page():
    st.title("📖 Uganda Minerals Handbook")

    st.info("""
Welcome to the **Uganda Minerals Master Handbook**.

This handbook is the official learning resource of **Pan Ideate Africa Ltd.**

📖 Read chapter by chapter.

🧪 Learn practical mineral science.

🇺🇬 Explore Uganda's mineral resources.

🚀 Build innovation and industry through knowledge.

Use the Handbook Navigation below to explore each chapter.
""")

st.divider()

show_chapter1()