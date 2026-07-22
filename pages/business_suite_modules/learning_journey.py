import streamlit as st


def show():

    st.header("🏆 Learning Journey")

    st.info(
        "Track your progress as you learn, innovate, build products "
        "and become a successful entrepreneur."
    )

    st.subheader("🌱 Your Journey")

    st.write("""
📖 Beginner

⬇

🧪 Science Learner

⬇

🔬 Practical Researcher

⬇

🏭 Product Developer

⬇

💼 Business Builder

⬇

🌍 African Innovator

⬇

👑 Pan Ideate Africa Ambassador
""")

    st.markdown("---")

    st.subheader("🏅 Achievements")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📚 Courses Completed", "12")

    with col2:
        st.metric("🏅 Badges Earned", "7")

    with col3:
        st.metric("🎓 Certificates", "3")

    st.markdown("---")

    st.success("""
Future versions will include:

✅ Personal learning dashboard

✅ Achievement badges

✅ Printable certificates

✅ Progress tracking

✅ Learning recommendations

✅ AI study coach
""")