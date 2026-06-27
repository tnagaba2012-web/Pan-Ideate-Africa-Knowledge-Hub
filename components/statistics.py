import streamlit as st


def show_statistics():

    st.header("📊 Knowledge Hub Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📚 Articles", "250+")

    with col2:
        st.metric("🧪 Projects", "40+")

    with col3:
        st.metric("👨‍🎓 Youth Target", "10,000+")

    with col4:
        st.metric("🌍 Countries", "54")

    st.divider()