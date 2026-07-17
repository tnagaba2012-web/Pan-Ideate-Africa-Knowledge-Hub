import streamlit as st

# Import Chapter 1 Sections
from chapters.chapter1_sections.section1_1 import show_section_1_1
from chapters.chapter1_sections.section1_2 import show_section_1_2
from chapters.chapter1_sections.section1_3 import show_section_1_3
def show_chapter1():
    
    st.title("📚 Chapter 1")
    st.subheader("Introduction to Minerals, Rocks and the Earth")

    st.success("Master Version 1.0")

    st.markdown("---")

    section = st.sidebar.selectbox(
        "Choose a Section",
        [
            "1.1 Why This Handbook Exists",
            "1.2 What Is the Earth?",
            "1.3 Minerals, Rocks and Ores",
            "1.4 The Rock Cycle",
            "1.5 Physical Properties of Minerals",
            "1.6 Mineral Classification",
            "1.7 How Minerals Form",
            "1.8 Minerals in Everyday Life",
            "1.9 Introduction to Mineral Exploration",
            "1.10 Chapter Summary"
        ]
    )
   
    st.markdown("---")

if section == "1.1 Why This Handbook Exists":
    show_section_1_1()

elif section == "1.2 What Is the Earth?":
    show_section_1_2()

elif section == "1.3 Minerals, Rocks and Ores":
    show_section_1_3()

else:
    st.info("🚧 This section will be activated as we build the chapter.")