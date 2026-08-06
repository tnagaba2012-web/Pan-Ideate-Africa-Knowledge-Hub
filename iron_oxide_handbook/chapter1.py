import streamlit as st
from iron_oxide_handbook.classification import classification
from iron_oxide_handbook.chemistry import chemistry
from iron_oxide_handbook.physical_properties import physical_properties
from iron_oxide_handbook.geology import geology
from iron_oxide_handbook.industry import industry

def introduction():
    st.markdown("""


# 1.1 What Are Iron Oxide Pigments?

(Chapter 1 content will be inserted here from the approved handbook.)
""")


def history():
    st.markdown("""
## 1.2 History and Evolution of Iron Oxide Pigments

(This section will be inserted here from the approved handbook.)
""")









def summary():
    st.markdown("""
## Chapter Summary
(This section will be inserted here.)
""")



def review_questions():
    st.markdown("""
## Review Questions

(This section will be inserted here.)
""")


def show_chapter1():
    st.title("📚 Chapter 1")

    introduction()
    history()
    classification()
    chemistry()
    physical_properties()
    geology()
    industry()
   
    summary()
    review_questions()
