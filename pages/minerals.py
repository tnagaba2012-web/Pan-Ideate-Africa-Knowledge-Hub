import streamlit as st

from chapters.chapter1 import show_chapter1


def show_page():

    st.title("🧪 Minerals & Chemistry - TEST")

    st.info("Explore Uganda's mineral resources and industrial chemistry.")

    st.divider()

    st.header("📚 Uganda Minerals Master Handbook")
    show_chapter1()
    

    st.markdown("""
- 🟤 Iron Oxide Pigments
- ⚪ Kaolin
- 🟢 Bentonite
- 💎 Silicon
- 🧂 Rock Salt
""")