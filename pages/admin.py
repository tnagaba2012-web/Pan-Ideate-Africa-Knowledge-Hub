import os
import streamlit as st

from pages.business_suite_modules import subscriptions

from utils.database import (
    get_connection,
    get_all_staff,
    get_staff_counts,
    add_staff,
    update_staff,
    update_staff_status,
    update_staff_role,
    reset_staff_password,
    delete_staff,
    get_staff_inbox,
    get_staff_sent_messages,
    get_unread_staff_count,
)


# ============================================================
# PAN IDEATE AFRICA
# ADMINISTRATION CENTRE
# ============================================================


def show_admin():

    st.title("🔐 Pan Ideate Africa Admin")

    st.info(
        "Welcome to the Pan Ideate Africa Administration Centre."
    )

    st.divider()

    # ========================================================
    # ADMIN LOGIN
    # ========================================================

    st.subheader("🔑 Administrator Login")

    password = st.text_input(
        "Enter administrator password",
        type="password",
        key="admin_password"
    )

    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_password:

        st.warning(
            "Administrator password has not been configured yet."
        )

        st.caption(
            "Configure ADMIN_PASSWORD before launching the "
            "Administration Centre."
        )

        return

    if password != admin_password:

        st.error("Incorrect password.")

        return

    st.success("Login successful.")

    st.divider()

    # ========================================================
    # CONTACT QUICK SUMMARY
    # ========================================================

    connection = get_connection()

    message_count = connection.execute(
        "SELECT COUNT(*) FROM messages"
    ).fetchone()[0]

    partnership_count = connection.execute(
        "SELECT COUNT(*) FROM partnerships"
    ).fetchone()[0]

    donation_count = connection.execute(
        "SELECT COUNT(*) FROM donations"
    ).fetchone()[0]

    connection.close()

    # ========================================================
    # ADMIN NAVIGATION
    # ========================================================

    st.header("⚙️ Administration")

    admin_option = st.selectbox(
        "Choose an administration area",
        [
            "Dashboard",
            "💳 Membership & Subscriptions",
            "📨 Contact Messages",
            "🤝 Partnership Requests",
            "❤️ Donation Requests",
            "👥 Staff Management",
            "💬 Staff Communications",
            "💡 Innovation Ideas",
            "🎓 Learning Centre",
            "📚 Knowledge Hub",
        ],
        key="admin_area"
    )

    st.divider()

    # ========================================================
    # DASHBOARD
    # ========================================================

    if admin_option == "Dashboard":

        st.subheader("📊 Administration Overview")

        staff_counts = get_staff_counts()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "📨 Messages",
                message_count
            )

        with col2:
            st.metric(
                "🤝 Partnerships",
                partnership_count
            )

        with col3:
            st.metric(
                "❤️ Donations",
                donation_count
            )

        with col4:
            st.metric(
                "👥 Active Staff",
                staff_counts["active"]
            )

        st.divider()

        st.subheader("🛡️ Staff Overview")

        staff_col1, staff_col2, staff_col3 = st.columns(3)

        with staff_col1:
            st.metric(
                "Total Staff",
                staff_counts["total"]
            )

        with staff_col2:
            st.metric(
                "Active",
                staff_counts["active"]
            )

        with staff_col3:
            st.metric(
                "Inactive",
                staff_counts["inactive"]
            )

        st.info(
            "The Administration Centre is now connected to "
            "the central staff database."
        )

    # ========================================================
    # MEMBERSHIP & SUBSCRIPTIONS
    # ========================================================

    elif admin_option == "💳 Membership & Subscriptions":

        st.subheader(
            "💳 Membership & Subscription Management"
        )

        subscriptions.ensure_subscription_table()

        connection = get_connection()

        total_members = connection.execute(
            "SELECT COUNT(*) FROM subscriptions"
        ).fetchone()[0]

        pending_members = connection.execute(
            """
            SELECT COUNT(*)
            FROM subscriptions
            WHERE status = 'Pending'
            """
        ).fetchone()[0]

        approved_members = connection.execute(
            """
            SELECT COUNT(*)
            FROM subscriptions
            WHERE status = 'Approved'
            """
        ).fetchone()[0]

        rejected_members = connection.execute(
            """
            SELECT COUNT(*)
            FROM subscriptions
            WHERE status = 'Rejected'
            """
        ).fetchone()[0]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "👥 Total Requests",
                total_members
            )

        with col2:
            st.metric(
                "🟡 Pending",
                pending_members
            )

        with col3:
            st.metric(
                "🟢 Approved",
                approved_members
            )

        with col4:
            st.metric(
                "🔴 Rejected",
                rejected_members
            )

        st.divider()

        status_filter = st.selectbox(
            "Filter membership requests",
            [
                "All",
                "Pending",
                "Approved",
                "Rejected"
            ],
            key="membership_status_filter"
        )

        if status_filter == "All":

            membership_rows = connection.execute(
                """
                SELECT *
                FROM subscriptions
                ORDER BY id DESC
                """
            ).fetchall()

        else:

            membership_rows = connection.execute(
                """
                SELECT *
                FROM subscriptions
                WHERE status = ?
                ORDER BY id DESC
                """,
                (status_filter,)
            ).fetchall()

        connection.close()

        st.markdown("### 👥 Membership Requests")

        if not membership_rows:

            st.info(
                "No membership requests found."
            )

        else:

            st.success(
                f"{len(membership_rows)} "
                "membership request(s) found."
            )

            for row in membership_rows:

                status = row["status"]

                if status == "Pending":
                    status_icon = "🟡"

                elif status == "Approved":
                    status_icon = "🟢"

                elif status == "Rejected":
                    status_icon = "🔴"

                else:
                    status_icon = "⚪"

                with st.expander(
                    f"{status_icon} #{row['id']} — "
                    f"{row['full_name']} — "
                    f"{row['plan']}"
                ):

                    st.write(
                        f"**Member:** {row['full_name']}"
                    )

                    st.write(
                        f"**Email:** {row['email']}"
                    )

                    if "phone" in row.keys():

                        st.write(
                            f"**Phone:** "
                            f"{row['phone'] or 'Not provided'}"
                        )

                    st.write(
                        f"**Plan:** {row['plan']}"
                    )

                    st.write(
                        f"**Status:** "
                        f"{status_icon} {row['status']}"
                    )

                    st.write(
                        f"**Payment Status:** "
                        f"{row['payment_status']}"
                    )

                    st.write(
                        f"**Submitted:** "
                        f"{row['created_at']}"
                    )

                    st.divider()

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        if st.button(
                            "✅ Approve",
                            key=f"approve_{row['id']}",
                            disabled=status == "Approved"
                        ):

                            connection = get_connection()

                            connection.execute(
                                """
                                UPDATE subscriptions
                                SET status = 'Approved',
                                    updated_at =
                                    CURRENT_TIMESTAMP
                                WHERE id = ?
                                """,
                                (row["id"],)
                            )

                            connection.commit()
                            connection.close()

                            st.success(
                                "Membership approved."
                            )

                            st.rerun()

                    with col2:

                        if st.button(
                            "❌ Reject",
                            key=f"reject_{row['id']}",
                            disabled=status == "Rejected"
                        ):

                            connection = get_connection()

                            connection.execute(
                                """
                                UPDATE subscriptions
                                SET status = 'Rejected',
                                    updated_at =
                                    CURRENT_TIMESTAMP
                                WHERE id = ?
                                """,
                                (row["id"],)
                            )

                            connection.commit()
                            connection.close()

                            st.warning(
                                "Membership rejected."
                            )

                            st.rerun()

                    with col3:

                        confirm = st.checkbox(
                            "Confirm delete",
                            key=f"confirm_sub_{row['id']}"
                        )

                        if st.button(
                            "🗑️ Delete",
                            key=f"delete_sub_{row['id']}",
                            disabled=not confirm
                        ):

                            connection = get_connection()

                            connection.execute(
                                """
                                DELETE FROM subscriptions
                                WHERE id = ?
                                """,
                                (row["id"],)
                            )

                            connection.commit()
                            connection.close()

                            st.success(
                                "Membership deleted."
                            )

                            st.rerun()

        st.divider()

        st.info(
            "🧪 TEST MODE: Membership approval is currently "
            "an administrative action. Real payment processing "
            "will be connected at a later stage."
        )

    # ========================================================
    # CONTACT MESSAGES
    # ========================================================

    elif admin_option == "📨 Contact Messages":

        st.subheader("📨 Contact Messages")

        connection = get_connection()

        new_rows = connection.execute(
            """
            SELECT *
            FROM messages
            WHERE status = 'New'
            ORDER BY id DESC
            """
        ).fetchall()

        old_rows = connection.execute(
            """
            SELECT *
            FROM messages
            WHERE status != 'New'
            ORDER BY id DESC
            """
        ).fetchall()

        connection.close()

        st.markdown("### 🔴 New Messages")

        if new_rows:

            st.success(
                f"{len(new_rows)} new message(s) "
                "waiting for attention."
            )

            for row in new_rows:

                with st.expander(
                    f"🔴 "
                    f"{row['subject'] or 'No subject'} — "
                    f"{row['name']}"
                ):

                    st.write(
                        f"**Name:** {row['name']}"
                    )

                    st.write(
                        f"**Organisation:** "
                        f"{row['organisation'] or 'Not provided'}"
                    )

                    st.write(
                        f"**Subject:** "
                        f"{row['subject'] or 'No subject'}"
                    )

                    st.write(
                        f"**Message:** {row['message']}"
                    )

                    st.write(
                        f"**Received:** {row['created_at']}"
                    )

                    if st.button(
                        "✅ Mark as Read",
                        key=f"read_contact_{row['id']}"
                    ):

                        connection = get_connection()

                        connection.execute(
                            """
                            UPDATE messages
                            SET status = 'Read'
                            WHERE id = ?
                            """,
                            (row["id"],)
                        )

                        connection.commit()
                        connection.close()

                        st.rerun()

        else:

            st.info(
                "✅ No new messages at this time."
            )

        st.divider()

        st.markdown("### 📖 Older / Read Messages")

        if old_rows:

            for row in old_rows:

                with st.expander(
                    f"📖 "
                    f"{row['subject'] or 'No subject'} — "
                    f"{row['name']}"
                ):

                    st.write(
                        f"**Name:** {row['name']}"
                    )

                    st.write(
                        f"**Organisation:** "
                        f"{row['organisation'] or 'Not provided'}"
                    )

                    st.write(
                        f"**Subject:** "
                        f"{row['subject'] or 'No subject'}"
                    )

                    st.write(
                        f"**Message:** {row['message']}"
                    )

                    st.write(
                        f"**Status:** {row['status']}"
                    )

                    st.write(
                        f"**Received:** {row['created_at']}"
                    )

        else:

            st.info(
                "There are no older/read messages yet."
            )

        st.divider()

        st.markdown("### 🗑️ Message Management")

        connection = get_connection()

        all_messages = connection.execute(
            """
            SELECT id, name, subject, status, created_at
            FROM messages
            ORDER BY id DESC
            """
        ).fetchall()

        connection.close()

        if all_messages:

            message_options = {
                f"#{row['id']} — "
                f"{row['subject'] or 'No subject'} — "
                f"{row['name']} "
                f"({row['status']})":
                row["id"]

                for row in all_messages
            }

            selected_message = st.selectbox(
                "Choose a message to delete",
                list(message_options.keys()),
                key="admin_delete_message"
            )

            selected_id = message_options[
                selected_message
            ]

            confirm_delete = st.checkbox(
                "I understand that this message "
                "will be permanently deleted.",
                key=f"confirm_delete_message_{selected_id}"
            )

            if st.button(
                "🗑️ Delete Selected Message",
                disabled=not confirm_delete,
                key=f"delete_contact_{selected_id}"
            ):

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
                    "Message deleted successfully."
                )

                st.rerun()

        else:

            st.info(
                "There are no messages available to delete."
            )

    # ========================================================
    # PARTNERSHIP REQUESTS
    # ========================================================

    elif admin_option == "🤝 Partnership Requests":

        st.subheader(
            "🤝 Partnership Requests"
        )

        connection = get_connection()

        new_rows = connection.execute(
            """
            SELECT *
            FROM partnerships
            WHERE status = 'New'
            ORDER BY id DESC
            """
        ).fetchall()

        reviewed_rows = connection.execute(
            """
            SELECT *
            FROM partnerships
            WHERE status != 'New'
            ORDER BY id DESC
            """
        ).fetchall()

        connection.close()

        st.markdown(
            "### 🔴 New Partnership Requests"
        )

        if new_rows:

            for row in new_rows:

                with st.expander(
                    f"🤝 "
                    f"{row['partnership_type'] or 'Partnership'} — "
                    f"{row['name']}"
                ):

                    st.write(
                        f"**Name:** {row['name']}"
                    )

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

                    st.write(
                        f"**Idea:** "
                        f"{row['idea'] or 'Not provided'}"
                    )

                    st.write(
                        f"**Received:** {row['created_at']}"
                    )

                    if st.button(
                        "✅ Mark as Reviewed",
                        key=f"review_partner_{row['id']}"
                    ):

                        connection = get_connection()

                        connection.execute(
                            """
                            UPDATE partnerships
                            SET status = 'Reviewed'
                            WHERE id = ?
                            """,
                            (row["id"],)
                        )

                        connection.commit()
                        connection.close()

                        st.rerun()

        else:

            st.info(
                "No new partnership requests."
            )

        st.divider()

        st.markdown(
            "### 📖 Older / Reviewed Requests"
        )

        if reviewed_rows:

            for row in reviewed_rows:

                with st.expander(
                    f"📖 "
                    f"{row['partnership_type'] or 'Partnership'} — "
                    f"{row['name']}"
                ):

                    st.write(
                        f"**Name:** {row['name']}"
                    )

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

                    st.write(
                        f"**Idea:** "
                        f"{row['idea'] or 'Not provided'}"
                    )

                    st.write(
                        f"**Status:** {row['status']}"
                    )

        else:

            st.info(
                "No reviewed partnership requests yet."
            )

    # ========================================================
    # DONATIONS
    # ========================================================

    elif admin_option == "❤️ Donation Requests":

        st.subheader(
            "❤️ Donation Requests"
        )

        connection = get_connection()

        new_rows = connection.execute(
            """
            SELECT *
            FROM donations
            WHERE status = 'New'
            ORDER BY id DESC
            """
        ).fetchall()

        reviewed_rows = connection.execute(
            """
            SELECT *
            FROM donations
            WHERE status != 'New'
            ORDER BY id DESC
            """
        ).fetchall()

        connection.close()

        st.markdown(
            "### 🔴 New Donation Requests"
        )

        if new_rows:

            for row in new_rows:

                with st.expander(
                    f"❤️ {row['name']} — "
                    f"{row['contribution_type']}"
                ):

                    st.write(
                        f"**Name:** {row['name']}"
                    )

                    st.write(
                        f"**Organisation:** "
                        f"{row['organisation'] or 'Not provided'}"
                    )

                    st.write(
                        f"**Contribution:** "
                        f"{row['contribution_type'] or 'Not specified'}"
                    )

                    st.write(
                        f"**Amount:** {row['amount']}"
                    )

                    st.write(
                        f"**Contact:** "
                        f"{row['contact'] or 'Not provided'}"
                    )

                    st.write(
                        f"**Message:** "
                        f"{row['message'] or 'No message provided'}"
                    )

                    st.write(
                        f"**Received:** {row['created_at']}"
                    )

                    if st.button(
                        "✅ Mark as Reviewed",
                        key=f"review_donation_{row['id']}"
                    ):

                        connection = get_connection()

                        connection.execute(
                            """
                            UPDATE donations
                            SET status = 'Reviewed'
                            WHERE id = ?
                            """,
                            (row["id"],)
                        )

                        connection.commit()
                        connection.close()

                        st.rerun()

        else:

            st.info(
                "No new donation requests."
            )

        st.divider()

        st.markdown(
            "### 📖 Older / Reviewed Donations"
        )

        if reviewed_rows:

            for row in reviewed_rows:

                with st.expander(
                    f"📖 {row['name']} — "
                    f"{row['contribution_type']}"
                ):

                    st.write(
                        f"**Name:** {row['name']}"
                    )

                    st.write(
                        f"**Organisation:** "
                        f"{row['organisation'] or 'Not provided'}"
                    )

                    st.write(
                        f"**Contribution:** "
                        f"{row['contribution_type'] or 'Not specified'}"
                    )

                    st.write(
                        f"**Amount:** {row['amount']}"
                    )

                    st.write(
                        f"**Contact:** "
                        f"{row['contact'] or 'Not provided'}"
                    )

                    st.write(
                        f"**Message:** "
                        f"{row['message'] or 'No message provided'}"
                    )

                    st.write(
                        f"**Status:** {row['status']}"
                    )

        else:

            st.info(
                "No reviewed donations yet."
            )

    # ========================================================
    # STAFF MANAGEMENT
    # ========================================================

    elif admin_option == "👥 Staff Management":

        st.subheader(
            "👥 Staff Management"
        )

        st.write(
            "Manage Pan Ideate Africa employee accounts, "
            "roles and access."
        )

        staff_counts = get_staff_counts()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "👥 Total Staff",
                staff_counts["total"]
            )

        with col2:
            st.metric(
                "🟢 Active",
                staff_counts["active"]
            )

        with col3:
            st.metric(
                "🔴 Inactive",
                staff_counts["inactive"]
            )

        with col4:
            st.metric(
                "🛡️ Administrators",
                staff_counts["admins"]
            )

        st.divider()

        tab1, tab2 = st.tabs(
            [
                "👥 Staff Directory",
                "➕ Add Staff Member"
            ]
        )

        # ----------------------------------------------------
        # DIRECTORY
        # ----------------------------------------------------

        with tab1:

            staff_list = get_all_staff()

            if not staff_list:

                st.info(
                    "No staff accounts found."
                )

            else:

                for employee in staff_list:

                    with st.container(border=True):

                        col1, col2, col3 = st.columns(
                            [3, 2, 2]
                        )

                        with col1:

                            st.markdown(
                                f"### 👤 "
                                f"{employee['full_name']}"
                            )

                            st.caption(
                                f"@{employee['username']}"
                            )

                            st.write(
                                f"Created: "
                                f"{employee['created_at']}"
                            )

                        with col2:

                            st.write(
                                f"**Role:** "
                                f"{employee['role']}"
                            )

                            if employee["status"] == "Active":

                                st.success(
                                    "🟢 Active"
                                )

                            else:

                                st.error(
                                    "🔴 Inactive"
                                )

                        with col3:

                            if employee["last_login"]:

                                st.write(
                                    f"Last login:"
                                )

                                st.caption(
                                    str(
                                        employee["last_login"]
                                    )
                                )

                            else:

                                st.caption(
                                    "Never logged in"
                                )

                        # ------------------------------------
                        # EDIT
                        # ------------------------------------

                        with st.expander(
                            "✏️ Manage this staff member"
                        ):

                            with st.form(
                                f"edit_staff_{employee['id']}"
                            ):

                                edit_name = st.text_input(
                                    "Full Name",
                                    value=employee["full_name"]
                                )

                                edit_username = st.text_input(
                                    "Username",
                                    value=employee["username"]
                                )

                                edit_role = st.selectbox(
                                    "Role",
                                    [
                                        "Staff",
                                        "Manager",
                                        "Finance",
                                        "Content Manager",
                                        "Agriculture Officer",
                                        "Minerals Officer",
                                        "Business Officer",
                                        "IT Officer",
                                        "Administrator",
                                        "Super Admin"
                                    ],
                                    index=[
                                        "Staff",
                                        "Manager",
                                        "Finance",
                                        "Content Manager",
                                        "Agriculture Officer",
                                        "Minerals Officer",
                                        "Business Officer",
                                        "IT Officer",
                                        "Administrator",
                                        "Super Admin"
                                    ].index(employee["role"])
                                    if employee["role"] in [
                                        "Staff",
                                        "Manager",
                                        "Finance",
                                        "Content Manager",
                                        "Agriculture Officer",
                                        "Minerals Officer",
                                        "Business Officer",
                                        "IT Officer",
                                        "Administrator",
                                        "Super Admin"
                                    ]
                                    else 0
                                )

                                edit_status = st.selectbox(
                                    "Account Status",
                                    [
                                        "Active",
                                        "Inactive"
                                    ],
                                    index=(
                                        0
                                        if employee["status"]
                                        == "Active"
                                        else 1
                                    )
                                )

                                save_changes = st.form_submit_button(
                                    "💾 Save Changes",
                                    use_container_width=True
                                )

                                if save_changes:

                                    try:

                                        update_staff(
                                            employee["id"],
                                            edit_name,
                                            edit_username,
                                            edit_role,
                                            edit_status
                                        )

                                        st.success(
                                            "Staff account updated."
                                        )

                                        st.rerun()

                                    except ValueError as error:

                                        st.error(
                                            str(error)
                                        )

                            st.divider()

                            # --------------------------------
                            # PASSWORD RESET
                            # --------------------------------

                            st.markdown(
                                "#### 🔑 Password Reset"
                            )

                            if employee["role"] != "Super Admin":

                                reset_password = st.text_input(
                                    "New temporary password",
                                    type="password",
                                    key=f"reset_password_{employee['id']}"
                                )

                                if st.button(
                                    "🔐 Reset Password",
                                    key=f"reset_button_{employee['id']}"
                                ):

                                    if len(reset_password) < 8:

                                        st.error(
                                            "Password must contain "
                                            "at least 8 characters."
                                        )

                                    else:

                                        try:

                                            reset_staff_password(
                                                employee["id"],
                                                reset_password
                                            )

                                            st.success(
                                                "Password reset successfully."
                                            )

                                        except ValueError as error:

                                            st.error(
                                                str(error)
                                            )

                            else:

                                st.info(
                                    "The Super Admin account is "
                                    "protected from deletion and "
                                    "ordinary password management."
                                )

                            st.divider()

                            # --------------------------------
                            # DELETE
                            # --------------------------------

                            if employee["role"] != "Super Admin":

                                confirm_delete_staff = st.checkbox(
                                    "Confirm permanent deletion",
                                    key=f"delete_staff_confirm_{employee['id']}"
                                )

                                if st.button(
                                    "🗑️ Delete Staff Account",
                                    key=f"delete_staff_{employee['id']}",
                                    disabled=not confirm_delete_staff
                                ):

                                    try:

                                        delete_staff(
                                            employee["id"]
                                        )

                                        st.success(
                                            "Staff account deleted."
                                        )

                                        st.rerun()

                                    except ValueError as error:

                                        st.error(
                                            str(error)
                                        )

        # ----------------------------------------------------
        # ADD STAFF
        # ----------------------------------------------------

        with tab2:

            st.markdown(
                "### ➕ Create New Employee Account"
            )

            st.info(
                "New employees created here will be able "
                "to use the Pan Ideate Africa Staff Login."
            )

            with st.form("admin_add_staff"):

                full_name = st.text_input(
                    "Full Name",
                    placeholder="e.g. Jane Namukasa"
                )

                username = st.text_input(
                    "Username",
                    placeholder="e.g. jane"
                )

                role = st.selectbox(
                    "Role",
                    [
                        "Staff",
                        "Manager",
                        "Finance",
                        "Content Manager",
                        "Agriculture Officer",
                        "Minerals Officer",
                        "Business Officer",
                        "IT Officer",
                        "Administrator"
                    ]
                )

                password = st.text_input(
                    "Initial Password",
                    type="password"
                )

                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password"
                )

                create_staff_account = st.form_submit_button(
                    "➕ Create Staff Account",
                    use_container_width=True,
                    type="primary"
                )

                if create_staff_account:

                    if not full_name.strip():

                        st.error(
                            "Please enter the employee's full name."
                        )

                    elif not username.strip():

                        st.error(
                            "Please enter a username."
                        )

                    elif len(password) < 8:

                        st.error(
                            "Password must contain at least 8 characters."
                        )

                    elif password != confirm_password:

                        st.error(
                            "Passwords do not match."
                        )

                    else:

                        try:

                            new_staff_id = add_staff(
                                full_name,
                                username,
                                password,
                                role,
                                "Active"
                            )

                            st.success(
                                f"✅ Staff account created successfully "
                                f"for {full_name}."
                            )

                            st.info(
                                f"Staff ID: {new_staff_id}"
                            )

                            st.rerun()

                        except ValueError as error:

                            st.error(
                                str(error)
                            )

    # ========================================================
    # STAFF COMMUNICATIONS
    # ========================================================

    elif admin_option == "💬 Staff Communications":

        st.subheader(
            "💬 Staff Communications"
        )

        staff_list = get_all_staff()

        if not staff_list:

            st.info(
                "No staff accounts are available."
            )

        else:

            st.markdown(
                "### 📊 Communication Overview"
            )

            total_unread = 0

            for employee in staff_list:

                total_unread += get_unread_staff_count(
                    employee["id"]
                )

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "👥 Staff Members",
                    len(staff_list)
                )

            with col2:

                st.metric(
                    "🔴 Unread Staff Messages",
                    total_unread
                )

            st.divider()

            st.markdown(
                "### 📥 Staff Inbox Review"
            )

            selected_employee = st.selectbox(
                "Select staff member",
                [
                    f"{employee['full_name']} "
                    f"(@{employee['username']})"
                    for employee in staff_list
                ],
                key="staff_message_employee"
            )

            employee_index = [
                f"{employee['full_name']} "
                f"(@{employee['username']})"
                for employee in staff_list
            ].index(selected_employee)

            selected_staff = staff_list[
                employee_index
            ]

            inbox = get_staff_inbox(
                selected_staff["id"]
            )

            if not inbox:

                st.info(
                    "This staff member's inbox is empty."
                )

            else:

                st.write(
                    f"{len(inbox)} message(s) in inbox."
                )

                for message in inbox:

                    read_icon = (
                        "⚪"
                        if message["is_read"]
                        else "🔴"
                    )

                    with st.expander(
                        f"{read_icon} "
                        f"{message['subject']} — "
                        f"{message['sender_name']}"
                    ):

                        st.write(
                            f"**From:** "
                            f"{message['sender_name']}"
                        )

                        st.write(
                            f"**Subject:** "
                            f"{message['subject']}"
                        )

                        st.write(
                            f"**Date:** "
                            f"{message['created_at']}"
                        )

                        st.divider()

                        st.write(
                            message["message"]
                        )

            st.divider()

            st.markdown(
                "### 📤 Sent Messages"
            )

            sent = get_staff_sent_messages(
                selected_staff["id"]
            )

            if not sent:

                st.info(
                    "This staff member has not sent messages."
                )

            else:

                for message in sent:

                    with st.expander(
                        f"📤 "
                        f"{message['subject']} → "
                        f"{message['recipient_name']}"
                    ):

                        st.write(
                            f"**To:** "
                            f"{message['recipient_name']}"
                        )

                        st.write(
                            f"**Date:** "
                            f"{message['created_at']}"
                        )

                        st.write(
                            f"**Read:** "
                            f"{'Yes' if message['is_read'] else 'No'}"
                        )

                        st.divider()

                        st.write(
                            message["message"]
                        )

    # ========================================================
    # OTHER ADMIN AREAS
    # ========================================================

    elif admin_option == "💡 Innovation Ideas":

        st.subheader(
            "💡 Innovation Ideas"
        )

        st.info(
            "The Innovation Ideas database module "
            "has not been connected yet."
        )

    elif admin_option == "🎓 Learning Centre":

        st.subheader(
            "🎓 Learning Centre"
        )

        st.info(
            "Learning Centre administration will be "
            "connected in a later stage."
        )

    elif admin_option == "📚 Knowledge Hub":

        st.subheader(
            "📚 Knowledge Hub"
        )

        st.info(
            "Knowledge Hub administration will be "
            "connected in a later stage."
        )

    st.divider()

    st.caption(
        "Pan Ideate Africa Administration Centre"
    )