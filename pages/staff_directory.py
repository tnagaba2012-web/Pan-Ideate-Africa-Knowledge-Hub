import sqlite3
from pathlib import Path
from datetime import date
import streamlit as st

# ============================================================
# PAN IDEATE AFRICA
# STAFF DIRECTORY V1
# ============================================================
# Purpose:
# Central employee directory shared by Admin and Staff.
#
# V1 includes:
# - Full Name
# - Staff ID
# - Username
# - Job Title
# - Department
# - Phone
# - Email
# - Work Location
# - Date Joined
# - Role
# - Status
# - Optional Bio
# - Search and filters
# - Admin editing
# - Staff read-only directory
#
# IMPORTANT:
# Existing staff accounts are preserved.
# New directory fields are added safely with ALTER TABLE only
# when they do not already exist.
#
# FUTURE ROADMAP:
# Admin-controlled module permissions will later allow the
# Administrator to choose exactly which staff members can access
# each internal module (Leave & Attendance, Expenses & Procurement,
# Documents, Tasks, etc.). That access-control layer is NOT
# activated in V1.
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "pan_ideate.db"

DEPARTMENTS = [
    "",
    "Administration",
    "Agriculture",
    "Business Development",
    "Finance",
    "Human Resources",
    "Information Technology",
    "Innovation",
    "Learning Centre",
    "Minerals & Chemistry",
    "Pigment Preparation Laboratory",
    "Research & Knowledge",
    "Other",
]

STATUSES = ["Active", "Inactive", "Suspended"]


