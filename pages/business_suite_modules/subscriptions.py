import streamlit as st


def show():

    st.header("💳 Membership & Subscription Plans")

    free, student, professional, enterprise = st.columns(4)

    with free:
        st.success("🟢 FREE")
        st.write("""
✔ Basic Handbook

✔ Community Access

✔ Basic AI Assistant
""")

    with student:
        st.info("🔵 STUDENT")
        st.write("""
✔ Everything in FREE

✔ Full Courses

✔ Quizzes

✔ Certificates
""")

    with professional:
        st.warning("🟠 PROFESSIONAL")
        st.write("""
✔ Everything in STUDENT

✔ Business Suite

✔ Production Guides

✔ Premium Downloads
""")

    with enterprise:
        st.error("👑 ENTERPRISE")
        st.write("""
✔ Everything Included

✔ AI Business Tools

✔ Team Accounts

✔ Analytics

✔ Priority Support
""")

    st.markdown("---")

    st.info(
        "Future versions will include online payments, subscription "
        "management, invoices and member dashboards."
    )