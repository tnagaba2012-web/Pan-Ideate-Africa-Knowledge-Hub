import streamlit as st
from knowledge.router import ask_ai
def show_page():

    st.title("🤖 Pan Ideate AI")

    st.success("🟢 Pan Ideate AI v2.0 is running successfully.")

    st.markdown("""
# Your African Science, Innovation & Entrepreneurship Assistant

Welcome to Pan Ideate AI.

Ask questions about:

• Biochar

• Minerals

• Agriculture

• Business

• Programming

• Artificial Intelligence
""")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask Pan Ideate AI anything...")

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