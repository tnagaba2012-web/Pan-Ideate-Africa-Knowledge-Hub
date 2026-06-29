import streamlit as st
from knowledge.router import ask_ai


def show_page():

    st.title("🤖 Pan Ideate AI")

    st.success("🟢 Pan Ideate AI v2.0 is running successfully.")

    st.markdown("""
# 🌍 Welcome to Pan Ideate AI

Africa's Science, Innovation & Entrepreneurship Assistant.
""")

    st.markdown("---")

    st.header("🧠 Pan Ideate AI Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📚 Knowledge Topics", "150+")

    with col2:
        st.metric("🧪 Projects", "20+")

    with col3:
        st.metric("🌍 Focus", "Africa")

    st.markdown("---")

    st.subheader("📂 Explore Knowledge")

    left, right = st.columns(2)

    with left:

        if st.button("🪨 Minerals & Chemistry",
                     use_container_width=True,
                     key="minerals"):
            st.session_state.quick = "Tell me about minerals and chemistry."

        if st.button("🌱 Agriculture",
                     use_container_width=True,
                     key="agriculture"):
            st.session_state.quick = "Tell me about agriculture."

        if st.button("🏭 Manufacturing",
                     use_container_width=True,
                     key="manufacturing"):
            st.session_state.quick = "Manufacturing ideas."

    with right:

        if st.button("💼 Business",
                     use_container_width=True,
                     key="business"):
            st.session_state.quick = "Business ideas."

        if st.button("💻 Programming",
                     use_container_width=True,
                     key="programming"):
            st.session_state.quick = "Python programming."

        if st.button("🤖 Artificial Intelligence",
                     use_container_width=True,
                     key="ai"):
            st.session_state.quick = "Artificial Intelligence."

    st.markdown("---")

    st.subheader("🚀 Featured Projects")

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

    st.markdown("---")

    st.subheader("⚡ Quick Questions")

    q1, q2 = st.columns(2)

    with q1:

        if st.button("🌱 What is Biochar?",
                     key="biochar"):
            st.session_state.quick = "What is Biochar?"

        if st.button("🪨 What is Bentonite?",
                     key="bentonite"):
            st.session_state.quick = "What is Bentonite?"

        if st.button("⛏ Uganda Minerals",
                     key="uganda"):
            st.session_state.quick = "What minerals are found in Uganda?"

    with q2:

        if st.button("🧪 What is Kaolin?",
                     key="kaolin"):
            st.session_state.quick = "What is Kaolin?"

        if st.button("⚛ Silicon",
                     key="silicon"):
            st.session_state.quick = "Explain Silicon."

        if st.button("💼 Business Ideas",
                     key="ideas"):
            st.session_state.quick = "Business ideas."

    st.markdown("---")

    st.subheader("💬 Ask Pan Ideate AI")

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