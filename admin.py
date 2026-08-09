import streamlit as st
import os

def show_admin():
    st.title("🔐 Pan Ideate Africa Admin")

    st.info("Welcome to the Pan Ideate Africa Administration Centre.")

    st.divider()

    # ADMIN LOGIN
    st.subheader("🔑 Administrator Login")

    password = st.text_input(
        "Enter administrator password",
        type="password"
    )

    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_password:
        st.warning(
            "Administrator password has not been configured yet."
        )
        st.caption(
            "We will configure the secure password before launching the Admin Centre."
        )
        return

    if password != admin_password:
        st.error("Incorrect password.")
        return

    st.success("Login successful.")

    st.divider()

    # ADMIN DASHBOARD
    st.header("📊 Administration Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📨 Messages", "0")

    with col2:
        st.metric("🤝 Partnerships", "0")

    with col3:
        st.metric("💡 Innovation Ideas", "0")

    st.divider()

    # CONTACT INBOX
    st.header("📬 Contact Inbox")

    st.info(
        "Messages submitted through the Contact page will appear here."
    )

    st.divider()

    # QUICK ADMIN SECTIONS
    st.header("⚙️ Administration")

    admin_option = st.selectbox(
        "Choose an administration area",
        [
            "Dashboard",
            "Contact Messages",
            "Partnership Requests",
            "Innovation Ideas",
            "Learning Centre",
            "Knowledge Hub",
        ]
    )

    st.write(f"Selected: **{admin_option}**")

    st.divider()

    st.caption(
        "Pan Ideate Africa Ltd. — Administration Centre"
    )