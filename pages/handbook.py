import streamlit as st
from chapters.chapter1 import show_chapter1
from components.handbook_header import show_handbook_header
from components.handbook_navigation import show_handbook_navigation
def show_page():
   show_handbook_header()
   selected_section = show_handbook_navigation()
   st.divider()

show_chapter1()
