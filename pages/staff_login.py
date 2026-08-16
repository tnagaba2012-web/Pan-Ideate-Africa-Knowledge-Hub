import streamlit as st
from pages.notification_centre import (
    show_notification_centre,
    get_notification_count,
)
import sqlite3
import hashlib
import secrets
from pathlib import Path
from datetime import datetime
import uuid
import mimetypes
from pages.document_centre import show_document_centre
from pages.staff_directory import show_staff as show_staff_directory_v1
from pages.ai_staff_assistant import show_staff_ai_assistant
from pages.meeting_centre import show_staff_meeting_centre
from pages.approval_centre import show_staff_approval_centre
from utils.approval_engine import has_approval_access
from pages.admin_access_control import init_access_control, has_staff_tool_access, STAFF_MODULES


# ============================================================
# PAN IDEATE AFRICA
# STAFF AUTHENTICATION & INTERNAL COMMUNICATION PORTAL
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "pan_ideate.db"
ATTACHMENTS_DIR = DATA_DIR / "staff_attachments"
MAX_ATTACHMENT_SIZE = 25 * 1024 * 1024

# Staff Voice keeps confidential-report attachments in a separate directory.
STAFF_VOICE_ATTACHMENTS_DIR = DATA_DIR / "staff_voice_attachments"
MAX_STAFF_VOICE_ATTACHMENT_SIZE = 15 * 1024 * 1024
MAX_ATTACHMENTS_PER_MESSAGE = 5


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """Create a connection to the Pan Ideate Africa database."""

    DATA_DIR.mkdir(exist_ok=True)
    ATTACHMENTS_DIR.mkdir(exist_ok=True)
    STAFF_VOICE_ATTACHMENTS_DIR.mkdir(exist_ok=True)

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

    # --------------------------------------------------------
    # MESSAGE ATTACHMENTS
    # --------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff_message_attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            original_name TEXT NOT NULL,
            stored_name TEXT NOT NULL UNIQUE,
            mime_type TEXT,
            file_size INTEGER NOT NULL,
            uploaded_by INTEGER NOT NULL,
            file_data BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(message_id) REFERENCES staff_messages(id),
            FOREIGN KEY(uploaded_by) REFERENCES staff_users(id)
        )
    """)

    # --------------------------------------------------------
    # ATTACHMENT STORAGE MIGRATION
    # --------------------------------------------------------
    cursor.execute("PRAGMA table_info(staff_message_attachments)")
    attachment_columns = {row["name"] for row in cursor.fetchall()}

    if "file_data" not in attachment_columns:
        cursor.execute(
            "ALTER TABLE staff_message_attachments "
            "ADD COLUMN file_data BLOB"
        )

# --------------------------------------------------------
    # CONFIDENTIAL STAFF VOICE / CONCERNS
    # --------------------------------------------------------
    # Identity is stored for Super Admin accountability, but ordinary
    # staff and delegated operators never receive reporter identity.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff_voice_concerns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_number TEXT UNIQUE NOT NULL,
            reporter_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            urgency TEXT NOT NULL DEFAULT 'Normal',
            area TEXT,
            wants_response INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'Submitted',
            attachment_name TEXT,
            attachment_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(reporter_id) REFERENCES staff_users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff_voice_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concern_id INTEGER NOT NULL,
            responder_id INTEGER NOT NULL,
            response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(concern_id) REFERENCES staff_voice_concerns(id),
            FOREIGN KEY(responder_id) REFERENCES staff_users(id)
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_staff_voice_reporter
        ON staff_voice_concerns(reporter_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_staff_voice_status
        ON staff_voice_concerns(status)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_staff_voice_created
        ON staff_voice_concerns(created_at DESC)
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
# MESSAGE ATTACHMENT HELPERS
# ============================================================

def save_message_attachment(uploaded_file, message_id, uploaded_by):
    """Save an attachment in the database and keep a local fallback copy."""
    if uploaded_file is None:
        return None

    data = uploaded_file.getvalue()
    if len(data) > MAX_ATTACHMENT_SIZE:
        raise ValueError(f"{uploaded_file.name} is larger than 25 MB.")

    safe_suffix = Path(uploaded_file.name).suffix.lower()
    stored_name = f"{uuid.uuid4().hex}{safe_suffix}"
    (ATTACHMENTS_DIR / stored_name).write_bytes(data)

    mime_type = (
        uploaded_file.type
        or mimetypes.guess_type(uploaded_file.name)[0]
        or "application/octet-stream"
    )

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO staff_message_attachments
        (message_id, original_name, stored_name, mime_type, file_size, uploaded_by, file_data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (message_id, uploaded_file.name, stored_name, mime_type, len(data), uploaded_by, sqlite3.Binary(data))
    )
    connection.commit()
    connection.close()
    return stored_name


def get_message_attachments(message_id, staff_id):
    """Return attachments only for the sender or recipient of the message."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT a.id, a.original_name, a.stored_name, a.mime_type, a.file_size, a.file_data
        FROM staff_message_attachments AS a
        JOIN staff_messages AS m ON a.message_id = m.id
        WHERE a.message_id = ?
          AND (m.sender_id = ? OR m.recipient_id = ?)
        ORDER BY a.id
        """,
        (message_id, staff_id, staff_id)
    )
    rows = cursor.fetchall()
    connection.close()
    return rows


def format_file_size(size):
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


def show_attachments(message_id, staff_id):
    """Show authorized attachments, using database data first."""
    attachments = get_message_attachments(message_id, staff_id)
    if not attachments:
        return

    st.markdown("**📎 Attachments**")
    for attachment in attachments:
        data = attachment["file_data"]

        # Compatibility with attachments created by the previous version.
        if data is None:
            path = ATTACHMENTS_DIR / attachment["stored_name"]
            if path.exists():
                data = path.read_bytes()

        if data is None:
            st.warning(f"Attachment unavailable: {attachment['original_name']}")
            continue

        st.download_button(
            label=(f"📎 {attachment['original_name']} "
                   f"({format_file_size(attachment['file_size'])})"),
            data=bytes(data),
            file_name=attachment["original_name"],
            mime=attachment["mime_type"] or "application/octet-stream",
            key=f"download_attachment_{attachment['id']}_{staff_id}",
            use_container_width=True
        )


# ============================================================
# COMPOSE MESSAGE
# ============================================================

def compose_message():

    st.title("✉️ Compose Message")
    st.caption(
        "Send a private message to another active Pan Ideate Africa staff member. "
        "Attachments are visible only to the sender and recipient."
    )

    staff_id = st.session_state.get("staff_id")
    employees = [
        employee
        for employee in get_active_staff()
        if employee["id"] != staff_id
    ]

    if not employees:
        st.warning(
            "There are currently no other active staff members to message."
        )
        return

    employee_options = {
        f"{employee['full_name']} (@{employee['username']}) — {employee['role']}":
        employee["id"]
        for employee in employees
    }

    with st.form("compose_message_form", clear_on_submit=True):
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

        uploaded_files = st.file_uploader(
            "📎 Attach files (optional)",
            type=[
                "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
                "csv", "txt", "jpg", "jpeg", "png", "gif", "webp",
                "zip"
            ],
            accept_multiple_files=True,
            help="Maximum 5 files. Maximum 25 MB per file."
        )

        if uploaded_files:
            if len(uploaded_files) > MAX_ATTACHMENTS_PER_MESSAGE:
                st.warning(
                    f"You selected {len(uploaded_files)} files. "
                    f"Only the first {MAX_ATTACHMENTS_PER_MESSAGE} will be sent."
                )
            selected_files = uploaded_files[:MAX_ATTACHMENTS_PER_MESSAGE]
            st.caption(
                "Selected: " + ", ".join(
                    f"{f.name} ({format_file_size(f.size)})"
                    for f in selected_files
                )
            )
        else:
            selected_files = []

        send = st.form_submit_button(
            "📨 Send Message",
            use_container_width=True,
            type="primary"
        )

    if send:
        recipient_id = employee_options[recipient_label]

        if not subject.strip():
            st.error("Please enter a subject.")
            return

        if not message.strip():
            st.error("Please enter a message.")
            return

        oversized = [
            f.name for f in selected_files
            if f.size > MAX_ATTACHMENT_SIZE
        ]
        if oversized:
            st.error(
                "These files exceed the 25 MB limit: "
                + ", ".join(oversized)
            )
            return

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO staff_messages
            (sender_id, recipient_id, subject, message)
            VALUES (?, ?, ?, ?)
            """,
            (
                staff_id,
                recipient_id,
                subject.strip(),
                message.strip()
            )
        )
        message_id = cursor.lastrowid
        connection.commit()
        connection.close()

        try:
            for uploaded_file in selected_files:
                save_message_attachment(
                    uploaded_file,
                    message_id,
                    staff_id
                )
        except Exception as exc:
            st.error(
                f"The message was created, but an attachment could not be saved: {exc}"
            )
            return

        st.success(
            "✅ Message sent successfully"
            + (f" with {len(selected_files)} attachment(s)." if selected_files else ".")
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
            show_attachments(message["id"], staff_id)

            # ----------------------------------------------------
            # DIRECT REPLY
            # ----------------------------------------------------
            st.divider()

            with st.form(
                f"reply_form_{message['id']}_{staff_id}",
                clear_on_submit=True
            ):
                st.markdown("**↩️ Direct Reply**")

                reply_subject = st.text_input(
                    "Subject",
                    value=(
                        message["subject"]
                        if message["subject"].lower().startswith("re:")
                        else f"Re: {message['subject']}"
                    ),
                    key=f"reply_subject_{message['id']}_{staff_id}"
                )

                reply_text = st.text_area(
                    f"Reply to {message['sender_name']}",
                    placeholder="Write your reply here...",
                    height=150,
                    key=f"reply_text_{message['id']}_{staff_id}"
                )

                reply_files = st.file_uploader(
                    "📎 Attach files (optional)",
                    type=[
                        "pdf", "doc", "docx", "xls", "xlsx",
                        "ppt", "pptx", "csv", "txt",
                        "jpg", "jpeg", "png", "gif", "webp", "zip"
                    ],
                    accept_multiple_files=True,
                    key=f"reply_files_{message['id']}_{staff_id}",
                    help="Maximum 5 files. Maximum 25 MB per file."
                )

                reply_send = st.form_submit_button(
                    "↩️ Send Reply",
                    use_container_width=True,
                    type="primary"
                )

            if reply_send:
                selected_reply_files = (reply_files or [])[
                    :MAX_ATTACHMENTS_PER_MESSAGE
                ]

                oversized = [
                    f.name for f in selected_reply_files
                    if f.size > MAX_ATTACHMENT_SIZE
                ]

                if not reply_text.strip():
                    st.error("Please write a reply before sending.")
                elif oversized:
                    st.error(
                        "These files exceed the 25 MB limit: "
                        + ", ".join(oversized)
                    )
                else:
                    connection = get_connection()
                    cursor = connection.cursor()

                    cursor.execute(
                        """
                        INSERT INTO staff_messages
                        (sender_id, recipient_id, subject, message)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            staff_id,
                            message["sender_id"],
                            reply_subject.strip() or f"Re: {message['subject']}",
                            reply_text.strip()
                        )
                    )

                    reply_message_id = cursor.lastrowid
                    connection.commit()
                    connection.close()

                    try:
                        for uploaded_file in selected_reply_files:
                            save_message_attachment(
                                uploaded_file,
                                reply_message_id,
                                staff_id
                            )
                    except Exception as exc:
                        st.error(
                            f"Reply was created, but an attachment could not "
                            f"be saved: {exc}"
                        )
                        return

                    st.success(
                        "✅ Reply sent successfully"
                        + (
                            f" with {len(selected_reply_files)} attachment(s)."
                            if selected_reply_files else "."
                        )
                    )
                    st.rerun()

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
            show_attachments(message["id"], staff_id)


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
# CONFIDENTIAL STAFF VOICE / CONCERNS
# ============================================================

STAFF_VOICE_CATEGORIES = [
    "Workplace Problem",
    "Staff Welfare",
    "Management Concern",
    "Harassment / Bullying",
    "Safety Concern",
    "Financial Concern",
    "Suggestion / Improvement",
    "Other",
]

STAFF_VOICE_URGENCY = ["Low", "Normal", "High", "Critical"]
STAFF_VOICE_AREAS = [
    "Administration",
    "Finance & Procurement",
    "Agriculture",
    "Minerals & Chemistry",
    "Business Development",
    "Artificial Intelligence",
    "Learning Centre",
    "Innovation",
    "Other / Prefer not to say",
]
STAFF_VOICE_STATUSES = [
    "Submitted",
    "Received",
    "Under Review",
    "Action Required",
    "Resolved",
    "Closed",
]


def _staff_voice_audit(action, summary, staff_id=None, target_id=None, details=None, severity="INFO"):
    """Best-effort connection to the existing tamper-evident Audit & Activity Log."""
    try:
        from pages.audit_log import log_audit_event
        log_audit_event(
            "Staff Voice",
            action,
            summary,
            actor_id=staff_id,
            actor_name="Confidential Staff Voice User" if staff_id else "System",
            actor_role="Staff" if staff_id else "System",
            target_type="staff_voice_case" if target_id else None,
            target_id=str(target_id) if target_id else None,
            details=details,
            severity=severity,
        )
    except Exception:
        # Staff Voice must remain usable even if the optional audit module is absent.
        pass


def _next_staff_voice_case_number(connection):
    year = datetime.now().year
    row = connection.execute(
        "SELECT COUNT(*) FROM staff_voice_concerns WHERE case_number LIKE ?",
        (f"PIA-CON-{year}-%",),
    ).fetchone()
    sequence = int(row[0] or 0) + 1
    return f"PIA-CON-{year}-{sequence:04d}"


def _staff_voice_save_attachment(uploaded_file):
    if not uploaded_file:
        return None, None

    data = uploaded_file.getvalue()
    if len(data) > MAX_STAFF_VOICE_ATTACHMENT_SIZE:
        st.error("Attachment is too large. The maximum size is 15 MB.")
        return None, None

    suffix = Path(uploaded_file.name).suffix
    stored_name = f"{uuid.uuid4().hex}{suffix}"
    path = STAFF_VOICE_ATTACHMENTS_DIR / stored_name
    path.write_bytes(data)
    return uploaded_file.name, str(path)


def _staff_voice_get_responses(concern_id):
    connection = get_connection()
    rows = connection.execute(
        """
        SELECT r.response, r.created_at, u.full_name
        FROM staff_voice_responses r
        JOIN staff_users u ON u.id = r.responder_id
        WHERE r.concern_id = ?
        ORDER BY r.created_at ASC
        """,
        (concern_id,),
    ).fetchall()
    connection.close()
    return rows


def show_staff_voice(staff):
    """Staff-facing confidential reporting and case tracking."""
    st.title("🔒 Staff Voice & Confidential Concerns")
    st.caption(
        "A confidential channel for workplace problems, welfare concerns, "
        "safety issues and constructive suggestions."
    )

    st.info(
        "🔐 Your identity is stored securely for Super Admin accountability, "
        "but it is hidden from ordinary staff, managers and delegated operators. "
        "Only the Super Admin can view the reporter identity."
    )

    report_tab, my_cases_tab, guidance_tab = st.tabs(
        ["📝 Submit a Concern", "📋 My Cases", "ℹ️ How Confidentiality Works"]
    )

    with report_tab:
        st.subheader("Tell us what is happening")
        st.write(
            "You can raise a problem without having to confront it publicly. "
            "Please give enough detail for the organisation to understand and act on it."
        )

        with st.form("staff_voice_submit_form", clear_on_submit=True):
            category = st.selectbox("Concern Type", STAFF_VOICE_CATEGORIES, key="sv_category")
            subject = st.text_input(
                "Short Subject",
                placeholder="e.g. Difficulty obtaining materials needed for my work",
                key="sv_subject",
            )
            description = st.text_area(
                "Describe the concern",
                height=180,
                placeholder="Explain what happened, what you are experiencing, and what you think would help.",
                key="sv_description",
            )
            c1, c2 = st.columns(2)
            with c1:
                urgency = st.selectbox("Urgency", STAFF_VOICE_URGENCY, index=1, key="sv_urgency")
            with c2:
                area = st.selectbox("Area / Department", STAFF_VOICE_AREAS, key="sv_area")

            wants_response = st.checkbox(
                "I would like the Super Admin to respond to this case.",
                value=True,
                key="sv_wants_response",
            )
            attachment = st.file_uploader(
                "Optional supporting document or image (maximum 15 MB)",
                key="sv_attachment",
            )

            submitted = st.form_submit_button(
                "🔐 Submit Confidentially",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            if not subject.strip():
                st.error("Please enter a short subject.")
            elif not description.strip():
                st.error("Please describe the concern before submitting it.")
            else:
                connection = get_connection()
                try:
                    case_number = _next_staff_voice_case_number(connection)
                    attachment_name, attachment_path = _staff_voice_save_attachment(attachment)
                    connection.execute(
                        """
                        INSERT INTO staff_voice_concerns
                        (case_number, reporter_id, category, subject, description,
                         urgency, area, wants_response, attachment_name, attachment_path)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            case_number,
                            staff["id"],
                            category,
                            subject.strip(),
                            description.strip(),
                            urgency,
                            area,
                            1 if wants_response else 0,
                            attachment_name,
                            attachment_path,
                        ),
                    )
                    connection.commit()
                    case_id = connection.execute(
                        "SELECT id FROM staff_voice_concerns WHERE case_number = ?",
                        (case_number,),
                    ).fetchone()[0]
                    st.success(f"Your confidential concern has been received. Case number: **{case_number}**")
                    st.info("Keep this case number for future reference. Your identity is not shown in ordinary case views.")
                    _staff_voice_audit(
                        "SUBMIT_CONCERN",
                        "Confidential staff concern submitted.",
                        staff_id=staff["id"],
                        target_id=case_id,
                        details={"case_number": case_number, "category": category, "urgency": urgency},
                        severity="HIGH" if urgency == "Critical" else "INFO",
                    )
                except Exception as exc:
                    st.error(f"The confidential concern could not be saved: {exc}")
                finally:
                    connection.close()

    with my_cases_tab:
        connection = get_connection()
        cases = connection.execute(
            """
            SELECT id, case_number, category, subject, description, urgency,
                   area, wants_response, status, attachment_name, created_at, updated_at
            FROM staff_voice_concerns
            WHERE reporter_id = ?
            ORDER BY created_at DESC
            """,
            (staff["id"],),
        ).fetchall()
        connection.close()

        if not cases:
            st.info("You have not submitted any confidential concerns yet.")
        else:
            for case in cases:
                with st.expander(
                    f"{case['case_number']} • {case['subject']} • {case['status']}",
                    expanded=False,
                ):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Status", case["status"])
                    c2.metric("Urgency", case["urgency"])
                    c3.metric("Submitted", str(case["created_at"])[:10])
                    st.write(f"**Type:** {case['category']}")
                    st.write(f"**Area:** {case['area'] or 'Not specified'}")
                    st.write(f"**Concern:** {case['description']}")
                    if case["attachment_name"]:
                        attachment_path = Path(case["attachment_name"] and case["attachment_name"])
                        st.caption(f"Supporting file: {case['attachment_name']}")
                        # The actual file path is intentionally not exposed to the UI.
                        db = get_connection()
                        stored = db.execute(
                            "SELECT attachment_path FROM staff_voice_concerns WHERE id = ? AND reporter_id = ?",
                            (case["id"], staff["id"]),
                        ).fetchone()
                        db.close()
                        if stored and stored[0] and Path(stored[0]).exists():
                            with open(stored[0], "rb") as f:
                                st.download_button(
                                    "📎 Download your attachment",
                                    f.read(),
                                    file_name=case["attachment_name"],
                                    key=f"sv_download_{case['id']}",
                                )

                    responses = _staff_voice_get_responses(case["id"])
                    if responses:
                        st.markdown("### 💬 Super Admin Response")
                        for response in responses:
                            st.info(
                                f"**Super Admin • {response['created_at']}**\n\n{response['response']}"
                            )
                    elif case["wants_response"]:
                        st.caption("A response has not yet been posted.")

    with guidance_tab:
        st.subheader("🔐 Confidentiality Rules")
        st.markdown(
            """
            - Your **name and staff account are stored**, but are hidden from ordinary staff and managers.
            - Only the **Super Admin** can open the identity details of a case.
            - Each concern receives a confidential case number such as **PIA-CON-2026-0001**.
            - You can return to **My Cases** to follow the status of your own submissions.
            - The Super Admin can respond, change status and manage the case.
            - Important Staff Voice actions can be recorded in the existing tamper-evident Audit & Activity Log.
            """
        )


