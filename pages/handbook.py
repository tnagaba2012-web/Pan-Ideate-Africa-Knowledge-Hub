import streamlit as st
from chapters.chapter1 import show_chapter1
from components.handbook_header import show_handbook_header
from components.handbook_navigation import show_handbook_navigation
def show_page():
   show_handbook_header()
   chapter, section = show_handbook_navigation()
   st.divider()

   if chapter == "Chapter 1 - Introduction to Minerals":
        show_chapter1()

   elif chapter == "Chapter 2 - Matter, Atoms and Elements":
        from chapters.chapter2 import show_chapter2
        show_chapter2()