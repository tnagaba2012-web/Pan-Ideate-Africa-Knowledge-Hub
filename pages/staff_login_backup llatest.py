import streamlit as st
import sqlite3
import hashlib
import secrets
from pathlib import Path
from datetime import datetime


# ============================================================
# PAN IDEATE AFRICA
# STAFF AUTHENTICATION & INTERNAL COMMUNICATION PORTAL
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "pan_ideate.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """Create a connection to the Pan Ideate Africa database."""

    DATA_DIR.mkdir(exist_ok=True)

    connection = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# PASSWORD SECURITY
# ============================================================

def hash_password(password):
    """
    Create a salted PBKDF2 password hash.
    """

    salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120000
    ).hex()

    return f"pbkdf2_sha256${salt}${password_hash}"


def verify_password(password, stored_hash):
    """
    Verify a password.

    Also supports the older SHA-256 format used by the
    previous Staff Login version.
    """

    if not stored_hash:
        return False

    # New secure format
    if stored_hash.startswith("pbkdf2_sha256$"):

        try:
            _, salt, password_hash = stored_hash.split("$", 2)

            calculated_hash = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt.encode("utf-8"),
                120000
            ).hex()

            return secrets.compare_digest(
                calculated_hash,
                password_hash
            )

        except Exception:
            return False

    # Compatibility with the previous SHA-256 system
    old_hash = hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()

    return secrets.compare_digest(
        old_hash,
        stored_hash
    )


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_database():

    connection = get_connection()
    cursor = connection.cursor()

    # --------------------------------------------------------
    # STAFF USERS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff_users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            full_name TEXT NOT NULL,

            username TEXT UNIQUE NOT NULL,

            password_hash TEXT NOT NULL,

            role TEXT NOT NULL DEFAULT 'Staff',

            status TEXT NOT NULL DEFAULT 'Active',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            last_login TIMESTAMP

        )
    """)

    # --------------------------------------------------------
    # INTERNAL STAFF MESSAGES
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff_messages (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            sender_id INTEGER NOT NULL,

            recipient_id INTEGER NOT NULL,

            subject TEXT NOT NULL,

            message TEXT NOT NULL,

            is_read INTEGER DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            read_at TIMESTAMP,

            FOREIGN KEY(sender_id)
                REFERENCES staff_users(id),

            FOREIGN KEY(recipient_id)
                REFERENCES staff_users(id)

        )
    """)

    connection.commit()
    connection.close()


# ============================================================
# INITIAL SUPER ADMIN
# ============================================================

def create_initial_admin():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM staff_users
        WHERE username = ?
        """,
        ("admin",)
    )

    admin = cursor.fetchone()

    if not admin:

        cursor.execute(
            """
            INSERT INTO staff_users
            (
                full_name,
                username,
                password_hash,
                role,
                status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                "Pan Ideate Africa Administrator",
                "admin",
                hash_password("PanIdeate@2026"),
                "Super Admin",
                "Active"
            )
        )

        connection.commit()

    connection.close()


# ============================================================
# STAFF AUTHENTICATION
# ============================================================

def authenticate(username, password):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM staff_users
        WHERE username = ?
        AND status = 'Active'
        """,
        (username.strip(),)
    )

    staff = cursor.fetchone()

    if staff:

        if verify_password(
            password,
            staff["password_hash"]
        ):

            cursor.execute(
                """
                UPDATE staff_users

                SET last_login = CURRENT_TIMESTAMP

                WHERE id = ?
                """,
                (staff["id"],)
            )

            connection.commit()
            connection.close()

            return staff

    connection.close()

    return None


# ============================================================
# SESSION MANAGEMENT
# ============================================================

