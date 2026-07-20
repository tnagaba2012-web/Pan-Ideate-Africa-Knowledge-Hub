import streamlit as st


def show_handbook_header():

    st.title("📖 Uganda Minerals Master Handbook")

    st.success(
        "Welcome to the official learning handbook of Pan Ideate Africa."
    )

    st.info("""
This handbook has been designed to help students, teachers,
researchers, innovators and entrepreneurs understand Uganda's
minerals, chemistry and industrial opportunities.

Use the navigation below to explore each chapter.

Future versions will include:

• 📚 Reading Progress

• 🔍 Search Handbook

• 🌍 Language Selection

• 🤖 Ask Pan Ideate AI

• ⬅ Previous & Next Navigation

• ⭐ Bookmarks

• 📝 Interactive Quizzes
""")

    st.divider()