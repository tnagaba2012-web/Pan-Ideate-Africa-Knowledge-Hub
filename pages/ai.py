import streamlit as st
from knowledge.router import ask_ai
from components.explorer import show_explorer

def show_page():
    st.success("✅ Pan Ideate AI v3.0 is running successfully!")
    show_explorer()
    st.error("THIS IS THE NEW AI.PY 123")
    st.markdown("""
Welcome to **Pan Ideate AI**

Africa's Science, Innovation and Entrepreneurship Assistant.
""")

    st.divider()

    st.header("📊 Pan Ideate AI Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📚 Knowledge Topics", "150+")

    with col2:
        st.metric("🧪 Projects", "20+")

    with col3:
        st.metric("🌍 Focus", "Africa")

    st.divider()

    st.header("🚀 Featured Projects")

    projects = [
        "Biochar Production",
        "Bentonite Technologies",
        "Kaolin Processing",
        "Silicon Extraction",
        "Iron Oxide Pigments",
        "Water Retention Products",
        "Rock Salt Processing",
        "Renewable Energy"
    ]

    for project in projects:
        st.write("✅", project)

    st.divider()

    st.header("⚡ Quick Questions")

    col1, col2 = st.columns(2)

    with col1:

        if st.button("🌱 What is Biochar?"):
            st.session_state.quick = "What is Biochar?"

        if st.button("🪨 What is Bentonite?"):
            st.session_state.quick = "Explain Bentonite."

        if st.button("🧪 What is Kaolin?"):
            st.session_state.quick = "Explain Kaolin."

        if st.button("⚙️ Silicon"):
            st.session_state.quick = "Explain Silicon."

    with col2:

        if st.button("🇺🇬 Uganda Minerals"):
            st.session_state.quick = "What minerals are found in Uganda?"

        if st.button("🎨 Iron Oxide Pigments"):
            st.session_state.quick = "Explain Iron Oxide Pigments."

        if st.button("💧 Water Retention"):
            st.session_state.quick = "Explain Water Retention Products."

        if st.button("💼 Business Ideas"):
            st.session_state.quick = "Give me business ideas."

    st.divider()
   
    st.header("💬 Ask Pan Ideate AI")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask Pan Ideate AI anything...")

    if "quick" in st.session_state:
        prompt = st.session_state.quick
        del st.session_state.quick

    if prompt:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        response = ask_ai(prompt)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )

        with st.chat_message("assistant"):
            st.markdown(response)