def initialize_session():

    defaults = {

        "staff_logged_in": False,

        "staff_id": None,

        "staff_name": None,

        "staff_username": None,

        "staff_role": None,

        "staff_section": "Dashboard"

    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value


# ============================================================
# LOGIN
# ============================================================

def show_login():

    st.markdown(
        """
        <style>

        .staff-login-box {
            padding: 25px;
            border-radius: 18px;
            background: linear-gradient(
                135deg,
                #f7fbff,
                #eef6ff
            );
            border: 1px solid #d9e8f5;
            margin-bottom: 20px;
        }

        .staff-title {
            text-align: center;
            font-size: 36px;
            font-weight: 800;
            color: #086E8E;
        }

        .staff-subtitle {
            text-align: center;
            color: #666666;
            font-size: 17px;
            margin-bottom: 25px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="staff-title">'
        '🌍 Pan Ideate Africa'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="staff-subtitle">'
        'Staff Administration & Communication Portal'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    with st.container(border=True):

        st.subheader("🔐 Staff Login")

        st.write(
            "Sign in using your Pan Ideate Africa staff account."
        )

        username = st.text_input(
            "Username",
            placeholder="Enter your username"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        st.write("")

        login = st.button(
            "🔓 Sign In",
            use_container_width=True,
            type="primary"
        )

        if login:

            if not username or not password:

                st.error(
                    "Please enter both username and password."
                )

                return

            staff = authenticate(
                username,
                password
            )

            if staff:

                st.session_state.staff_logged_in = True

                st.session_state.staff_id = staff["id"]

                st.session_state.staff_name = staff["full_name"]

                st.session_state.staff_username = staff["username"]

                st.session_state.staff_role = staff["role"]

                st.session_state.staff_section = "Dashboard"

                st.success(
                    f"Welcome, {staff['full_name']}!"
                )

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )

    st.divider()

    st.caption(
        "Pan Ideate Africa — Authorized Staff Access"
    )


# ============================================================
# GET CURRENT STAFF
# ============================================================

def get_current_staff():

    staff_id = st.session_state.get("staff_id")

    if not staff_id:
        return None

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM staff_users
        WHERE id = ?
        """,
        (staff_id,)
    )

    staff = cursor.fetchone()

    connection.close()

    return staff


# ============================================================
# UNREAD MESSAGE COUNT
# ============================================================

def get_unread_count():

    staff_id = st.session_state.get("staff_id")

    if not staff_id:
        return 0

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM staff_messages
        WHERE recipient_id = ?
        AND is_read = 0
        """,
        (staff_id,)
    )

    count = cursor.fetchone()[0]

    connection.close()

    return count


# ============================================================
# STAFF DIRECTORY
# ============================================================

def get_active_staff():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            full_name,
            username,
            role,
            status
        FROM staff_users
        WHERE status = 'Active'
        ORDER BY full_name
        """
    )

    staff = cursor.fetchall()

    connection.close()

    return staff


# ============================================================
# DASHBOARD
# ============================================================

def show_dashboard():

    staff = get_current_staff()

    if not staff:
        return

    unread = get_unread_count()

    st.title("🛡️ Staff Dashboard")

    st.write(
        f"Welcome back, **{staff['full_name']}**."
    )

    st.caption(
        f"Role: {staff['role']} • "
        f"Username: {staff['username']}"
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Account Status",
            staff["status"]
        )

    with col2:

        st.metric(
            "Unread Messages",
            unread
        )

    with col3:

        active_staff = len(get_active_staff())

        st.metric(
            "Active Staff",
            active_staff
        )

    st.divider()

    st.subheader("🌍 Pan Ideate Africa Staff Portal")

    st.info(
        """
        This is the internal staff area of the
        Pan Ideate Africa Knowledge Hub.

        Use the navigation above to manage your profile,
        communicate with colleagues, and access staff
        administration functions according to your role.
        """
    )


# ============================================================
# MY PROFILE
# ============================================================

