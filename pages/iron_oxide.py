import streamlit as st
from knowledge.iron_oxide_handbook import get_info

def show_page():
    st.title("🟥 Iron Oxide Pigments Handbook")

    st.success("Pan Ideate Africa Knowledge Hub")

    st.markdown(get_info())