import streamlit as st

from chapters.chapter2_sections.section2_1 import show_section2_1
from chapters.chapter2_sections.section2_2 import show_section2_2
from chapters.chapter2_sections.section2_3 import show_section2_3
from chapters.chapter2_sections.section2_4 import show_section2_4
from chapters.chapter2_sections.section2_5 import show_section2_5
from chapters.chapter2_sections.section2_6 import show_section2_6
from chapters.chapter2_sections.section2_7 import show_section2_7
from chapters.chapter2_sections.section2_8 import show_section2_8
from chapters.chapter2_sections.section2_9 import show_section2_9
from chapters.chapter2_sections.section2_10 import show_section2_10


def show_chapter2():

    st.title("🧪 Chapter 2")

    st.subheader("Matter, Atoms and Elements")

    st.success("Master Version 1.0")

    st.markdown("---")

    section = st.selectbox(
        "🧪 Chapter 2 Navigation",
        [
            "2.1 What is Matter?",
            "2.2 States of Matter",
            "2.3 Atoms",
            "2.4 Elements",
            "2.5 The Periodic Table",
            "2.6 Molecules and Compounds",
            "2.7 Chemical Reactions",
            "2.8 Mixtures and Separation Techniques",
            "2.9 Matter in Minerals",
            "2.10 Chapter Summary"
        ]
    )

    st.markdown("---")

    if section == "2.1 What is Matter?":
        show_section2_1()

    elif section == "2.2 States of Matter":
        show_section2_2()

    elif section == "2.3 Atoms":
        show_section2_3()

    elif section == "2.4 Elements":
        show_section2_4()

    elif section == "2.5 The Periodic Table":
        show_section2_5()

    elif section == "2.6 Molecules and Compounds":
        show_section2_6()

    elif section == "2.7 Chemical Reactions":
        show_section2_7()

    elif section == "2.8 Mixtures and Separation Techniques":
        show_section2_8()

    elif section == "2.9 Matter in Minerals":
        show_section2_9()

    elif section == "2.10 Chapter Summary":
        show_section2_10()