def show_profile():

    staff = get_current_staff()

    if not staff:
        return

    st.title("👤 My Profile")

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"**Full Name:** {staff['full_name']}"
        )

        st.write(
            f"**Username:** {staff['username']}"
        )

        st.write(
            f"**Role:** {staff['role']}"
        )

    with col2:

        st.write(
            f"**Status:** {staff['status']}"
        )

        st.write(
            f"**Account Created:** "
            f"{staff['created_at']}"
        )

        last_login = staff["last_login"]

        if last_login:

            st.write(
                f"**Last Login:** {last_login}"
            )

        else:

            st.write(
                "**Last Login:** First login"
            )

    st.divider()

    st.subheader("🔑 Change Password")

    with st.form("change_password_form"):

        current_password = st.text_input(
            "Current Password",
            type="password"
        )

        new_password = st.text_input(
            "New Password",
            type="password"
        )

        confirm_password = st.text_input(
            "Confirm New Password",
            type="password"
        )

        change_password = st.form_submit_button(
            "🔐 Change Password",
            use_container_width=True
        )

        if change_password:

            if not current_password:
                st.error("Enter your current password.")
                return

            if not new_password:
                st.error("Enter a new password.")
                return

            if len(new_password) < 8:

                st.error(
                    "New password must contain at least 8 characters."
                )

                return

            if new_password != confirm_password:

                st.error(
                    "The new passwords do not match."
                )

                return

            if not verify_password(
                current_password,
                staff["password_hash"]
            ):

                st.error(
                    "Current password is incorrect."
                )

                return

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE staff_users
                SET password_hash = ?
                WHERE id = ?
                """,
                (
                    hash_password(new_password),
                    staff["id"]
                )
            )

            connection.commit()
            connection.close()

            st.success(
                "Password changed successfully."
            )


# ============================================================
# COMPOSE MESSAGE
# ============================================================

def compose_message():

    st.title("✉️ Compose Message")

    staff_id = st.session_state.get("staff_id")

    employees = [
        employee
        for employee in get_active_staff()
        if employee["id"] != staff_id
    ]

    if not employees:

        st.warning(
            "There are currently no other active staff "
            "members to message."
        )

        return

    employee_options = {
        f"{employee['full_name']} "
        f"(@{employee['username']}) — {employee['role']}":
        employee["id"]

        for employee in employees
    }

    with st.form("compose_message_form"):

        recipient_label = st.selectbox(
            "To",
            list(employee_options.keys())
        )

        subject = st.text_input(
            "Subject",
            placeholder="Enter message subject"
        )

        message = st.text_area(
            "Message",
            placeholder="Write your message here...",
            height=220
        )

        send = st.form_submit_button(
            "📨 Send Message",
            use_container_width=True,
            type="primary"
        )

        if send:

            recipient_id = employee_options[
                recipient_label
            ]

            if not subject.strip():

                st.error(
                    "Please enter a subject."
                )

                return

            if not message.strip():

                st.error(
                    "Please enter a message."
                )

                return

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO staff_messages
                (
                    sender_id,
                    recipient_id,
                    subject,
                    message
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    staff_id,
                    recipient_id,
                    subject.strip(),
                    message.strip()
                )
            )

            connection.commit()
            connection.close()

            st.success(
                "✅ Message sent successfully."
            )

            st.rerun()


# ============================================================
# INBOX
# ============================================================

def show_inbox():

    staff_id = st.session_state.get("staff_id")

    st.title("📥 Inbox")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            messages.*,
            staff_users.full_name AS sender_name,
            staff_users.username AS sender_username,
            staff_users.role AS sender_role

        FROM staff_messages AS messages

        JOIN staff_users
        ON messages.sender_id = staff_users.id

        WHERE messages.recipient_id = ?

        ORDER BY messages.created_at DESC
        """,
        (staff_id,)
    )

    messages = cursor.fetchall()

    connection.close()

    if not messages:

        st.info(
            "Your inbox is currently empty."
        )

        return

    unread = sum(
        1 for message in messages
        if message["is_read"] == 0
    )

    if unread:

        st.info(
            f"📬 You have {unread} unread message(s)."
        )

    for message in messages:

        status_icon = (
            "🔵"
            if message["is_read"] == 0
            else "⚪"
        )

        with st.expander(
            f"{status_icon} "
            f"{message['subject']} — "
            f"{message['sender_name']} "
            f"({message['created_at']})"
        ):

            st.write(
                f"**From:** "
                f"{message['sender_name']} "
                f"(@{message['sender_username']})"
            )

            st.write(
                f"**Role:** {message['sender_role']}"
            )

            st.write(
                f"**Date:** {message['created_at']}"
            )

            st.divider()

            st.write(message["message"])

            if message["is_read"] == 0:

                connection = get_connection()
                cursor = connection.cursor()

                cursor.execute(
                    """
                    UPDATE staff_messages

                    SET
                        is_read = 1,
                        read_at = CURRENT_TIMESTAMP

                    WHERE id = ?
                    """,
                    (message["id"],)
                )

                connection.commit()
                connection.close()


