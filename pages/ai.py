import streamlit as st


def show_page():
    # ===============================
    # PAGE TITLE
    # ===============================
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
""")

    # ===============================
    # KNOWLEDGE BASE
    # ===============================
    # ======================================
# PAN IDEATE AI DASHBOARD
# ======================================

st.header("🤖 Pan Ideate AI Dashboard")

col1, col2 = st.columns(2)

with col1:
    st.metric("🧠 AI Version", "1.0")
    st.metric("📚 Knowledge Topics", "20+")

with col2:
    st.metric("🟢 AI Status", "Learning")
    st.metric("🌍 Region", "Africa")

st.divider()
st.header("🧠 Pan Ideate AI Knowledge Base")
st.success(
        "Pan Ideate AI is continuously learning science, technology, entrepreneurship and innovation."
    )

knowledge = {

        "🪨 Minerals & Chemistry": [
            "Iron Oxide Pigments",
            "Bentonite",
            "Kaolin",
            "Silicon",
            "Rock Salt",
            "Biochar Chemistry"
        ],

        "🌱 Agriculture": [
            "Biochar Production",
            "Water Retention",
            "Soil Improvement",
            "Organic Fertilizers",
            "Livestock Feed Binders"
        ],

        "💼 Business Development": [
            "Business Planning",
            "Youth Entrepreneurship",
            "Value Addition",
            "Market Opportunities"
        ],

        "💻 Programming": [
            "Python",
            "Streamlit",
            "GitHub",
            "VS Code",
            "Artificial Intelligence"
        ],

        "🎓 Learning Centre": [
            "School Demonstrations",
            "Training Manuals",
            "Practical Chemistry",
            "Innovation Projects"
        ]

    }

for category, topics in knowledge.items():
        with st.expander(category):
            for topic in topics:
                st.write("✅", topic)
st.divider()

    # ===============================
    # CHAT
    # ===============================
st.header("🚀 Ask Pan Ideate AI")

if "messages" not in st.session_state:
        st.session_state.messages = []

for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

prompt = st.chat_input("Ask Pan Ideate AI anything...")

if prompt:

        st.session_state.messages.append(
            {"role": "user", "content": prompt}
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        response = f"""
Hello! 👋

You asked:

**{prompt}**

I am **Pan Ideate AI**.

At the moment I am running in demonstration mode.

Very soon I will answer questions using OpenAI together with the Pan Ideate Africa Knowledge Base.

My future knowledge includes:

🪨 Minerals & Chemistry

🌱 Agriculture & Biochar

💼 Business Development

💻 Python Programming

🤖 Artificial Intelligence

🎓 Scientific Learning

🚀 Innovation & Entrepreneurship

Thank you for helping build Africa's future!
"""

        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )

        with st.chat_message("assistant"):
            st.markdown(response)

st.success("🟢 Pan Ideate AI v2.0 is running successfully.")