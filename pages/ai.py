import streamlit as st

from knowledge.router import ask_ai
from components.explorer import show_explorer


def show_page():

    # ==========================================================
    # Header
    # ==========================================================

    st.title("🤖 Pan Ideate AI")

    st.caption(
        "Africa's Science, Minerals, Agriculture and Innovation Assistant"
    )

    st.success("✅ Pan Ideate AI v5.0 is running successfully!")

    st.info(
        """
Welcome to **Pan Ideate AI**, your intelligent assistant for the
Pan Ideate Africa Knowledge Hub.

Explore minerals, chemistry, agriculture, business,
innovation and manufacturing through one intelligent assistant.
"""
    )

    # ==========================================================
    # Explorer
    # ==========================================================

    show_explorer()

    st.divider()

    # ==========================================================
    # Dashboard
    # ==========================================================

    st.subheader("📊 AI Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📚 Knowledge Topics", "150+")

    with col2:
        st.metric("🧪 Projects", "20+")

    with col3:
        st.metric("🌍 Focus", "Africa")

    st.divider()

    # ==========================================================
    # Featured Projects
    # ==========================================================

    st.subheader("🚀 Featured Projects")

    projects = [
        "Iron Oxide Pigments",
        "Biochar Production",
        "Kaolin Processing",
        "Bentonite Applications",
        "Silica & Quartz",
        "Water Retention Technologies",
        "Agriculture Innovation",
        "Uganda Minerals Handbook",
    ]

    for project in projects:
        st.write("✅", project)

    st.divider()

    # ==========================================================
    # Ask AI
    # ==========================================================

    st.subheader("💬 Ask Pan Ideate AI")

    question = st.chat_input("Ask anything...")

    if question:

        with st.chat_message("user"):
            st.markdown(question)

        response = ask_ai(question)

        with st.chat_message("assistant"):
            st.markdown(response)

    st.divider()

    st.caption("© 2026 Pan Ideate Africa Ltd")