def show_confidential_concerns_admin(staff):
    """Super Admin-only case management. Reporter identity is deliberately shown here and nowhere else."""
    if staff["role"] != "Super Admin":
        st.error("🔒 Only the Super Admin can access confidential concern management.")
        return

    st.title("🛡️ Confidential Staff Concerns")
    st.caption("Super Admin control centre — reporter identities are protected from ordinary staff.")

    connection = get_connection()
    total = connection.execute("SELECT COUNT(*) FROM staff_voice_concerns").fetchone()[0]
    open_count = connection.execute(
        "SELECT COUNT(*) FROM staff_voice_concerns WHERE status NOT IN ('Resolved', 'Closed')"
    ).fetchone()[0]
    critical = connection.execute(
        "SELECT COUNT(*) FROM staff_voice_concerns WHERE urgency = 'Critical' AND status NOT IN ('Resolved', 'Closed')"
    ).fetchone()[0]
    resolved = connection.execute(
        "SELECT COUNT(*) FROM staff_voice_concerns WHERE status IN ('Resolved', 'Closed')"
    ).fetchone()[0]
    connection.close()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📥 Total Cases", total)
    c2.metric("🔎 Open Cases", open_count)
    c3.metric("🚨 Open Critical", critical)
    c4.metric("✅ Resolved / Closed", resolved)

    st.divider()

    f1, f2, f3 = st.columns(3)
    with f1:
        status_filter = st.selectbox("Status", ["All"] + STAFF_VOICE_STATUSES, key="sv_admin_status")
    with f2:
        urgency_filter = st.selectbox("Urgency", ["All"] + STAFF_VOICE_URGENCY, key="sv_admin_urgency")
    with f3:
        category_filter = st.selectbox("Category", ["All"] + STAFF_VOICE_CATEGORIES, key="sv_admin_category")

    connection = get_connection()
    query = """
        SELECT c.*, u.full_name AS reporter_name, u.username AS reporter_username,
               u.role AS reporter_role
        FROM staff_voice_concerns c
        JOIN staff_users u ON u.id = c.reporter_id
        WHERE 1=1
    """
    params = []
    if status_filter != "All":
        query += " AND c.status = ?"
        params.append(status_filter)
    if urgency_filter != "All":
        query += " AND c.urgency = ?"
        params.append(urgency_filter)
    if category_filter != "All":
        query += " AND c.category = ?"
        params.append(category_filter)
    query += " ORDER BY CASE c.urgency WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Normal' THEN 3 ELSE 4 END, c.created_at DESC"
    cases = connection.execute(query, params).fetchall()
    connection.close()

    if not cases:
        st.success("No confidential concerns match the selected filters.")
        return

    st.subheader("📋 Confidential Case Register")

    for case in cases:
        with st.expander(
            f"{case['case_number']} • {case['urgency']} • {case['status']} • {case['subject']}",
            expanded=False,
        ):
            # Explicit identity access is limited to this Super Admin view.
            st.warning(
                f"🔐 Reporter identity — {case['reporter_name']} (@{case['reporter_username']}) • {case['reporter_role']}"
            )
            _staff_voice_audit(
                "VIEW_CONFIDENTIAL_IDENTITY",
                "Super Admin viewed the reporter identity of a confidential staff concern.",
                staff_id=staff["id"],
                target_id=case["id"],
                details={"case_number": case["case_number"]},
            )

            c1, c2, c3 = st.columns(3)
            c1.metric("Status", case["status"])
            c2.metric("Urgency", case["urgency"])
            c3.metric("Submitted", str(case["created_at"])[:16])
            st.write(f"**Category:** {case['category']}")
            st.write(f"**Area:** {case['area'] or 'Not specified'}")
            st.write(f"**Subject:** {case['subject']}")
            st.write(f"**Concern:** {case['description']}")
            st.caption(f"Response requested: {'Yes' if case['wants_response'] else 'No'}")

            if case["attachment_name"] and case["attachment_path"] and Path(case["attachment_path"]).exists():
                with open(case["attachment_path"], "rb") as f:
                    st.download_button(
                        "📎 Download Supporting Attachment",
                        f.read(),
                        file_name=case["attachment_name"],
                        key=f"sv_admin_download_{case['id']}",
                    )

            responses = _staff_voice_get_responses(case["id"])
            if responses:
                st.markdown("### 💬 Response History")
                for response in responses:
                    st.info(f"**Super Admin • {response['created_at']}**\n\n{response['response']}")

            st.markdown("### ⚙️ Case Management")
            with st.form(f"sv_admin_manage_{case['id']}"):
                new_status = st.selectbox(
                    "Case Status",
                    STAFF_VOICE_STATUSES,
                    index=STAFF_VOICE_STATUSES.index(case["status"]) if case["status"] in STAFF_VOICE_STATUSES else 0,
                    key=f"sv_status_{case['id']}",
                )
                response_text = st.text_area(
                    "Response to Staff Member (optional)",
                    placeholder="Write a response that the reporting staff member will see in My Cases.",
                    key=f"sv_response_{case['id']}",
                )
                save_case = st.form_submit_button("💾 Save Case Update", type="primary", use_container_width=True)

            if save_case:
                db = get_connection()
                try:
                    db.execute(
                        "UPDATE staff_voice_concerns SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (new_status, case["id"]),
                    )
                    if response_text.strip():
                        db.execute(
                            "INSERT INTO staff_voice_responses (concern_id, responder_id, response) VALUES (?, ?, ?)",
                            (case["id"], staff["id"], response_text.strip()),
                        )
                    db.commit()
                    _staff_voice_audit(
                        "UPDATE_CASE",
                        "Super Admin updated a confidential staff concern.",
                        staff_id=staff["id"],
                        target_id=case["id"],
                        details={"case_number": case["case_number"], "status": new_status, "response_added": bool(response_text.strip())},
                    )
                    st.success("Confidential case updated successfully.")
                    st.rerun()
                finally:
                    db.close()