# ============================================================
# SENT MESSAGES
# ============================================================

def show_sent():

    staff_id = st.session_state.get("staff_id")

    st.title("📤 Sent Messages")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            messages.*,
            staff_users.full_name AS recipient_name,
            staff_users.username AS recipient_username,
            staff_users.role AS recipient_role

        FROM staff_messages AS messages

        JOIN staff_users
        ON messages.recipient_id = staff_users.id

        WHERE messages.sender_id = ?

        ORDER BY messages.created_at DESC
        """,
        (staff_id,)
    )

    messages = cursor.fetchall()

    connection.close()

    if not messages:

        st.info(
            "You have not sent any messages yet."
        )

        return

    for message in messages:

        read_status = (
            "✓ Read"
            if message["is_read"]
            else "○ Unread"
        )

        with st.expander(
            f"📨 {message['subject']} — "
            f"{message['recipient_name']} "
            f"({message['created_at']})"
        ):

            st.write(
                f"**To:** "
                f"{message['recipient_name']} "
                f"(@{message['recipient_username']})"
            )

            st.write(
                f"**Status:** {read_status}"
            )

            st.write(
                f"**Date:** {message['created_at']}"
            )

            st.divider()

            st.write(message["message"])


# ============================================================
# STAFF DIRECTORY
# ============================================================

def show_staff_directory():

    st.title("👥 Staff Directory")

    staff = get_active_staff()

    if not staff:

        st.info(
            "No active staff members found."
        )

        return

    for employee in staff:

        with st.container(border=True):

            col1, col2, col3 = st.columns(
                [3, 2, 1]
            )

            with col1:

                st.write(
                    f"**{employee['full_name']}**"
                )

                st.caption(
                    f"@{employee['username']}"
                )

            with col2:

                st.write(
                    employee["role"]
                )

            with col3:

                st.write("🟢 Active")


# ============================================================
# SUPER ADMIN — STAFF MANAGEMENT
# ============================================================

def show_staff_management():

    if st.session_state.get("staff_role") != "Super Admin":

        st.error(
            "You do not have permission to access "
            "Staff Management."
        )

        return

    st.title("🛡️ Staff Management")

    tab1, tab2 = st.tabs(
        [
            "👥 Staff Accounts",
            "➕ Add Staff Member"
        ]
    )

    # --------------------------------------------------------
    # STAFF ACCOUNTS
    # --------------------------------------------------------

    with tab1:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM staff_users
            ORDER BY created_at DESC
            """
        )

        staff = cursor.fetchall()

        connection.close()

        if not staff:

            st.info(
                "No staff accounts found."
            )

        for employee in staff:

            with st.container(border=True):

                col1, col2, col3 = st.columns(
                    [3, 2, 2]
                )

                with col1:

                    st.write(
                        f"**{employee['full_name']}**"
                    )

                    st.caption(
                        f"@{employee['username']}"
                    )

                with col2:

                    st.write(
                        f"Role: {employee['role']}"
                    )

                    st.write(
                        f"Status: {employee['status']}"
                    )

                with col3:

                    if employee["username"] != "admin":

                        if employee["status"] == "Active":

                            if st.button(
                                "🔴 Deactivate",
                                key=f"deactivate_{employee['id']}"
                            ):

                                update_staff_status(
                                    employee["id"],
                                    "Inactive"
                                )

                                st.rerun()

                        else:

                            if st.button(
                                "🟢 Activate",
                                key=f"activate_{employee['id']}"
                            ):

                                update_staff_status(
                                    employee["id"],
                                    "Active"
                                )

                                st.rerun()

                        if st.button(
                            "🔑 Reset Password",
                            key=f"reset_{employee['id']}"
                        ):

                            reset_staff_password(
                                employee["id"]
                            )

                            st.success(
                                "Password reset to: "
                                "Welcome@2026"
                            )

    # --------------------------------------------------------
    # ADD STAFF
    # --------------------------------------------------------

    with tab2:

        with st.form("add_staff_form"):

            full_name = st.text_input(
                "Full Name"
            )

            username = st.text_input(
                "Username"
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

            create = st.form_submit_button(
                "➕ Create Staff Account",
                use_container_width=True,
                type="primary"
            )

            if create:

                if not full_name.strip():

                    st.error(
                        "Please enter the staff member's name."
                    )

                    return

                if not username.strip():

                    st.error(
                        "Please enter a username."
                    )

                    return

                if len(password) < 8:

                    st.error(
                        "Password must contain at least 8 characters."
                    )

                    return

                if password != confirm_password:

                    st.error(
                        "Passwords do not match."
                    )

                    return

                connection = get_connection()
                cursor = connection.cursor()

                try:

                    cursor.execute(
                        """
                        INSERT INTO staff_users
                        (
                            full_name,
                            username,
                            password_hash,
                            role,
                            status
                        )
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            full_name.strip(),
                            username.strip(),
                            hash_password(password),
                            role,
                            "Active"
                        )
                    )

                    connection.commit()

                    st.success(
                        f"Staff account for "
                        f"{full_name} created successfully."
                    )

                except sqlite3.IntegrityError:

                    st.error(
                        "That username already exists."
                    )

                finally:

                    connection.close()


# ============================================================
# STAFF MANAGEMENT HELPERS
# ============================================================

def update_staff_status(staff_id, status):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE staff_users

        SET status = ?

        WHERE id = ?
        """,
        (status, staff_id)
    )

    connection.commit()
    connection.close()


def reset_staff_password(staff_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE staff_users

        SET password_hash = ?

        WHERE id = ?
        """,
        (
            hash_password("Welcome@2026"),
            staff_id
        )
    )

    connection.commit()
    connection.close()


# ============================================================
# LOGOUT
# ============================================================

def logout():

    for key in [
        "staff_logged_in",
        "staff_id",
        "staff_name",
        "staff_username",
        "staff_role",
        "staff_section"
    ]:

        st.session_state.pop(
            key,
            None
        )

    st.rerun()


# ============================================================
# STAFF PORTAL
# ============================================================

def show_staff_portal():

    staff = get_current_staff()

    if not staff:
        logout()
        return

    unread = get_unread_count()
    active_staff = get_active_staff()

    # --------------------------------------------------------
    # STAFF PORTAL HEADER
    # --------------------------------------------------------
    st.markdown(
        """
        <style>
        .staff-portal-header {
            padding: 18px 22px;
            border-radius: 16px;
            background: linear-gradient(135deg, #eef7ff, #f8fbff);
            border: 1px solid #d8e9f5;
            margin-bottom: 18px;
        }

        .staff-portal-title {
            color: #086E8E;
            font-size: 30px;
            font-weight: 800;
            margin-bottom: 4px;
        }

        .staff-portal-subtitle {
            color: #5f6b76;
            font-size: 15px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="staff-portal-header">
            <div class="staff-portal-title">🛡️ Staff Portal</div>
            <div class="staff-portal-subtitle">
                Welcome, <strong>{staff['full_name']}</strong>
                &nbsp;•&nbsp; {staff['role']}
                &nbsp;•&nbsp; @{staff['username']}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # STAFF STATISTICS
    # --------------------------------------------------------
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM staff_users")
    total_staff = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM staff_users WHERE status = 'Active'"
    )
    active_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM staff_users WHERE status != 'Active'"
    )
    inactive_count = cursor.fetchone()[0]

    connection.close()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("👥 Total Employees", total_staff)

    with col2:
        st.metric("🟢 Active Employees", active_count)

    with col3:
        st.metric("⚪ Inactive Employees", inactive_count)

    with col4:
        st.metric("✉️ Unread Messages", unread)

    st.divider()

    # --------------------------------------------------------
    # MAIN STAFF NAVIGATION
    #
    # We intentionally use tabs instead of another sidebar
    # because app.py already owns the main Streamlit sidebar.
    # --------------------------------------------------------
    tabs = [
        "🏠 Dashboard",
        "👥 Staff Directory",
        "✉️ Messages",
        "👤 My Profile"
    ]

    if staff["role"] == "Super Admin":
        tabs.append("🛡️ Staff Management")

    selected_tab = st.tabs(tabs)

    # --------------------------------------------------------
    # DASHBOARD TAB
    # --------------------------------------------------------
    with selected_tab[0]:
        st.subheader("🌍 Pan Ideate Africa Staff Dashboard")

        st.info(
            """
            Welcome to the internal Pan Ideate Africa staff portal.

            From here you can communicate with colleagues, view the
            staff directory, manage your profile, and — if you are a
            Super Admin — manage staff accounts.
            """
        )

        st.subheader("⚡ Quick Actions")

        q1, q2, q3 = st.columns(3)

        with q1:
            st.markdown("### 👥")
            st.write("**Staff Directory**")
            st.caption(
                f"{active_count} active employee(s) available."
            )

        with q2:
            st.markdown("### ✉️")
            st.write("**Internal Messages**")
            if unread:
                st.warning(
                    f"You have {unread} unread message(s)."
                )
            else:
                st.caption("Your inbox is up to date.")

        with q3:
            st.markdown("### 🔐")
            st.write("**Your Account**")
            st.caption(
                f"Role: {staff['role']}"
            )

        st.divider()

        st.subheader("👥 Current Active Staff")

        if active_staff:
            for employee in active_staff:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([4, 2, 1])

                    with c1:
                        st.write(
                            f"**{employee['full_name']}**"
                        )
                        st.caption(
                            f"@{employee['username']} • "
                            f"{employee['role']}"
                        )

                    with c2:
                        st.write("🟢 Active")

                    with c3:
                        if employee["id"] == staff["id"]:
                            st.caption("You")
                        else:
                            st.caption("Available")
        else:
            st.info("No active staff members found.")

    # --------------------------------------------------------
    # STAFF DIRECTORY TAB
    # --------------------------------------------------------
    with selected_tab[1]:
        show_staff_directory()

    # --------------------------------------------------------
    # MESSAGES TAB
    # --------------------------------------------------------
    with selected_tab[2]:
        st.subheader("✉️ Internal Staff Messages")

        inbox_tab, compose_tab, sent_tab = st.tabs(
            [
                f"📥 Inbox ({unread})",
                "📝 Compose Message",
                "📤 Sent Messages"
            ]
        )

        with inbox_tab:
            show_inbox()

        with compose_tab:
            compose_message()

        with sent_tab:
            show_sent()

    # --------------------------------------------------------
    # PROFILE TAB
    # --------------------------------------------------------
    with selected_tab[3]:
        show_profile()

    # --------------------------------------------------------
    # SUPER ADMIN STAFF MANAGEMENT TAB
    # --------------------------------------------------------
    if staff["role"] == "Super Admin":
        with selected_tab[4]:
            show_staff_management()

    # --------------------------------------------------------
    # LOGOUT
    # --------------------------------------------------------
    st.divider()

    logout_col1, logout_col2, logout_col3 = st.columns([3, 2, 3])

    with logout_col2:
        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):
            logout()


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def show():

    # Prepare database
    init_database()

    # Create initial Super Admin if necessary
    create_initial_admin()

    # Prepare session
    initialize_session()

    # Show appropriate screen
    if st.session_state["staff_logged_in"]:

        show_staff_portal()

    else:

        show_login()