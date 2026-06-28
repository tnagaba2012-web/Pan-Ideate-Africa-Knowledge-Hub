import streamlit as st

def show_page():
    st.title("🤖 Pan Ideate AI")

    st.markdown("""
# Your African Science, Innovation & Entrepreneurship Assistant

Welcome to **Pan Ideate AI**.

Pan Ideate AI is being developed by **Pan Ideate Africa Ltd.** to help students,
teachers, researchers, entrepreneurs and innovators learn, explore and build
practical solutions using science and technology.

---

## 🌍 What can Pan Ideate AI help you with?

🧪 Minerals & Chemistry

🌱 Agriculture & Biochar

💼 Business Development

🤖 Artificial Intelligence

💻 Programming & Python

📚 Scientific Learning

🚀 Innovation & Research

---

## 💬 Ask Pan Ideate AI questions like:

- How do I produce biochar?
- Explain bentonite chemistry.
- Teach me Python from the beginning.
- How can Ugandan youth start a mineral business?
- Show me practical school science demonstrations.

---

### 🚀 The future starts here.
""")
# ===============================
# PAN IDEATE AI CHAT
# ===============================

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
     # User input
prompt = st.chat_input("Ask Pan Ideate AI anything...")

if prompt:
    # Save user message
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Temporary AI response
    response = (
        "Hello! 👋 I am Pan Ideate AI.\n\n"
        "I am still being trained to become Africa's Science, "
        "Innovation and Entrepreneurship Assistant.\n\n"
        "Soon I will answer questions about minerals, chemistry, "
        "agriculture, business development and many other topics."
    )

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )

    with st.chat_message("assistant"):
        st.markdown(response)   
st.success("🟢 Pan Ideate AI is ready to chat!")

prompt = st.chat_input("Ask Pan Ideate AI anything...")

if prompt:

    with st.chat_message("user"):
        st.markdown(prompt)

    response = f"""
Hello! 👋

You asked:

**{prompt}**

I am currently in training.

Very soon I will answer questions about:

🔬 Minerals & Chemistry

🌱 Agriculture & Biochar

💼 Business Development

🤖 Artificial Intelligence

📚 Education

🌍 African Innovation

For now I'm using a temporary response while my intelligence is being connected.
"""

    with st.chat_message("assistant"):
        st.markdown(response)