def show_staff_voice_analytics(staff):
    """High-level Super Admin analytics without exposing identities in the summary."""
    if staff["role"] != "Super Admin":
        return

    st.subheader("📊 Staff Voice Analytics")
    connection = get_connection()
    rows = connection.execute(
        "SELECT category, status, urgency, created_at FROM staff_voice_concerns"
    ).fetchall()
    connection.close()

    if not rows:
        st.info("Analytics will appear after confidential concerns are submitted.")
        return

    categories = {}
    statuses = {}
    urgencies = {}
    for row in rows:
        categories[row["category"]] = categories.get(row["category"], 0) + 1
        statuses[row["status"]] = statuses.get(row["status"], 0) + 1
        urgencies[row["urgency"]] = urgencies.get(row["urgency"], 0) + 1

    a1, a2, a3 = st.columns(3)
    with a1:
        st.markdown("**Cases by Category**")
        st.table([{"Category": k, "Cases": v} for k, v in sorted(categories.items(), key=lambda x: (-x[1], x[0]))])
    with a2:
        st.markdown("**Cases by Status**")
        st.table([{"Status": k, "Cases": v} for k, v in sorted(statuses.items(), key=lambda x: (-x[1], x[0]))])
    with a3:
        st.markdown("**Cases by Urgency**")
        st.table([{"Urgency": k, "Cases": v} for k, v in sorted(urgencies.items(), key=lambda x: (-x[1], x[0]))])


