import streamlit as st
import os
from pages.business_suite_modules import subscriptions
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
            "💳 Membership & Subscriptions",
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
            
        #SUBSCRIPTION AND MEMBERSHIP MANAGEMENT    
            
    elif admin_option == "💳 Membership & Subscriptions":
        subscriptions.show()        
            
            

    # ==========================================================
    # ============================================================
    # CONTACT MESSAGES
    # ============================================================

    elif admin_option == "Contact Messages":

        st.subheader("📨 Contact Messages")

        connection = get_connection()

        # --------------------------------------------------------
            # GET NEW MESSAGES
        # ==========================================

       

        new_rows = connection.execute("""
            SELECT
                id,
                name,
                organisation,
                subject,
                message,
                status,
                created_at
            FROM messages
            WHERE status = 'New'
            ORDER BY id DESC
        """).fetchall()

        # --------------------------------------------------------
        # GET READ / OLDER MESSAGES
        # --------------------------------------------------------

        old_rows = connection.execute("""
            SELECT
                id,
                name,
                organisation,
                subject,
                message,
                status,
                created_at
            FROM messages
            WHERE status != 'New'
            ORDER BY id DESC
        """).fetchall()

        connection.close()

        # ========================================================
        # NEW MESSAGES
        # ========================================================

        st.markdown("### 🔴 New Messages")

        if new_rows:

            st.success(
                f"{len(new_rows)} new message(s) waiting for attention."
            )

            for row in new_rows:

                with st.expander(
                    f"🔴 {row['subject'] or 'No subject'} — {row['name']}"
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

                    st.write(f"**Status:** 🔴 {row['status']}")

                    st.write(
                        f"**Received:** {row['created_at']}"
                    )

                    if st.button(
                        "✅ Mark as Read",
                        key=f"read_message_{row['id']}"
                    ):

                        connection = get_connection()

                        connection.execute(
                            """
                            UPDATE messages
                            SET status = 'Read'
                            WHERE id = ?
                            """,
                            (row['id'],)
                        )

                        connection.commit()
                        connection.close()

                        st.success("Message marked as read.")

                        st.rerun()

        else:

            st.info("✅ No new messages at this time.")

        # ========================================================
        # OLDER / READ MESSAGES
        # ========================================================

        st.divider()

        st.markdown("### 📖 Older / Read Messages")

        if old_rows:

            st.write(
                f"{len(old_rows)} older/read message(s) available."
            )

            for row in old_rows:

                with st.expander(
                    f"📖 {row['subject'] or 'No subject'} — {row['name']}"
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

                    st.write(f"**Status:** 📖 {row['status']}")

                    st.write(
                        f"**Received:** {row['created_at']}"
                    )

        else:

            st.info("There are no older/read messages yet.")
        # ========================================================
        # DELETE MESSAGES
        # ========================================================

        st.divider()

        st.markdown("### 🗑️ Message Management")

        connection = get_connection()

        all_messages = connection.execute("""
            SELECT
                id,
                name,
                subject,
                status,
                created_at
            FROM messages
            ORDER BY id DESC
        """).fetchall()

        connection.close()

        if all_messages:

            message_options = {
                f"#{row['id']} — {row['subject'] or 'No subject'} — "
                f"{row['name']} ({row['status']})": row["id"]
                for row in all_messages
            }

            selected_message = st.selectbox(
                "Choose a message to delete",
                list(message_options.keys()),
                key="delete_message_selector"
            )

            selected_id = message_options[selected_message]

            st.warning(
                "⚠️ Deleting a message is permanent. "
                "Please confirm before continuing."
            )

            confirm_delete = st.checkbox(
                "I understand that this message will be permanently deleted.",
                key=f"confirm_delete_{selected_id}"
            )

            if st.button(
                "🗑️ Delete Selected Message",
                key=f"delete_message_{selected_id}"
            ):

                if not confirm_delete:

                    st.error(
                        "Please confirm the deletion first."
                    )

                else:

                    connection = get_connection()

                    connection.execute(
                        """
                        DELETE FROM messages
                        WHERE id = ?
                        """,
                        (selected_id,)
                    )

                    connection.commit()
                    connection.close()

                    st.success(
                        "✅ Message deleted successfully."
                    )

                    st.rerun()

        else:

            st.info("There are no messages available to delete.")

    # ==========================================================
   # ============================================================
    # PARTNERSHIP REQUESTS
    # ============================================================

    elif admin_option == "Partnership Requests":

        st.subheader("🤝 Partnership Requests")

        connection = get_connection()

        # --------------------------------------------------------
        # NEW PARTNERSHIP REQUESTS
        # --------------------------------------------------------

        st.header("🔴 New Partnership Requests")

        new_rows = connection.execute("""
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
            WHERE status = 'New'
            ORDER BY id DESC
        """).fetchall()

        if new_rows:

            st.success(
                f"{len(new_rows)} new partnership request(s) found."
            )

            for row in new_rows:

                with st.expander(
                    f"🤝 {row['partnership_type'] or 'Partnership Request'} "
                    f"— {row['name']}"
                ):

                    st.write(f"**Name:** {row['name']}")

                    st.write(
                        f"**Organisation:** "
                        f"{row['organisation'] or 'Not provided'}"
                    )

                    st.write(
                        f"**Contact:** "
                        f"{row['contact'] or 'Not provided'}"
                    )

                    st.write(
                        f"**Partnership Type:** "
                        f"{row['partnership_type'] or 'Not specified'}"
                    )

                    st.write("**Partnership Idea:**")

                    st.write(
                        row['idea'] or "No partnership idea provided."
                    )

                    st.write(
                        f"**Received:** {row['created_at']}"
                    )

                    st.write(
                        f"**Status:** 🔴 {row['status']}"
                    )

                    if st.button(
                        "✅ Mark as Reviewed",
                        key=f"review_partnership_{row['id']}"
                    ):

                        update_connection = get_connection()

                        update_connection.execute(
                            """
                            UPDATE partnerships
                            SET status = 'Reviewed'
                            WHERE id = ?
                            """,
                            (row["id"],)
                        )

                        update_connection.commit()
                        update_connection.close()

                        st.success(
                            "Partnership request marked as reviewed."
                        )

                        st.rerun()

        else:

            st.info(
                "No new partnership requests at this time."
            )

        st.divider()

        # --------------------------------------------------------
        # OLDER / REVIEWED PARTNERSHIP REQUESTS
        # --------------------------------------------------------

        st.header("📖 Older / Reviewed Partnership Requests")

        reviewed_rows = connection.execute("""
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
            WHERE status != 'New'
            ORDER BY id DESC
        """).fetchall()

        if reviewed_rows:

            st.write(
                f"{len(reviewed_rows)} reviewed partnership request(s) available."
            )

            for row in reviewed_rows:

                with st.expander(
                    f"📖 {row['partnership_type'] or 'Partnership Request'} "
                    f"— {row['name']}"
                ):

                    st.write(f"**Name:** {row['name']}")

                    st.write(
                        f"**Organisation:** "
                        f"{row['organisation'] or 'Not provided'}"
                    )

                    st.write(
                        f"**Contact:** "
                        f"{row['contact'] or 'Not provided'}"
                    )

                    st.write(
                        f"**Partnership Type:** "
                        f"{row['partnership_type'] or 'Not specified'}"
                    )

                    st.write("**Partnership Idea:**")

                    st.write(
                        row['idea'] or "No partnership idea provided."
                    )

                    st.write(
                        f"**Received:** {row['created_at']}"
                    )

                    st.write(
                        f"**Status:** 🟢 {row['status']}"
                    )

        else:

            st.info(
                "There are no older/reviewed partnership requests yet."
            )

        connection.close()

        st.divider()

        # --------------------------------------------------------
        # PARTNERSHIP REQUEST MANAGEMENT
        # --------------------------------------------------------

        st.header("🗑️ Partnership Request Management")

        management_connection = get_connection()

        management_rows = management_connection.execute("""
            SELECT
                id,
                name,
                organisation,
                partnership_type,
                status,
                created_at
            FROM partnerships
            ORDER BY id DESC
        """).fetchall()

        management_connection.close()

        if management_rows:

            partnership_options = [
                f"{row['id']} — "
                f"{row['name']} — "
                f"{row['partnership_type'] or 'Partnership'} — "
                f"{row['status']}"
                for row in management_rows
            ]

            selected_partnership = st.selectbox(
                "Select a partnership request to manage:",
                partnership_options
            )

            selected_id = int(
                selected_partnership.split(" — ")[0]
            )

            st.warning(
                "⚠️ Deleting a partnership request is permanent."
            )

            confirm_delete = st.checkbox(
                "I understand that this request will be permanently deleted.",
                key="confirm_delete_partnership"
            )

            if st.button(
                "🗑️ Delete Selected Partnership Request",
                key="delete_partnership"
            ):

                if not confirm_delete:

                    st.error(
                        "Please confirm the deletion first."
                    )

                else:

                    delete_connection = get_connection()

                    delete_connection.execute(
                        """
                        DELETE FROM partnerships
                        WHERE id = ?
                        """,
                        (selected_id,)
                    )

                    delete_connection.commit()
                    delete_connection.close()

                    st.success(
                        "Partnership request deleted successfully."
                    )

                    st.rerun()

        else:

            st.info(
                "There are no partnership requests available to manage."
            )

    # ==========================================================
    # DONATIONS
    # ==========================================================
    elif admin_option == "Donation Requests":

        st.subheader("❤️ Donation Requests")

        connection = get_connection()

        # ==========================================================
        # NEW DONATION REQUESTS
        # ==========================================================

        st.header("🔴 New Donation Requests")

        new_rows = connection.execute("""
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
            WHERE status = 'New'
            ORDER BY id DESC
        """).fetchall()

        if new_rows:

            st.success(f"{len(new_rows)} new donation request(s) found.")

            for row in new_rows:

                with st.expander(
                    f"❤️ {row['name']} — {row['contribution_type']}"
                ):

                    st.write(f"**Name:** {row['name']}")

                    st.write(
                        f"**Organisation:** "
                        f"{row['organisation'] or 'Not provided'}"
                    )

                    st.write(
                        f"**Contribution:** "
                        f"{row['contribution_type'] or 'Not specified'}"
                    )

                    st.write(f"**Amount:** {row['amount']}")

                    st.write(
                        f"**Contact:** "
                        f"{row['contact'] or 'Not provided'}"
                    )

                    st.write(
                        f"**Message:** "
                        f"{row['message'] or 'No message provided'}"
                    )

                    st.write(f"**Received:** {row['created_at']}")

                    st.write("**Status:** 🔴 New")

                    if st.button(
                        "✅ Mark as Reviewed",
                        key=f"review_donation_{row['id']}"
                    ):

                        update_connection = get_connection()

                        update_connection.execute(
                            """
                            UPDATE donations
                            SET status = 'Reviewed'
                            WHERE id = ?
                            """,
                            (row["id"],)
                        )

                        update_connection.commit()
                        update_connection.close()

                        st.success("Donation request marked as reviewed.")
                        st.rerun()

        else:

            st.info("No new donation requests at this time.")

        # ==========================================================
        # OLDER / REVIEWED DONATIONS
        # ==========================================================

        st.divider()

        st.header("📖 Older / Reviewed Donations")

        reviewed_rows = connection.execute("""
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
            WHERE status != 'New'
            ORDER BY id DESC
        """).fetchall()

        if reviewed_rows:

            st.write(
                f"{len(reviewed_rows)} reviewed donation(s) available."
            )

            for row in reviewed_rows:

                with st.expander(
                    f"📖 {row['name']} — {row['contribution_type']}"
                ):

                    st.write(f"**Name:** {row['name']}")

                    st.write(
                        f"**Organisation:** "
                        f"{row['organisation'] or 'Not provided'}"
                    )

                    st.write(
                        f"**Contribution:** "
                        f"{row['contribution_type'] or 'Not specified'}"
                    )

                    st.write(f"**Amount:** {row['amount']}")

                    st.write(
                        f"**Contact:** "
                        f"{row['contact'] or 'Not provided'}"
                    )

                    st.write(
                        f"**Message:** "
                        f"{row['message'] or 'No message provided'}"
                    )

                    st.write(f"**Received:** {row['created_at']}")

                    st.write(f"**Status:** 🟢 {row['status']}")

        else:

            st.info("There are no older/reviewed donations yet.")

        # ==========================================================
        # DONATION MANAGEMENT
        # ==========================================================

        st.divider()

        st.header("🗑️ Donation Management")

        if new_rows or reviewed_rows:

            all_rows = new_rows + reviewed_rows

            donation_options = {
                f"{row['id']} — {row['name']} — "
                f"{row['contribution_type']} — {row['status']}":
                row["id"]
                for row in all_rows
            }

            selected_donation = st.selectbox(
                "Select a donation request to manage:",
                list(donation_options.keys()),
                key="selected_donation"
            )

            selected_id = donation_options[selected_donation]

            st.warning(
                "Deleting a donation request is permanent."
            )

            confirm_delete = st.checkbox(
                "I understand that this donation request "
                "will be permanently deleted.",
                key="confirm_delete_donation"
            )

            if st.button(
                "🗑️ Delete Selected Donation Request",
                disabled=not confirm_delete,
                key="delete_donation"
            ):

                delete_connection = get_connection()

                delete_connection.execute(
                    """
                    DELETE FROM donations
                    WHERE id = ?
                    """,
                    (selected_id,)
                )

                delete_connection.commit()
                delete_connection.close()

                st.success(
                    "Donation request permanently deleted."
                )

                st.rerun()

        else:

            st.info("There are no donations available to manage.")

        connection.close()
   

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
