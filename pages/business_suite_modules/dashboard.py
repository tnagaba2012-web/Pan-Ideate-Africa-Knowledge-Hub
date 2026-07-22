import streamlit as st


def show():

    st.header("📊 Business Dashboard")

    st.info(
        "Welcome to the Pan Ideate Africa Business Dashboard. "
        "This dashboard provides a quick overview of your learning, "
        "projects and business activities."
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("👥 Members", "1,245", "+42")

    with col2:
        st.metric("📚 Courses", "86", "+4")

    with col3:
        st.metric("💼 Projects", "18", "+2")

    with col4:
        st.metric("🌍 Countries", "12", "+1")

    st.markdown("---")

    st.subheader("⚡ Quick Actions")

    a, b, c = st.columns(3)

    with a:
        st.button("🛒 Marketplace")

    with b:
        st.button("📦 Inventory")

    with c:
        st.button("📊 Reports")

    st.markdown("---")

    st.success(
        "🚀 More dashboard features such as charts, notifications, "
        "business analytics and AI insights will be added in Version 2.2."
    )