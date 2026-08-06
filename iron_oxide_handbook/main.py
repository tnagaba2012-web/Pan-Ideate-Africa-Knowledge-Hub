import streamlit as st

from iron_oxide_handbook.chapter1 import show_chapter1
from iron_oxide_handbook.chapter2 import show_chapter2
from iron_oxide_handbook.chapter3 import show_chapter3
from iron_oxide_handbook.chapter4 import show_chapter4
from iron_oxide_handbook.chapter5 import show_chapter5
from iron_oxide_handbook.chapter6 import show_chapter6
from iron_oxide_handbook.chapter7 import show_chapter7
from iron_oxide_handbook.chapter8 import show_chapter8
from iron_oxide_handbook.chapter9 import show_chapter9
from iron_oxide_handbook.chapter10 import show_chapter10
from iron_oxide_handbook.chapter11 import show_chapter11
from iron_oxide_handbook.chapter12 import show_chapter12
from iron_oxide_handbook.cover import show_cover


def show_handbook():

    st.title("🟥 Iron Oxide Pigments Handbook")
    st.subheader("📚 Table of Contents")
    st.write("Select a chapter to begin reading:")
    chapter = st.selectbox(
        "Select Chapter",
        [
            
            "📕 Cover Page",
            "Chapter 1 - Introduction",
            "Chapter 2 - Geology & Mineralogy",
            "Chapter 3 - Chemistry",
            "Chapter 4 - Exploration",
            "Chapter 5 - Beneficiation",
            "Chapter 6 - Manufacturing",
            "Chapter 7 - Applications",
            "Chapter 8 - Quality Control",
            "Chapter 9 - Environment",
            "Chapter 10 - Health & Safety",
            "Chapter 11 - Business",
            "Chapter 12 - Uganda Resource Atlas",
        ],
    )
    if chapter == "📕 Cover Page":
        show_cover()

    elif chapter == "Chapter 1 - Introduction":
        show_chapter1()
    if chapter == "Chapter 1 - Introduction":
        show_chapter1()

    elif chapter == "Chapter 2 - Geology & Mineralogy":
        show_chapter2()

    elif chapter == "Chapter 3 - Chemistry":
        show_chapter3()

    elif chapter == "Chapter 4 - Exploration":
        show_chapter4()

    elif chapter == "Chapter 5 - Beneficiation":
        show_chapter5()

    elif chapter == "Chapter 6 - Manufacturing":
        show_chapter6()

    elif chapter == "Chapter 7 - Applications":
        show_chapter7()

    elif chapter == "Chapter 8 - Quality Control":
        show_chapter8()

    elif chapter == "Chapter 9 - Environment":
        show_chapter9()

    elif chapter == "Chapter 10 - Health & Safety":
        show_chapter10()

    elif chapter == "Chapter 11 - Business":
        show_chapter11()

    elif chapter == "Chapter 12 - Uganda Resource Atlas":
        show_chapter12()