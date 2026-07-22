import streamlit as st


def show():

    st.header("📊 Business Reports & Analytics")

    st.info(
        "Generate business insights and monitor the performance "
        "of your projects and products."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric("💰 Monthly Revenue", "UGX 12.5M", "+8%")
        st.metric("🛒 Products Sold", "324", "+15")

    with col2:
        st.metric("👥 Active Customers", "142", "+11")
        st.metric("📦 Orders Processed", "96", "+9")

    st.markdown("---")

    st.subheader("📈 Available Reports")

    st.write("""
• Daily Sales Report

• Weekly Sales Report

• Monthly Financial Summary

• Inventory Report

• Customer Activity Report

• Production Performance Report

• Agriculture Project Report
""")

    st.markdown("---")

    st.success("""
Future versions will include:

✅ Interactive charts

✅ PDF report generation

✅ Excel export

✅ Business forecasting

✅ Profit and loss analysis

✅ AI-powered business insights
""")