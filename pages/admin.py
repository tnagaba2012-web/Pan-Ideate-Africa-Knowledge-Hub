import os
import streamlit as st
import streamlit.components.v1 as components

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
from pages.admin_staff_messaging import show_admin_staff_messages
from pages.notification_centre import (
    show_notification_centre,
    get_notification_count,
)
from pages.task_manager import show_admin_task_manager
from pages.document_centre import show_admin_document_centre
from pages.leave_attendance import show_admin_leave_attendance
from pages.staff_directory import show_admin_staff_directory
from pages.staff_login import init_database as init_staff_database, create_initial_admin, authenticate
from pages.ai_staff_assistant import show_admin_ai_staff_assistant
from pages.meeting_centre import show_admin_meeting_centre
from pages.approval_centre import show_approval_centre
from pages.expenses_procurement import show_admin_expenses_procurement
from pages.admin_access_control import show_access_control, has_module_access, is_super_admin, init_access_control
from pages.audit_log import show_audit_log, log_audit_event

# ============================================================
# PAN IDEATE AFRICA
# ADMINISTRATION CENTRE
# ============================================================


def _dashboard_shortcut(target):
    """Set the administration destination from a dashboard shortcut.

    This runs as a Streamlit button callback, before the next script run,
    so it is safe to update the selectbox session-state value.
    """
    st.session_state["admin_area"] = target


