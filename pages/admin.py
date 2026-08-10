import streamlit as st
import os
from utils.database import get_connection

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

   

    
        # CONTACT INBOX
    st.header("📨 Contact Inbox")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, organisation, subject, message
        FROM messages
        ORDER BY id DESC
    """)

    messages = cursor.fetchall()

    connection.close()

    if messages:
        st.success(f"{len(messages)} contact message(s) received.")

        for msg in messages:
            st.markdown(f"### 📨 {msg['subject']}")
            st.write(f"**Name:** {msg['name']}")
            st.write(f"**Organisation:** {msg['organisation'] or 'Not provided'}")
            st.write(f"**Message:** {msg['message']}")
            st.divider()
    else:
        st.info("No contact messages have been received yet.")

        st.divider()

    # QUICK ADMIN SECTIONS
    st.header("⚙️ Administration")

    admin_option = st.selectbox(
        "Choose an administration area",
        [
            "Dashboard",
            "Contact Messages",
            "Partnership Requests",
            "Donation Requests",
            "Innovation Ideas",
            "Learning Centre",
            "Knowledge Hub",
        ]
    )

    st.write(f"Selected: **{admin_option}**")
    st.divider()

    # ==========================================================
    # DATABASE COUNTS
    # ==========================================================

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM messages")
    message_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM partnerships")
    partnership_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM donations")
    donation_count = cursor.fetchone()[0]

    connection.close()

    # ==========================================================
    # DASHBOARD
    # ==========================================================

    if admin_option == "Dashboard":

        st.subheader("📊 Administration Overview")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("📨 Messages", message_count)

        with col2:
            st.metric("🤝 Partnerships", partnership_count)

        with col3:
            st.metric("💝 Donations", donation_count)

    # ==========================================================
    # CONTACT MESSAGES
    # ==========================================================

    elif admin_option == "Contact Messages":

        st.subheader("📨 Contact Messages")

        connection = get_connection()

        rows = connection.execute("""
            SELECT
                id,
                name,
                organisation,
                subject,
                message,
                status,
                created_at
            FROM messages
            ORDER BY id DESC
        """).fetchall()

        connection.close()

        if rows:
            st.success(f"{len(rows)} message(s) found.")

            for row in rows:

                with st.expander(
                    f"📨 {row['subject'] or 'No subject'} — {row['name']}"
                ):

                    st.write(f"**Name:** {row['name']}")
                    st.write(
                        f"**Organisation:** "
                        f"{row['organisation'] or 'Not provided'}"
                    )
                    st.write(
                        f"**Subject:** "
                        f"{row['subject'] or 'No subject'}"
                    )
                    st.write(f"**Message:** {row['message']}")
                    st.write(f"**Status:** {row['status']}")
                    st.write(f"**Received:** {row['created_at']}")

        else:
            st.info("No contact messages have been received yet.")

    # ==========================================================
    # PARTNERSHIP REQUESTS
    # ==========================================================

    elif admin_option == "Partnership Requests":

        st.subheader("🤝 Partnership Requests")

        connection = get_connection()

        rows = connection.execute("""
            SELECT
                id,
                name,
                organisation,
                contact,
                partnership_type,
                idea,
                status,
                created_at
            FROM partnerships
            ORDER BY id DESC
        """).fetchall()

        connection.close()

        if rows:
            st.success(f"{len(rows)} partnership request(s) found.")

            for row in rows:

                with st.expander(
                    f"🤝 {row['partnership_type']} — {row['name']}"
                ):

                    st.write(f"**Name:** {row['name']}")
                    st.write(
                        f"**Organisation:** "
                        f"{row['organisation'] or 'Not provided'}"
                    )
                    st.write(f"**Contact:** {row['contact']}")
                    st.write(
                        f"**Partnership Type:** "
                        f"{row['partnership_type']}"
                    )
                    st.write(f"**Idea:** {row['idea']}")
                    st.write(f"**Status:** {row['status']}")
                    st.write(f"**Received:** {row['created_at']}")

        else:
            st.info("No partnership requests have been received yet.")

    # ==========================================================
    # DONATIONS
    # ==========================================================

    elif admin_option == "Donation Requests":

        st.subheader("💝 Donation Requests")

        connection = get_connection()

        rows = connection.execute("""
            SELECT
                id,
                name,
                organisation,
                contribution_type,
                amount,
                contact,
                message,
                status,
                created_at
            FROM donations
            ORDER BY id DESC
        """).fetchall()

        connection.close()

        if rows:
            st.success(f"{len(rows)} donation request(s) found.")

            for row in rows:

                with st.expander(
                    f"💝 {row['name']} — {row['contribution_type']}"
                ):

                    st.write(f"**Name:** {row['name']}")
                    st.write(
                        f"**Organisation:** "
                        f"{row['organisation'] or 'Not provided'}"
                    )
                    st.write(
                        f"**Contribution:** "
                        f"{row['contribution_type']}"
                    )
                    st.write(f"**Amount:** {row['amount']}")
                    st.write(f"**Contact:** {row['contact']}")
                    st.write(f"**Message:** {row['message']}")
                    st.write(f"**Status:** {row['status']}")
                    st.write(f"**Received:** {row['created_at']}")

        else:
            st.info("No donation requests have been received yet.")

    # ==========================================================
    # OTHER ADMIN AREAS
    # ==========================================================

    elif admin_option == "Innovation Ideas":

        st.subheader("💡 Innovation Ideas")
        st.info(
            "The Innovation Ideas database module has not been connected yet."
        )

    elif admin_option == "Learning Centre":

        st.subheader("🎓 Learning Centre")
        st.info(
            "Learning Centre administration will be connected in a later stage."
        )

    elif admin_option == "Knowledge Hub":

        st.subheader("📚 Knowledge Hub")
        st.info(
            "Knowledge Hub administration will be connected in a later stage."
        )

    st.divider()

    st.caption(
        "Pan Ideate Africa Ltd. — Administration Centre"
    )