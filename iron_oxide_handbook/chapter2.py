import streamlit as st
from iron_oxide_handbook.geology_intro import introduction
from iron_oxide_handbook.formation import formation

def show_chapter2():
    st.title("📘 Chapter 2")

    introduction()
    formation()

