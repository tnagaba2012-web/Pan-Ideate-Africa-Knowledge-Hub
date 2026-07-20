import streamlit as st

from knowledge.router import ask_ai
from components.explorer import show_explorer


def show_page():

    # -------------------------------------------------
    # Header
    # -------------------------------------------------

    st.success("✅ Pan Ideate AI v4.0 is running successfully!")

    show_explorer()

    st.markdown("""
# 🤖 Pan Ideate AI

### Africa's Science, Minerals, Agriculture and Innovation Assistant

Welcome to **Pan Ideate AI**, the intelligent assistant of the
**Pan Ideate Africa Knowledge Hub**.

This assistant helps you explore:

- 🧪 Minerals & Chemistry
- 🌱 Agriculture & Biochar
- 🏺 Kaolin & Bentonite
- 💧 Water Retention Technologies
- 🏭 Manufacturing
- 💼 Business Development
- 📖 Uganda Minerals Handbook
- 🚀 Innovation & Entrepreneurship

Simply type your question below.

Examples:

• What is Quartz?

• Explain Bentonite.

• What is Biochar?

• Tell me about Kaolin.

• Explain mineral chemistry.

• What minerals are found in Uganda?
""")

    st.divider()

    # -------------------------------------------------
    # Dashboard
    # -------------------------------------------------

    st.header("📊 Pan Ideate AI Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📚 Knowledge Topics", "150+")

    with col2:
        st.metric("🧪 Projects", "20+")

    with col3:
        st.metric("🌍 Focus", "Africa")

    st.divider()

    # -------------------------------------------------
    # Featured Projects
    # -------------------------------------------------

    st.header("🚀 Featured Projects")

    projects = [

        "Biochar Production",

        "Bentonite Technologies",

        "Kaolin Processing",

        "Silicon Extraction",

        "Iron Oxide Pigments",

        "Water Retention Products",

        "Rock Salt Processing",

        "Renewable Energy",

        "Clay Innovation",

        "Agricultural Technologies"

    ]

    for project in projects:
        st.write("✅", project)

    st.divider()

    # -------------------------------------------------
    # Quick Questions
    # -------------------------------------------------

    st.subheader("⚡ Quick Questions")

    col1, col2 = st.columns(2)

    with col1:

        if st.button("🪨 What is Kaolin?"):
            st.session_state.quick = "What is Kaolin?"

        if st.button("🌱 What is Biochar?"):
            st.session_state.quick = "What is Biochar?"

        if st.button("⚪ What is Bentonite?"):
            st.session_state.quick = "Explain Bentonite."

    with col2:

        if st.button("💎 What is Quartz?"):
            st.session_state.quick = "What is Quartz?"

        if st.button("🧪 Mineral Chemistry"):
            st.session_state.quick = "Explain mineral chemistry."

        if st.button("🇺🇬 Uganda Minerals"):
            st.session_state.quick = "What minerals are found in Uganda?"

        if st.button("🎨 Iron Oxide Pigments"):
            st.session_state.quick = "Explain Iron Oxide Pigments."

        if st.button("💧 Water Retention"):
            st.session_state.quick = "Explain Water Retention Products."

        if st.button("💼 Business Ideas"):
            st.session_state.quick = "Give me business ideas."

    st.divider()
        # -------------------------------------------------
    # AI Chat
    # -------------------------------------------------

    st.header("💬 Ask Pan Ideate AI")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous conversation
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Use a Quick Question if one was selected
    prompt = None

    if "quick" in st.session_state:
        prompt = st.session_state.quick
        del st.session_state.quick
    else:
        prompt = st.chat_input("Ask Pan Ideate AI anything...")

    # Process the question
    if prompt:

        # Show user's message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        # Get answer from the Knowledge Router
        response = ask_ai(prompt)

        # Fallback if no answer is available
        if not response or response.strip() == "":
            response = """
Sorry, I don't know that yet.

I am still learning.

Current knowledge includes:

• Minerals
• Uganda Minerals
• Quartz
• Kaolin
• Bentonite
• Silica Sand
• Limestone
• Rock Salt
• Biochar

More chapters will be added soon.
"""

        # Save assistant reply
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )

        # Display assistant reply
        with st.chat_message("assistant"):
            st.markdown(response)

    # -------------------------------------------------
    # Footer
    # -------------------------------------------------

    st.divider()

    st.caption(
        "Pan Ideate AI v4.0 • Powered by the Pan Ideate Africa Knowledge Hub"
    )