def db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def ensure_directory_fields():
    """Safely add directory fields to the existing staff_users table."""
    con = db()
    cur = con.cursor()

    cur.execute("""
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

    existing = {
        row["name"]
        for row in cur.execute(
            "PRAGMA table_info(staff_users)"
        ).fetchall()
    }

    new_columns = {
        "staff_id": "TEXT",
        "job_title": "TEXT",
        "department": "TEXT",
        "phone": "TEXT",
        "email": "TEXT",
        "work_location": "TEXT",
        "date_joined": "TEXT",
        "bio": "TEXT",
    }

    for column, definition in new_columns.items():
        if column not in existing:
            cur.execute(
                f"ALTER TABLE staff_users ADD COLUMN {column} {definition}"
            )

    con.commit()
    con.close()


def get_staff(staff_id):
    ensure_directory_fields()
    con = db()
    row = con.execute("""
        SELECT
            id, staff_id, full_name, username, job_title,
            department, phone, email, work_location,
            date_joined, role, status, bio, created_at, last_login
        FROM staff_users
        WHERE id = ?
        LIMIT 1
    """, (staff_id,)).fetchone()
    con.close()
    return row


def get_directory_staff(
    search="",
    department="All",
    role="All",
    status="Active",
):
    ensure_directory_fields()
    con = db()

    query = """
        SELECT
            id, staff_id, full_name, username, job_title,
            department, phone, email, work_location,
            date_joined, role, status, bio
        FROM staff_users
        WHERE 1=1
    """
    params = []

    if search.strip():
        term = f"%{search.strip()}%"
        query += """
            AND (
                full_name LIKE ?
                OR username LIKE ?
                OR staff_id LIKE ?
                OR job_title LIKE ?
                OR department LIKE ?
            )
        """
        params.extend([term] * 5)

    if department != "All":
        query += " AND department = ?"
        params.append(department)

    if role != "All":
        query += " AND role = ?"
        params.append(role)

    if status != "All":
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY full_name COLLATE NOCASE"

    rows = con.execute(query, params).fetchall()
    con.close()
    return rows


def update_directory_profile(
    staff_id,
    full_name,
    staff_identifier,
    job_title,
    department,
    phone,
    email,
    work_location,
    date_joined,
    role,
    status,
    bio,
):
    ensure_directory_fields()

    if not full_name.strip():
        return False, "Full Name is required."

    if not role.strip():
        return False, "Role is required."

    if status not in STATUSES:
        return False, "Invalid account status."

    con = db()

    try:
        con.execute("""
            UPDATE staff_users
            SET
                full_name = ?,
                staff_id = ?,
                job_title = ?,
                department = ?,
                phone = ?,
                email = ?,
                work_location = ?,
                date_joined = ?,
                role = ?,
                status = ?,
                bio = ?
            WHERE id = ?
        """, (
            full_name.strip(),
            staff_identifier.strip(),
            job_title.strip(),
            department.strip(),
            phone.strip(),
            email.strip(),
            work_location.strip(),
            date_joined.strip(),
            role.strip(),
            status,
            bio.strip(),
            staff_id,
        ))

        con.commit()
    except sqlite3.IntegrityError as error:
        con.close()
        return False, f"Could not save staff profile: {error}"

    con.close()
    return True, "Staff directory profile updated successfully."


def _roles():
    ensure_directory_fields()
    con = db()
    rows = con.execute("""
        SELECT DISTINCT role
        FROM staff_users
        WHERE role IS NOT NULL AND TRIM(role) != ''
        ORDER BY role
    """).fetchall()
    con.close()
    return [r["role"] for r in rows]


def show_staff_directory(staff_id=None):
    """Read-only directory for logged-in staff."""
    ensure_directory_fields()

    st.title("👥 Staff Directory")
    st.caption(
        "Pan Ideate Africa — Authorized Staff Directory"
    )

    search = st.text_input(
        "🔎 Search Staff",
        placeholder="Search by name, Staff ID, username, job title or department",
        key="directory_staff_search",
    )

    roles = ["All"] + _roles()
    departments = ["All"] + [
        d for d in DEPARTMENTS if d
    ]

    c1, c2, c3 = st.columns(3)

    with c1:
        department = st.selectbox(
            "Department",
            departments,
            key="directory_staff_department",
        )

    with c2:
        role = st.selectbox(
            "Role",
            roles,
            key="directory_staff_role",
        )

    with c3:
        status = st.selectbox(
            "Status",
            ["Active", "All", "Inactive", "Suspended"],
            key="directory_staff_status",
        )

    rows = get_directory_staff(
        search=search,
        department=department,
        role=role,
        status=status,
    )

    st.caption(f"{len(rows)} staff member(s) found.")

    if not rows:
        st.info("No staff members match your search.")
        return

    for employee in rows:
        with st.container(border=True):
            c1, c2 = st.columns([3, 2])

            with c1:
                st.subheader(employee["full_name"])

                if employee["job_title"]:
                    st.write(f"**{employee['job_title']}**")

                st.caption(
                    f"Staff ID: {employee['staff_id'] or 'Not yet assigned'}"
                )

                st.caption(
                    f"@{employee['username']} • {employee['role']}"
                )

                if employee["department"]:
                    st.write(
                        f"**Department:** {employee['department']}"
                    )

            with c2:
                status_icon = {
                    "Active": "🟢",
                    "Inactive": "⚪",
                    "Suspended": "🔴",
                }.get(employee["status"], "⚪")

                st.write(
                    f"**Status:** {status_icon} {employee['status']}"
                )

                if employee["phone"]:
                    st.write(f"📞 {employee['phone']}")

                if employee["email"]:
                    st.write(f"✉️ {employee['email']}")

                if employee["work_location"]:
                    st.write(
                        f"📍 {employee['work_location']}"
                    )

            if employee["bio"]:
                st.caption(employee["bio"])


def show_admin_staff_directory(admin_id=None):
    """Administrator view: search, inspect and maintain staff profiles."""
    ensure_directory_fields()

    st.title("👥 Staff Directory")
    st.caption(
        "Pan Ideate Africa — Staff Directory Administration"
    )

    st.info(
        "Use this section to maintain authorized employee directory "
        "information. Existing login accounts are preserved."
    )

    rows = get_directory_staff(status="All")
    active_count = sum(
        1 for r in rows if r["status"] == "Active"
    )
    inactive_count = len(rows) - active_count

    a, b, c = st.columns(3)
    a.metric("👥 Total Staff", len(rows))
    b.metric("🟢 Active", active_count)
    c.metric("⚪ Other Status", inactive_count)

    st.divider()

    search = st.text_input(
        "🔎 Search employee",
        placeholder="Name, Staff ID, username, role or department",
        key="directory_admin_search",
    )

    departments = ["All"] + [
        d for d in DEPARTMENTS if d
    ]
    roles = ["All"] + _roles()

    c1, c2, c3 = st.columns(3)

    with c1:
        department = st.selectbox(
            "Department",
            departments,
            key="directory_admin_department",
        )

    with c2:
        role = st.selectbox(
            "Role",
            roles,
            key="directory_admin_role",
        )

    with c3:
        status = st.selectbox(
            "Status",
            ["All", "Active", "Inactive", "Suspended"],
            key="directory_admin_status",
        )

    rows = get_directory_staff(
        search=search,
        department=department,
        role=role,
        status=status,
    )

    st.caption(f"{len(rows)} employee record(s) found.")

    if not rows:
        st.info("No employee records found.")
        return

    for employee in rows:
        with st.expander(
            f"{employee['full_name']} — "
            f"{employee['role']} — "
            f"{employee['status']}"
        ):
            with st.form(
                f"directory_edit_{employee['id']}"
            ):
                c1, c2 = st.columns(2)

                with c1:
                    full_name = st.text_input(
                        "Full Name",
                        value=employee["full_name"] or "",
                    )
                    staff_identifier = st.text_input(
                        "Staff ID",
                        value=employee["staff_id"] or "",
                    )
                    username = st.text_input(
                        "Username",
                        value=employee["username"] or "",
                        disabled=True,
                    )
                    job_title = st.text_input(
                        "Job Title",
                        value=employee["job_title"] or "",
                    )
                    department_value = st.selectbox(
                        "Department",
                        DEPARTMENTS,
                        index=(
                            DEPARTMENTS.index(employee["department"])
                            if employee["department"] in DEPARTMENTS
                            else 0
                        ),
                    )

                with c2:
                    phone = st.text_input(
                        "Phone",
                        value=employee["phone"] or "",
                    )
                    email = st.text_input(
                        "Email",
                        value=employee["email"] or "",
                    )
                    work_location = st.text_input(
                        "Work Location",
                        value=employee["work_location"] or "",
                    )
                    date_joined = st.text_input(
                        "Date Joined",
                        value=employee["date_joined"] or "",
                        placeholder="YYYY-MM-DD",
                    )

                    roles_for_form = list(
                        dict.fromkeys(
                            [employee["role"]] + [
                                r for r in _roles()
                                if r != employee["role"]
                            ]
                        )
                    )
                    role_value = st.selectbox(
                        "Role",
                        roles_for_form,
                        index=0,
                    )

                    status_value = st.selectbox(
                        "Status",
                        STATUSES,
                        index=(
                            STATUSES.index(employee["status"])
                            if employee["status"] in STATUSES
                            else 0
                        ),
                    )

                bio = st.text_area(
                    "Professional Bio / Notes",
                    value=employee["bio"] or "",
                )

                save = st.form_submit_button(
                    "💾 Save Staff Directory Record",
                    use_container_width=True,
                    type="primary",
                )

                if save:
                    ok, message = update_directory_profile(
                        employee["id"],
                        full_name,
                        staff_identifier,
                        job_title,
                        department_value,
                        phone,
                        email,
                        work_location,
                        date_joined,
                        role_value,
                        status_value,
                        bio,
                    )

                    if ok:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

            st.caption(
                "🔐 Username and password remain part of the existing "
                "authentication system and are not changed here."
            )


def show_staff(staff_id):
    show_staff_directory(staff_id)


def show_admin(admin_id):
    show_admin_staff_directory(admin_id)


def show(user_id=None, admin=False):
    if admin:
        show_admin_staff_directory(user_id)
    else:
        show_staff_directory(user_id)


ensure_directory_fields()