# ============================================================

# ============================================================
# STAFF PORTAL
# ============================================================


STAFF_TOOL_LABELS = {key: label for key, label, _ in STAFF_MODULES}

def _restricted_tool(module_key, staff):
    label = STAFF_TOOL_LABELS.get(module_key, module_key)
    st.markdown(f"### {label}")
    st.warning("🔒 **Access Restricted**")
    st.write("This tool is available in the Pan Ideate Africa staff toolbox, but your current authorization does not permit access.")
    st.info(f"Your administrator can grant access to **{label}** when appropriate.")
    st.caption(f"Current role: {staff['role']} • Access is controlled by your individual authorization profile.")

def _render_staff_tool(module_key, staff):
    if not has_staff_tool_access(staff['id'], module_key):
        _restricted_tool(module_key, staff)
        return
    try:
        if module_key == 'leave_attendance':
            from pages.leave_attendance import show_staff
            show_staff(staff['id'])
        elif module_key == 'expenses_procurement':
            from pages.expenses_procurement import show_staff
            show_staff(staff['id'])
        elif module_key == 'tasks':
            from pages.task_manager import show_staff
            show_staff(staff['id'])
        elif module_key == 'staff_directory':
            show_staff_directory_v1(staff['id'])
        elif module_key == 'staff_messages':
            st.subheader("✉️ Internal Staff Messages")
            inbox_tab, compose_tab, sent_tab = st.tabs([f"📥 Inbox ({get_unread_count()})", "📝 Compose Message", "📤 Sent Messages"])
            with inbox_tab: show_inbox()
            with compose_tab: compose_message()
            with sent_tab: show_sent()
        elif module_key == 'notifications':
            show_notification_centre(staff['id'])
        elif module_key == 'documents':
            show_document_centre(staff['id'])
        elif module_key == 'ai_assistant':
            show_staff_ai_assistant(staff['id'])
        elif module_key == 'meetings':
            show_staff_meeting_centre(staff['id'])
        elif module_key == 'approvals':
            if has_approval_access(staff['id']): show_staff_approval_centre(staff['id'])
            else: _restricted_tool(module_key, staff)
        elif module_key == 'audit_log':
            from pages.audit_log import show_audit_log
            show_audit_log()
        elif module_key == 'innovation':
            from pages.innovation_engine import show_page
            show_page(staff)
        else:
            st.markdown(f"### {STAFF_TOOL_LABELS.get(module_key, module_key)}")
            st.info("🛠️ This tool is reserved in the staff toolbox and is ready for future staff-facing activation. Your access permission has been recorded.")
    except Exception as exc:
        st.error(f"The {STAFF_TOOL_LABELS.get(module_key, module_key)} tool could not be opened safely yet.")
        st.caption(f"Technical detail: {exc}")

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
    init_access_control()
    notification_count = get_notification_count(staff["id"])
    approval_access = has_approval_access(staff["id"])

    # Complete toolbox stays visible; permissions are enforced when opened.
    tabs = [
        "🏠 Dashboard", f"🔔 Notifications ({notification_count})", "👥 Staff Directory",
        "🕘 Leave & Attendance", "💰 Expenses & Procurement", "📋 Task & Project Manager",
        "💬 Staff Communications", "✉️ Messages", "👤 My Profile", "📁 Documents",
        "🤖 AI Staff Assistant", "📅 Meeting Centre", "✅ Approval Centre",
        "🔐 Audit & Activity Log", "💡 Innovation Ideas", "🎓 Learning Centre", "📚 Knowledge Hub",
        "🔒 Staff Voice", "🛡️ Staff Management",
    ]

    selected_tab = st.tabs(tabs)

    tab_indices = {
        label: index
        for index, label in enumerate(tabs)
    }

    notification_tab = next(
        label
        for label in tabs
        if label.startswith("🔔 Notifications")
    )

    # --------------------------------------------------------
    # DASHBOARD TAB
    # --------------------------------------------------------
    with selected_tab[tab_indices["🏠 Dashboard"]]:
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
    # STAFF TOOLBOX
    # --------------------------------------------------------
    with selected_tab[tab_indices[f"🔔 Notifications ({notification_count})"]]: _render_staff_tool('notifications', staff)
    with selected_tab[tab_indices["👥 Staff Directory"]]: _render_staff_tool('staff_directory', staff)
    with selected_tab[tab_indices["🕘 Leave & Attendance"]]: _render_staff_tool('leave_attendance', staff)
    with selected_tab[tab_indices["💰 Expenses & Procurement"]]: _render_staff_tool('expenses_procurement', staff)
    with selected_tab[tab_indices["📋 Task & Project Manager"]]: _render_staff_tool('tasks', staff)
    with selected_tab[tab_indices["💬 Staff Communications"]]: _render_staff_tool('staff_communications', staff)
    with selected_tab[tab_indices["✉️ Messages"]]: _render_staff_tool('staff_messages', staff)
    with selected_tab[tab_indices["👤 My Profile"]]: show_profile()
    with selected_tab[tab_indices["📁 Documents"]]: _render_staff_tool('documents', staff)
    with selected_tab[tab_indices["🤖 AI Staff Assistant"]]: _render_staff_tool('ai_assistant', staff)
    with selected_tab[tab_indices["📅 Meeting Centre"]]: _render_staff_tool('meetings', staff)
    with selected_tab[tab_indices["✅ Approval Centre"]]: _render_staff_tool('approvals', staff)
    with selected_tab[tab_indices["🔐 Audit & Activity Log"]]: _render_staff_tool('audit_log', staff)
    with selected_tab[tab_indices["💡 Innovation Ideas"]]: _render_staff_tool('innovation', staff)
    with selected_tab[tab_indices["🎓 Learning Centre"]]: _render_staff_tool('learning', staff)
    with selected_tab[tab_indices["📚 Knowledge Hub"]]: _render_staff_tool('knowledge_hub', staff)

    # --------------------------------------------------------
    # CONFIDENTIAL STAFF VOICE
    # Available to all active staff; it is intentionally separate
    # from ordinary module-access permissions so staff can report
    # concerns without needing permission from a manager.
    # --------------------------------------------------------
    with selected_tab[tab_indices["🔒 Staff Voice"]]:
        show_staff_voice(staff)

    with selected_tab[tab_indices["🛡️ Staff Management"]]:
        if staff["role"] == "Super Admin":
            show_staff_management()
        else:
            _render_staff_tool("staff_management", staff)

    # --------------------------------------------------------
    # SUPER ADMIN — CONFIDENTIAL CONCERNS MANAGEMENT
    # --------------------------------------------------------
    if staff["role"] == "Super Admin":
        with selected_tab[tab_indices["🔒 Staff Voice"]]:
            st.divider()
            st.subheader("🛡️ Super Admin Confidential Concerns Management")
            show_confidential_concerns_admin(staff)
            st.divider()
            show_staff_voice_analytics(staff)

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