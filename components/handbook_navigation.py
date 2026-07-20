import streamlit as st


def show_handbook_navigation():

    st.subheader("📚 Handbook Navigation")

    chapter = st.selectbox(
    "Choose a Chapter",
    [
        "Chapter 1 - Introduction to Minerals",
        "Chapter 2 - Matter, Atoms and Elements"
    ]
)

    section = None

    if chapter == "Chapter 1 - Introduction to Minerals":

        section = st.selectbox(
            "Choose a Section",
            [
                "1.1 Why This Handbook Exists",
                "1.2 What is the Earth?",
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
    elif chapter == "Chapter 2 - Matter, Atoms and Elements":

        section = st.selectbox(
        "Choose a Section",
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
    st.session_state["selected_section"] = section
    
    return chapter, section