def show_admin():

    init_access_control()

    st.title("🔐 Pan Ideate Africa Admin")

    st.info(
        "Welcome to the Pan Ideate Africa Administration Centre."
    )

    st.divider()

    # ========================================================
    # ADMIN LOGIN
    # ========================================================

    st.subheader("🔑 Administration Login")

    access_mode = st.radio(
        "Access mode",
        ["👑 Super Admin", "👤 Delegated Staff Operator"],
        horizontal=True,
        key="admin_access_mode",
    )

    current_operator_id = None
    current_is_super_admin = False

    if access_mode == "👑 Super Admin":
        password = st.text_input(
            "Enter administrator password",
            type="password",
            key="admin_password"
        )

        admin_password = os.getenv("ADMIN_PASSWORD")

        if not admin_password:
            st.warning("Administrator password has not been configured yet.")
            st.caption("Configure ADMIN_PASSWORD before launching the Administration Centre.")
            return

        if password != admin_password:
            st.info("Enter the Super Admin password to continue.")
            return

        connection = get_connection()
        row = connection.execute("""
            SELECT id FROM staff_users
            WHERE LOWER(username) = 'admin' AND status = 'Active'
            LIMIT 1
        """).fetchone()
        connection.close()
        current_operator_id = row["id"] if row else None
        current_is_super_admin = True
        st.success("Super Admin access granted — all Administration Centre functions are available.")

    else:
        operator_username = st.text_input("Staff Username", key="delegated_operator_username")
        operator_password = st.text_input("Staff Password", type="password", key="delegated_operator_password")
        if not operator_username or not operator_password:
            st.info("Enter the staff member's own login credentials.")
            return
        staff = authenticate(operator_username, operator_password)
        if not staff:
            st.error("Invalid staff username or password.")
            return
        current_operator_id = staff["id"]
        current_is_super_admin = is_super_admin(current_operator_id)
        if current_is_super_admin:
            st.success(f"Welcome, {staff['full_name']} — Super Admin access.")
        elif not any(has_module_access(current_operator_id, key) for key, _, _ in __import__('pages.admin_access_control', fromlist=['MODULES']).MODULES):
            st.warning("This staff member has not been assigned any Administration Centre functions yet.")
            return
        else:
            st.success(f"Delegated Administration access granted to {staff['full_name']}.")

    # Record successful administrator/delegated-operator login.
    try:
        log_audit_event(
            "Administration",
            "LOGIN",
            "Administration Centre access granted.",
            actor_name=("PAN IDEATE AFRICA ADMINISTRATOR" if current_is_super_admin else "Delegated Staff Operator"),
            actor_role=("Super Admin" if current_is_super_admin else "Delegated Operator"),
            severity="INFO",
        )
    except Exception:
        pass

    # Record one successful administrator login per active Streamlit session.
    if not st.session_state.get("admin_audit_login_recorded", False):
        try:
            log_audit_event(
                "Administration",
                "LOGIN",
                "Administrator signed in to the Administration Centre.",
                actor_name="PAN IDEATE AFRICA ADMINISTRATOR",
                actor_role="Administrator",
                severity="INFO",
            )
            st.session_state["admin_audit_login_recorded"] = True
        except Exception:
            # Audit logging must never prevent the existing Admin Centre from opening.
            pass

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

    all_admin_areas = [
        ("membership", "💳 Membership & Subscriptions"),
        ("contact_messages", "📨 Contact Messages"),
        ("partnerships", "🤝 Partnership Requests"),
        ("donations", "❤️ Donation Requests"),
        ("staff_management", "👥 Staff Management"),
        ("staff_directory", "👥 Staff Directory"),
        ("leave_attendance", "🕘 Leave & Attendance"),
        ("expenses_procurement", "💰 Expenses & Procurement"),
        ("tasks", "📋 Task & Project Manager"),
        ("staff_communications", "💬 Staff Communications"),
        ("staff_messages", "✉️ Staff Messages"),
        ("notifications", "🔔 Notification Centre"),
        ("ai_assistant", "🤖 AI Staff Assistant"),
        ("meetings", "📅 Meeting Centre"),
        ("approvals", "✅ Approval Centre"),
        ("audit_log", "🔐 Audit & Activity Log"),
        ("documents", "📁 Document Centre"),
        ("innovation", "💡 Innovation Ideas"),
        ("learning", "🎓 Learning Centre"),
        ("knowledge_hub", "📚 Knowledge Hub"),
    ]
    permitted_areas = [label for key, label in all_admin_areas if current_is_super_admin or has_module_access(current_operator_id, key)]
    admin_choices = ["Dashboard"] + permitted_areas
    if current_is_super_admin:
        admin_choices.append("🛡️ Staff Module Access Control")

    admin_option = st.selectbox(
        "Choose an administration area",
        admin_choices,
        key="admin_area"
    )

    st.divider()

    # ========================================================
    # ADVANCED ADMIN DASHBOARD
    # ========================================================

    if admin_option == "Dashboard":

        st.subheader("📊 Advanced Administration Dashboard")
        st.caption(
            "Pan Ideate Africa — organization-wide operations, workforce, "
            "approvals, tasks, meetings and payroll overview."
        )

        staff_counts = get_staff_counts()

        # ----------------------------------------------------
        # Safe dashboard helpers. These never assume that a newer
        # module/database table already exists.
        # ----------------------------------------------------
        def _table_exists(connection, table_name):
            row = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ? LIMIT 1",
                (table_name,)
            ).fetchone()
            return row is not None

        def _safe_count(connection, table_names, where=None, params=()):
            for table_name in table_names:
                if _table_exists(connection, table_name):
                    try:
                        sql = f"SELECT COUNT(*) FROM {table_name}"
                        if where:
                            sql += f" WHERE {where}"
                        return int(connection.execute(sql, params).fetchone()[0])
                    except Exception:
                        continue
            return 0

        def _safe_sum(connection, table_names, column_names):
            for table_name in table_names:
                if not _table_exists(connection, table_name):
                    continue
                for column_name in column_names:
                    try:
                        row = connection.execute(
                            f"SELECT COALESCE(SUM({column_name}), 0) FROM {table_name}"
                        ).fetchone()
                        return float(row[0] or 0)
                    except Exception:
                        continue
            return 0.0

        def _ensure_dashboard_settings(connection):
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS admin_dashboard_settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    next_salary_date TEXT,
                    salary_amount REAL DEFAULT 0,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO admin_dashboard_settings
                (id, next_salary_date, salary_amount)
                VALUES (1, NULL, 0)
                """
            )
            connection.commit()

        connection = get_connection()
        _ensure_dashboard_settings(connection)
        dashboard_settings = connection.execute(
            "SELECT next_salary_date, salary_amount FROM admin_dashboard_settings WHERE id = 1"
        ).fetchone()

        # Organization-wide operational counts. Existing tables are used
        # where available; missing future modules simply report zero.
        staff_unread = sum(
            get_unread_staff_count(employee["id"])
            for employee in get_all_staff()
        )
        notification_count = 0
        try:
            admin_row = connection.execute(
                """
                SELECT id
                FROM staff_users
                WHERE LOWER(username) = 'admin'
                  AND status = 'Active'
                LIMIT 1
                """
            ).fetchone()
            if admin_row:
                notification_count = int(get_notification_count(admin_row["id"]))
        except Exception:
            notification_count = 0

        pending_tasks = _safe_count(
            connection,
            ["tasks", "task_items", "project_tasks", "staff_tasks"],
            "status IN ('Pending', 'Open', 'Assigned', 'In Progress')"
        )
        overdue_tasks = _safe_count(
            connection,
            ["tasks", "task_items", "project_tasks", "staff_tasks"],
            "status NOT IN ('Completed', 'Closed', 'Cancelled') AND due_date < date('now')"
        )
        pending_approvals = _safe_count(
            connection,
            ["approval_requests", "approval_items", "approval_actions"],
            "status IN ('Pending', 'pending', 'Awaiting Approval')"
        )
        upcoming_meetings = _safe_count(
            connection,
            ["meetings", "meeting_records", "department_meetings"],
            "status NOT IN ('Cancelled', 'Completed')"
        )
        open_actions = _safe_count(
            connection,
            ["meeting_actions", "actions", "meeting_followups"],
            "status NOT IN ('Completed', 'Closed')"
        )
        on_leave = _safe_count(
            connection,
            ["leave_requests", "leave_records", "attendance_leave"],
            "status IN ('Approved', 'On Leave', 'approved', 'on leave')"
        )
        pending_expenses = _safe_count(
            connection,
            ["expense_claims", "expenses", "expense_requests"],
            "status IN ('Pending', 'Submitted', 'Awaiting Approval')"
        )
        pending_procurement = _safe_count(
            connection,
            ["procurement_requests", "procurement", "purchase_requests"],
            "status IN ('Pending', 'Submitted', 'Awaiting Approval')"
        )

        # ----------------------------------------------------
        # TOP SNAPSHOT
        # ----------------------------------------------------
        top = st.columns(4)
        with top[0]:
            st.metric("👥 Active Staff", staff_counts["active"])
        with top[1]:
            st.metric("📨 Unread Staff Messages", staff_unread)
        with top[2]:
            st.metric("🔔 Open Notifications", notification_count)
        with top[3]:
            st.metric("📝 Pending Approvals", pending_approvals)

        top2 = st.columns(4)
        with top2[0]:
            st.metric("📋 Open Tasks", pending_tasks)
        with top2[1]:
            st.metric("⏰ Overdue Tasks", overdue_tasks)
        with top2[2]:
            st.metric("📅 Upcoming Meetings", upcoming_meetings)
        with top2[3]:
            st.metric("🏖️ Staff on Leave", on_leave)

        # ----------------------------------------------------
        # MANAGEMENT ALERTS
        # ----------------------------------------------------
        st.divider()
        st.markdown("### 🚨 Management Attention")
        alerts = []
        if overdue_tasks:
            alerts.append(("🔴", f"{overdue_tasks} task(s) are overdue."))
        if pending_approvals:
            alerts.append(("🟠", f"{pending_approvals} approval request(s) need attention."))
        if pending_expenses:
            alerts.append(("🟠", f"{pending_expenses} expense request(s) are awaiting action."))
        if pending_procurement:
            alerts.append(("🟠", f"{pending_procurement} procurement request(s) are awaiting action."))
        if open_actions:
            alerts.append(("🟠", f"{open_actions} meeting action(s) remain open."))
        if not alerts:
            st.success("🟢 No major operational alerts detected right now.")
        else:
            for icon, message in alerts:
                st.warning(f"{icon} {message}")

        # ----------------------------------------------------
        # WORKFORCE STATUS
        # ----------------------------------------------------
        st.divider()
        st.markdown("### 🛡️ Workforce Status")
        workforce = st.columns(4)
        with workforce[0]:
            st.metric("Total Staff", staff_counts["total"])
        with workforce[1]:
            st.metric("🟢 Active", staff_counts["active"])
        with workforce[2]:
            st.metric("🔴 Inactive", staff_counts["inactive"])
        with workforce[3]:
            st.metric("🏖️ On Leave", on_leave)

        role_counts = {}
        for employee in get_all_staff():
            role = employee["role"] or "Unassigned"
            role_counts[role] = role_counts.get(role, 0) + 1

        if role_counts:
            st.markdown("#### 👤 Staff by Role")
            role_cols = st.columns(min(4, max(1, len(role_counts))))
            for index, (role, count) in enumerate(sorted(role_counts.items())):
                with role_cols[index % len(role_cols)]:
                    st.metric(role, count)

        # ----------------------------------------------------
        # OPERATIONS CENTRE
        # ----------------------------------------------------
        st.divider()
        st.markdown("### ⚙️ Operations Centre")
        operations = st.columns(4)
        with operations[0]:
            st.metric("📋 Tasks", pending_tasks)
        with operations[1]:
            st.metric("📅 Meetings", upcoming_meetings)
        with operations[2]:
            st.metric("💰 Pending Expenses", pending_expenses)
        with operations[3]:
            st.metric("🛒 Pending Procurement", pending_procurement)

        st.caption(
            "Use the Administration menu to open the detailed Tasks, Meeting, "
            "Approval, Leave & Attendance, and operational modules."
        )

        # ----------------------------------------------------
        # SALARY PAYMENT COUNTDOWN
        # ----------------------------------------------------
        st.divider()
        st.markdown("### 💰 Salary Payment Countdown")
        st.caption(
            "Set the next salary payment date here. The countdown is visible "
            "to authorized administrators only."
        )

        from datetime import date, datetime

        saved_salary_date = None
        if dashboard_settings and dashboard_settings["next_salary_date"]:
            try:
                saved_salary_date = date.fromisoformat(dashboard_settings["next_salary_date"])
            except (TypeError, ValueError):
                saved_salary_date = None

        salary_date = st.date_input(
            "Next salary payment date",
            value=saved_salary_date or date.today(),
            key="admin_salary_payment_date"
        )

        salary_amount = st.number_input(
            "Estimated total payroll (UGX, optional)",
            min_value=0.0,
            value=float(dashboard_settings["salary_amount"] or 0) if dashboard_settings else 0.0,
            step=100000.0,
            key="admin_salary_amount"
        )

        salary_col1, salary_col2 = st.columns(2)
        with salary_col1:
            if st.button("💾 Save Salary Settings", key="save_salary_settings", use_container_width=True):
                connection.execute(
                    """
                    UPDATE admin_dashboard_settings
                    SET next_salary_date = ?,
                        salary_amount = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = 1
                    """,
                    (salary_date.isoformat(), salary_amount)
                )
                connection.commit()
                st.success("Salary payment settings saved.")
                st.rerun()
        with salary_col2:
            st.metric("👥 Employees to Pay", staff_counts["active"])

        now = datetime.now()
        target = datetime.combine(salary_date, datetime.min.time())
        remaining_seconds = int((target - now).total_seconds())

        if remaining_seconds > 0:
            days_left = remaining_seconds // 86400
            hours_left = (remaining_seconds % 86400) // 3600
            minutes_left = (remaining_seconds % 3600) // 60
            seconds_left = remaining_seconds % 60
            countdown_text = (
                f"{days_left} DAYS {hours_left:02d} HOURS "
                f"{minutes_left:02d} MINUTES {seconds_left:02d} SECONDS"
            )
            st.success(f"💰 NEXT SALARY PAYMENT — {countdown_text}")

            # Live browser countdown. It does not require a new database
            # request every second and therefore does not disturb the app.
            target_iso = target.isoformat()
            components.html(
                f"""
                <div style="font-family:Arial,sans-serif;text-align:center;">
                  <div style="font-size:16px;font-weight:600;margin-bottom:6px;">
                    ⏳ Live Salary Countdown
                  </div>
                  <div id="salary-countdown" style="font-size:24px;font-weight:700;">
                    {countdown_text}
                  </div>
                </div>
                <script>
                const target = new Date({target_iso!r}).getTime();
                function updateSalaryCountdown() {{
                    const now = new Date().getTime();
                    let distance = target - now;
                    const box = document.getElementById('salary-countdown');
                    if (!box) return;
                    if (distance <= 0) {{
                        box.textContent = 'SALARY PAYMENT DATE IS TODAY';
                        return;
                    }}
                    const days = Math.floor(distance / 86400000);
                    distance %= 86400000;
                    const hours = Math.floor(distance / 3600000);
                    distance %= 3600000;
                    const minutes = Math.floor(distance / 60000);
                    const seconds = Math.floor((distance % 60000) / 1000);
                    box.textContent = `${{days}} DAYS ${{String(hours).padStart(2,'0')}} HOURS ${{String(minutes).padStart(2,'0')}} MINUTES ${{String(seconds).padStart(2,'0')}} SECONDS`;
                }}
                updateSalaryCountdown();
                setInterval(updateSalaryCountdown, 1000);
                </script>
                """,
                height=95,
            )
        elif remaining_seconds == 0:
            st.error("💰 SALARY PAYMENT DATE IS TODAY.")
        else:
            st.warning(
                "⚠️ The salary payment date has passed. Update it to the next payment date."
            )

        payroll_info = st.columns(3)
        with payroll_info[0]:
            st.metric("📅 Payment Date", salary_date.strftime("%d %B %Y"))
        with payroll_info[1]:
            st.metric("💵 Estimated Payroll", f"UGX {salary_amount:,.0f}")
        with payroll_info[2]:
            average_salary = salary_amount / staff_counts["active"] if staff_counts["active"] else 0
            st.metric("💵 Average / Active Employee", f"UGX {average_salary:,.0f}")

        # ----------------------------------------------------
        # DEPARTMENT / ROLE OVERVIEW
        # ----------------------------------------------------
        st.divider()
        st.markdown("### 🏢 Organization Overview")
        st.info(
            "Department-level analytics will automatically become available "
            "when department assignments are stored in the central staff records. "
            "For now, the dashboard shows the available role structure without "
            "inventing department data."
        )

        # ----------------------------------------------------
        # MANAGEMENT SHORTCUTS
        # ----------------------------------------------------
        st.divider()
        st.markdown("### 🔗 Management Shortcuts")
        shortcuts = st.columns(5)
        shortcut_labels = [
            "👥 Staff Directory",
            "🕘 Leave & Attendance",
            "📋 Tasks",
            "📅 Meetings",
            "✅ Approvals",
            "💰 Expenses",
            "🛒 Procurement",
            "📁 Documents",
            "🤖 AI Assistant",
            "🔔 Notifications",
            "🔐 Audit Log",
        ]
        shortcut_targets = [
            "👥 Staff Directory",
            "🕘 Leave & Attendance",
            "📋 Task & Project Manager",
            "📅 Meeting Centre",
            "✅ Approval Centre",
            "💰 Expenses & Procurement",
            "💰 Expenses & Procurement",
            "📁 Document Centre",
            "🤖 AI Staff Assistant",
            "🔔 Notification Centre",
            "🔐 Audit & Activity Log",
        ]

        for index, label in enumerate(shortcut_labels):
            with shortcuts[index % len(shortcuts)]:
                st.button(
                    label,
                    key=f"dashboard_shortcut_{index}",
                    use_container_width=True,
                    on_click=_dashboard_shortcut,
                    args=(shortcut_targets[index],),
                )

        connection.close()

        st.info(
            "The Advanced Admin Dashboard is connected to the central staff "
            "database and is designed to grow as each operational module is "
            "connected."
        )

    # ========================================================
    # STAFF MODULE ACCESS CONTROL
    # ========================================================

    elif admin_option == "🛡️ Staff Module Access Control":
        show_access_control(current_operator_id)

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
    # STAFF DIRECTORY
    # ========================================================

    elif admin_option == "👥 Staff Directory":

        try:
            init_staff_database()
            create_initial_admin()
            connection = get_connection()
            admin_row = connection.execute(
                """
                SELECT id, full_name, role, status
                FROM staff_users
                WHERE username = 'admin'
                  AND role = 'Super Admin'
                  AND status = 'Active'
                LIMIT 1
                """
            ).fetchone()
            connection.close()

            if admin_row:
                show_admin_staff_directory(admin_row["id"])
            else:
                st.error(
                    "The central Super Admin staff account could not be found."
                )
        except Exception as error:
            st.error(f"Unable to open Staff Directory: {error}")

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
                "➕ Add Staff Member",
            ]
        )

        # --------------------------------------------------------
        # STAFF DIRECTORY
        # --------------------------------------------------------
        with tab1:
            st.markdown("### 👥 Staff Accounts")

            staff_list = get_all_staff()

            if not staff_list:
                st.info("No staff accounts found.")
            else:
                for employee in staff_list:
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([3, 2, 2])

                        with col1:
                            st.markdown(f"### 👤 {employee['full_name']}")
                            st.caption(f"@{employee['username']}")
                            st.write(f"Created: {employee['created_at']}")

                        with col2:
                            st.write(f"**Role:** {employee['role']}")
                            if employee["status"] == "Active":
                                st.success("🟢 Active")
                            else:
                                st.error("🔴 Inactive")

                        with col3:
                            if employee["last_login"]:
                                st.write("Last login:")
                                st.caption(str(employee["last_login"]))
                            else:
                                st.caption("Never logged in")

                        with st.expander("✏️ Manage this staff member"):
                            with st.form(f"edit_staff_{employee['id']}"):
                                edit_name = st.text_input(
                                    "Full Name",
                                    value=employee["full_name"],
                                )
                                edit_username = st.text_input(
                                    "Username",
                                    value=employee["username"],
                                )

                                roles = [
                                    "Staff",
                                    "Manager",
                                    "Finance",
                                    "Content Manager",
                                    "Agriculture Officer",
                                    "Minerals Officer",
                                    "Business Officer",
                                    "IT Officer",
                                    "Administrator",
                                    "Super Admin",
                                ]

                                edit_role = st.selectbox(
                                    "Role",
                                    roles,
                                    index=(
                                        roles.index(employee["role"])
                                        if employee["role"] in roles
                                        else 0
                                    ),
                                )

                                edit_status = st.selectbox(
                                    "Account Status",
                                    ["Active", "Inactive"],
                                    index=(
                                        0
                                        if employee["status"] == "Active"
                                        else 1
                                    ),
                                )

                                save_changes = st.form_submit_button(
                                    "💾 Save Changes",
                                    use_container_width=True,
                                )

                                if save_changes:
                                    try:
                                        update_staff(
                                            employee["id"],
                                            edit_name,
                                            edit_username,
                                            edit_role,
                                            edit_status,
                                        )
                                        st.success("Staff account updated.")
                                        st.rerun()
                                    except ValueError as error:
                                        st.error(str(error))

                            st.divider()
                            st.markdown("#### 🔑 Password Reset")

                            if employee["role"] != "Super Admin":
                                reset_password = st.text_input(
                                    "New temporary password",
                                    type="password",
                                    key=f"reset_password_{employee['id']}",
                                )

                                if st.button(
                                    "🔐 Reset Password",
                                    key=f"reset_button_{employee['id']}",
                                ):
                                    if len(reset_password) < 8:
                                        st.error(
                                            "Password must contain at least 8 characters."
                                        )
                                    else:
                                        try:
                                            reset_staff_password(
                                                employee["id"],
                                                reset_password,
                                            )
                                            st.success(
                                                "Password reset successfully."
                                            )
                                        except ValueError as error:
                                            st.error(str(error))
                            else:
                                st.info(
                                    "The Super Admin account is protected "
                                    "from deletion and ordinary password management."
                                )

                            st.divider()

                            if employee["role"] != "Super Admin":
                                confirm_delete_staff = st.checkbox(
                                    "Confirm permanent deletion",
                                    key=f"delete_staff_confirm_{employee['id']}",
                                )

                                if st.button(
                                    "🗑️ Delete Staff Account",
                                    key=f"delete_staff_{employee['id']}",
                                    disabled=not confirm_delete_staff,
                                ):
                                    try:
                                        delete_staff(employee["id"])
                                        st.success("Staff account deleted.")
                                        st.rerun()
                                    except ValueError as error:
                                        st.error(str(error))

        # --------------------------------------------------------
        # ADD STAFF MEMBER
        # --------------------------------------------------------
        with tab2:
            st.markdown("### ➕ Create New Employee Account")
            st.info(
                "New employees created here will be able to use "
                "the Pan Ideate Africa Staff Login."
            )

            with st.form("admin_add_staff"):
                full_name = st.text_input(
                    "Full Name",
                    placeholder="e.g. Jane Namukasa",
                )
                username = st.text_input(
                    "Username",
                    placeholder="e.g. jane",
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
                        "Administrator",
                    ],
                )
                password = st.text_input(
                    "Initial Password",
                    type="password",
                )
                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password",
                )

                create_staff_account = st.form_submit_button(
                    "➕ Create Staff Account",
                    use_container_width=True,
                    type="primary",
                )

                if create_staff_account:
                    if not full_name.strip():
                        st.error("Please enter the employee's full name.")
                    elif not username.strip():
                        st.error("Please enter a username.")
                    elif len(password) < 8:
                        st.error(
                            "Password must contain at least 8 characters."
                        )
                    elif password != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        try:
                            new_staff_id = add_staff(
                                full_name,
                                username,
                                password,
                                role,
                                "Active",
                            )
                            st.success(
                                f"✅ Staff account created successfully for {full_name}."
                            )
                            st.info(f"Staff ID: {new_staff_id}")
                            st.rerun()
                        except ValueError as error:
                            st.error(str(error))

    # ========================================================
    # TASK & PROJECT MANAGER
    # ========================================================

    elif admin_option == "🕘 Leave & Attendance":

        try:
            init_staff_database()
            create_initial_admin()
            connection = get_connection()
            admin_row = connection.execute(
                """
                SELECT id, full_name, role, status
                FROM staff_users
                WHERE username = 'admin'
                  AND role = 'Super Admin'
                  AND status = 'Active'
                LIMIT 1
                """
            ).fetchone()
            connection.close()

            if admin_row:
                show_admin_leave_attendance(admin_row["id"])
            else:
                st.error(
                    "The central Super Admin staff account could not be found."
                )
        except Exception as error:
            st.error(f"Unable to open Leave & Attendance: {error}")

    elif admin_option == "💰 Expenses & Procurement":
        show_admin_expenses_procurement(current_operator_id)

    elif admin_option == "📋 Task & Project Manager":
        admin_staff_id = current_operator_id

        if admin_staff_id:
            show_admin_task_manager(admin_staff_id)
        else:
            st.error("The active Super Admin staff account could not be found.")

    # ========================================================
    # STAFF MESSAGES
    # ========================================================

    elif admin_option == "✉️ Staff Messages":
        show_admin_staff_messages()

    # ========================================================
    # NOTIFICATION CENTRE
    # ========================================================

    elif admin_option == "🔔 Notification Centre":
        admin_staff_id = current_operator_id

        if admin_staff_id:
            show_notification_centre(admin_staff_id)
        else:
            st.error(
                "The active Super Admin staff account could not be found."
            )

    # ========================================================
    # STAFF COMMUNICATIONS
    # ========================================================

    # ========================================================
    # DOCUMENT CENTRE
    # ========================================================

    # ========================================================
    # AI STAFF ASSISTANT
    # ========================================================

    elif admin_option == "🤖 AI Staff Assistant":
        admin_staff_id = current_operator_id

        if admin_staff_id:
            show_admin_ai_staff_assistant(admin_staff_id)
        else:
            st.error(
                "The active Super Admin staff account could not be found."
            )

    # ========================================================
    # MEETING CENTRE
    # ========================================================

    elif admin_option == "📅 Meeting Centre":
        admin_staff_id = current_operator_id

        if admin_staff_id:
            show_admin_meeting_centre(admin_staff_id)
        else:
            st.error(
                "The active Super Admin staff account could not be found."
            )

    # ========================================================
    # APPROVAL CENTRE
    # ========================================================

    elif admin_option == "✅ Approval Centre":
        admin_staff_id = current_operator_id

        if admin_staff_id:
            show_approval_centre(admin_staff_id)
        else:
            st.error(
                "The active Super Admin staff account could not be found."
            )

    elif admin_option == "📁 Document Centre":
        admin_staff_id = current_operator_id

        if admin_staff_id:
            show_admin_document_centre(admin_staff_id)
        else:
            st.error(
                "The active Super Admin staff account could not be found."
            )

    elif admin_option == "💬 Staff Communications":
        st.subheader("💬 Staff Communications")

        staff_list = get_all_staff()

        if not staff_list:
            st.info("No staff accounts are available.")
        else:
            st.markdown("### 📊 Communication Overview")

            total_unread = sum(
                get_unread_staff_count(employee["id"])
                for employee in staff_list
            )

            col1, col2 = st.columns(2)
            with col1:
                st.metric("👥 Staff Members", len(staff_list))
            with col2:
                st.metric("🔴 Unread Staff Messages", total_unread)

            st.divider()
            st.markdown("### 📥 Staff Inbox Review")

            employee_labels = [
                f"{employee['full_name']} (@{employee['username']})"
                for employee in staff_list
            ]

            selected_employee = st.selectbox(
                "Select staff member",
                employee_labels,
                key="staff_message_employee",
            )

            selected_staff = staff_list[employee_labels.index(selected_employee)]

            inbox = get_staff_inbox(selected_staff["id"])

            if not inbox:
                st.info("This staff member's inbox is empty.")
            else:
                st.write(f"{len(inbox)} message(s) in inbox.")

                for message in inbox:
                    read_icon = "⚪" if message["is_read"] else "🔴"
                    with st.expander(
                        f"{read_icon} {message['subject']} — "
                        f"{message['sender_name']}"
                    ):
                        st.write(f"**From:** {message['sender_name']}")
                        st.write(f"**Subject:** {message['subject']}")
                        st.write(f"**Date:** {message['created_at']}")
                        st.divider()
                        st.write(message["message"])

            st.divider()
            st.markdown("### 📤 Sent Messages")

            sent = get_staff_sent_messages(selected_staff["id"])

            if not sent:
                st.info("This staff member has not sent messages.")
            else:
                for message in sent:
                    read_status = (
                        "✓✓ Read"
                        if message["is_read"]
                        else "✓ Sent — Not yet read"
                    )

                    with st.expander(
                        f"📤 {message['subject']} → "
                        f"{message['recipient_name']}"
                    ):
                        st.write(f"**To:** {message['recipient_name']}")
                        st.write(f"**Date:** {message['created_at']}")
                        st.write(f"**Status:** {read_status}")

                        if message["is_read"]:
                            st.success(
                                "✓✓ The recipient has opened this message."
                            )
                        else:
                            st.info(
                                "✓ Sent. The recipient has not opened this "
                                "message yet."
                            )

                        st.divider()
                        st.write(message["message"])
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

    elif admin_option == "🔐 Audit & Activity Log":

        show_audit_log()

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
