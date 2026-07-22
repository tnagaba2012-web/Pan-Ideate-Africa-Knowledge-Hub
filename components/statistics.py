import streamlit as st


def show_statistics():

    st.header("📊 Knowledge Hub Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📚 Knowledge Articles", "250+")

        st.metric("🧪 Science Projects", "40+")

    with col2:
        st.metric("🌱 Agriculture Guides", "30+")

        st.metric("🤖 AI Learning Tools", "10+")

    with col3:
        st.metric("👨‍🎓 Youth Target", "10,000+")

        st.metric("🌍 African Countries", "54")

        st.divider()