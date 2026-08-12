import streamlit as st
import hashlib
import sqlite3
from pathlib import Path


# ============================================================
# PAN IDEATE AFRICA — STAFF LOGIN
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "pan_ideate.db"


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    DATA_DIR.mkdir(exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def init_staff_table():
    connection = get_connection()
    cursor = connection.cursor()

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

    connection.commit()
    connection.close()


# ============================================================
# PASSWORD SECURITY
# ============================================================

def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def verify_password(password, password_hash):
    return hash_password(password) == password_hash


# ============================================================
# CREATE INITIAL SUPER ADMIN
# ============================================================

def create_initial_admin():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM staff_users WHERE username = ?",
        ("admin",)
    )

    existing_admin = cursor.fetchone()

    if not existing_admin:
        cursor.execute("""
            INSERT INTO staff_users
            (
                full_name,
                username,
                password_hash,
                role,
                status
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            "Pan Ideate Africa Administrator",
            "admin",
            hash_password("PanIdeate@2026"),
            "Super Admin",
            "Active"
        ))

        connection.commit()

    connection.close()


# ============================================================
# AUTHENTICATION
# ============================================================

def authenticate(username, password):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM staff_users
        WHERE username = ?
        AND status = 'Active'
    """, (username.strip(),))

    staff = cursor.fetchone()

    if staff and verify_password(
        password,
        staff["password_hash"]
    ):

        cursor.execute("""
            UPDATE staff_users
            SET last_login = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (staff["id"],))

        connection.commit()
        connection.close()

        return staff

    connection.close()

    return None


# ============================================================
# LOGIN PAGE
# ============================================================

def show_login():

    st.set_page_config(
        page_title="Pan Ideate Africa — Staff Login",
        page_icon="🔐",
        layout="centered"
    )

    st.markdown(
        """
        <style>

        .login-title {
            text-align: center;
            font-size: 34px;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .login-subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-title">🌍 Pan Ideate Africa</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-subtitle">Staff Administration Portal</div>',
        unsafe_allow_html=True
    )

    st.divider()

    st.subheader("🔐 Staff Login")

    username = st.text_input(
        "Username",
        placeholder="Enter your staff username"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password"
    )

    login = st.button(
        "🔓 Sign In",
        use_container_width=True
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

            st.session_state["staff_logged_in"] = True
            st.session_state["staff_id"] = staff["id"]
            st.session_state["staff_name"] = staff["full_name"]
            st.session_state["staff_username"] = staff["username"]
            st.session_state["staff_role"] = staff["role"]

            st.success(
                f"Welcome, {staff['full_name']}!"
            )

            st.info(
                f"Role: {staff['role']}"
            )

            st.rerun()

        else:

            st.error(
                "Invalid username or password."
            )


# ============================================================
# LOGGED-IN STAFF VIEW
# ============================================================

def show_staff_portal():

    st.success(
        f"Welcome back, {st.session_state.get('staff_name', 'Staff Member')}!"
    )

    st.write(
        f"**Role:** {st.session_state.get('staff_role', 'Staff')}"
    )

    st.divider()

    st.header("🛡️ Staff Administration Portal")

    st.info(
        "Staff authentication is active. "
        "The Admin Centre will be connected here next."
    )

    if st.button("🚪 Logout", use_container_width=True):

        for key in [
            "staff_logged_in",
            "staff_id",
            "staff_name",
            "staff_username",
            "staff_role"
        ]:
            st.session_state.pop(key, None)

        st.rerun()


# ============================================================
# APPLICATION START
# ============================================================

init_staff_table()
create_initial_admin()

if "staff_logged_in" not in st.session_state:
    st.session_state["staff_logged_in"] = False


if st.session_state["staff_logged_in"]:
    show_staff_portal()
else:
    show_login()