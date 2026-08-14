import streamlit as st
import sqlite3
import mimetypes
import uuid
from pathlib import Path
from datetime import datetime


# ============================================================
# PAN IDEATE AFRICA — DOCUMENT CENTRE V1
# ============================================================
# Internal document storage for Admin and Staff.
#
# This module is intentionally self-contained in V1.
# It uses the existing Pan Ideate Africa database and staff_users
# table, but does NOT modify Admin Centre or Staff Portal yet.
# We will connect it to those areas after this module is tested.
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "pan_ideate.db"
DOCUMENTS_DIR = DATA_DIR / "documents"

MAX_DOCUMENT_SIZE = 50 * 1024 * 1024  # 50 MB

ALLOWED_EXTENSIONS = [
    "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
    "csv", "txt", "rtf", "jpg", "jpeg", "png", "gif",
    "webp", "zip"
]

CATEGORIES = [
    "Administration",
    "Finance",
    "Human Resources",
    "Projects",
    "Research",
    "Training",
    "Reports",
    "Policies & SOPs",
    "Marketing",
    "Other",
]

ACCESS_OPTIONS = [
    "Admin Only",
    "All Staff",
    "Selected Staff",
]


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    return conn


def init_document_database():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_name TEXT NOT NULL,
            stored_name TEXT NOT NULL UNIQUE,
            mime_type TEXT,
            file_size INTEGER NOT NULL DEFAULT 0,
            category TEXT NOT NULL DEFAULT 'Other',
            description TEXT,
            access_level TEXT NOT NULL DEFAULT 'Admin Only',
            uploaded_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_archived INTEGER NOT NULL DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS document_access (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            staff_id INTEGER NOT NULL,
            granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(document_id, staff_id)
        )
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_documents_category
        ON documents(category)
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_documents_uploaded_by
        ON documents(uploaded_by)
    """)

    conn.commit()
    conn.close()


# ============================================================
# STAFF HELPERS
# ============================================================

def get_staff_members():
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT id, full_name, username, role, status
            FROM staff_users
            WHERE status = 'Active'
            ORDER BY full_name
        """).fetchall()
    except sqlite3.OperationalError:
        rows = []

    conn.close()
    return rows


def get_staff(staff_id):
    if not staff_id:
        return None

    conn = get_connection()

    try:
        row = conn.execute("""
            SELECT id, full_name, username, role, status
            FROM staff_users
            WHERE id = ?
            LIMIT 1
        """, (staff_id,)).fetchone()
    except sqlite3.OperationalError:
        row = None

    conn.close()
    return row


def is_super_admin(staff_id):
    staff = get_staff(staff_id)
    return bool(staff and staff["role"] == "Super Admin")


# ============================================================
# DOCUMENT HELPERS
# ============================================================

def format_size(size):
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    if size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    return f"{size / (1024 * 1024 * 1024):.1f} GB"


def document_is_allowed(document_row, staff_id):
    if not staff_id:
        return False

    if is_super_admin(staff_id):
        return True

    access_level = document_row["access_level"]

    if access_level == "All Staff":
        return True

    if access_level == "Admin Only":
        return False

    conn = get_connection()

    row = conn.execute("""
        SELECT id
        FROM document_access
        WHERE document_id = ?
          AND staff_id = ?
        LIMIT 1
    """, (
        document_row["id"],
        staff_id,
    )).fetchone()

    conn.close()

    return row is not None


def get_visible_documents(staff_id, category="All", search_text=""):
    if not staff_id:
        return []

    conn = get_connection()

    query = """
        SELECT
            d.*,
            u.full_name AS uploader_name
        FROM documents AS d
        LEFT JOIN staff_users AS u
            ON d.uploaded_by = u.id
        WHERE d.is_archived = 0
    """

    params = []

    if category != "All":
        query += " AND d.category = ?"
        params.append(category)

    if search_text.strip():
        query += """
            AND (
                LOWER(d.original_name) LIKE ?
                OR LOWER(COALESCE(d.description, '')) LIKE ?
            )
        """
        term = f"%{search_text.strip().lower()}%"
        params.extend([term, term])

    query += " ORDER BY d.created_at DESC"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return [
        row for row in rows
        if document_is_allowed(row, staff_id)
    ]


def save_document(
    uploaded_file,
    uploaded_by,
    category,
    description,
    access_level,
    selected_staff_ids=None,
):
    if uploaded_file is None:
        return False, "No file selected."

    if not uploaded_by:
        return False, "You must be logged in to upload a document."

    data = uploaded_file.getvalue()

    if len(data) > MAX_DOCUMENT_SIZE:
        return False, "The maximum document size is 50 MB."

    extension = Path(uploaded_file.name).suffix.lower().lstrip(".")

    if extension not in ALLOWED_EXTENSIONS:
        return False, (
            "This file type is not allowed. "
            "Please upload a supported office document, PDF, image or ZIP."
        )

    stored_name = f"{uuid.uuid4().hex}.{extension}"
    stored_path = DOCUMENTS_DIR / stored_name

    try:
        stored_path.write_bytes(data)

        mime_type = (
            uploaded_file.type
            or mimetypes.guess_type(uploaded_file.name)[0]
            or "application/octet-stream"
        )

        conn = get_connection()

        cur = conn.cursor()
        cur.execute("""
            INSERT INTO documents (
                original_name,
                stored_name,
                mime_type,
                file_size,
                category,
                description,
                access_level,
                uploaded_by
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            uploaded_file.name,
            stored_name,
            mime_type,
            len(data),
            category,
            description.strip(),
            access_level,
            uploaded_by,
        ))

        document_id = cur.lastrowid

        if access_level == "Selected Staff":
            for staff_id in selected_staff_ids or []:
                cur.execute("""
                    INSERT OR IGNORE INTO document_access
                    (document_id, staff_id)
                    VALUES (?, ?)
                """, (
                    document_id,
                    int(staff_id),
                ))

        conn.commit()
        conn.close()

        return True, "Document uploaded successfully."

    except Exception as exc:
        try:
            if stored_path.exists():
                stored_path.unlink()
        except Exception:
            pass

        return False, f"Could not save the document: {exc}"


def read_document(document_row):
    path = DOCUMENTS_DIR / document_row["stored_name"]

    if path.exists():
        return path.read_bytes()

    return None


def archive_document(document_id, staff_id):
    if not is_super_admin(staff_id):
        return False

    conn = get_connection()

    conn.execute("""
        UPDATE documents
        SET is_archived = 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (document_id,))

    conn.commit()
    conn.close()

    return True


# ============================================================
# UPLOAD INTERFACE
# ============================================================

def show_upload_area(staff_id):
    st.subheader("⬆️ Upload Document")

    if not is_super_admin(staff_id):
        st.info(
            "Staff document uploading will be enabled according to "
            "document permissions in the next integration stage."
        )
        return

    with st.form("document_upload_form", clear_on_submit=True):

        uploaded_file = st.file_uploader(
            "Choose a document",
            type=ALLOWED_EXTENSIONS,
            help="Maximum file size: 50 MB."
        )

        col1, col2 = st.columns(2)

        with col1:
            category = st.selectbox(
                "Category",
                CATEGORIES
            )

        with col2:
            access_level = st.selectbox(
                "Who can access this document?",
                ACCESS_OPTIONS
            )

        description = st.text_area(
            "Description",
            placeholder="Briefly describe this document..."
        )

        selected_staff_ids = []

        if access_level == "Selected Staff":
            staff_members = get_staff_members()

            if staff_members:
                selected_staff_ids = st.multiselect(
                    "Select staff members",
                    options=[row["id"] for row in staff_members],
                    format_func=lambda staff_id: next(
                        (
                            row["full_name"]
                            for row in staff_members
                            if row["id"] == staff_id
                        ),
                        str(staff_id)
                    )
                )
            else:
                st.warning("No active staff members were found.")

        submitted = st.form_submit_button(
            "📤 Upload Document",
            use_container_width=True
        )

        if submitted:
            success, message = save_document(
                uploaded_file=uploaded_file,
                uploaded_by=staff_id,
                category=category,
                description=description,
                access_level=access_level,
                selected_staff_ids=selected_staff_ids,
            )

            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)


# ============================================================
# DOCUMENT LIST
# ============================================================

def show_document_library(staff_id):
    st.subheader("📚 Document Library")

    col1, col2 = st.columns([1, 2])

    with col1:
        category = st.selectbox(
            "Filter by category",
            ["All"] + CATEGORIES,
            key="document_category_filter"
        )

    with col2:
        search_text = st.text_input(
            "🔎 Search documents",
            placeholder="Search by filename or description...",
            key="document_search"
        )

    documents = get_visible_documents(
        staff_id,
        category=category,
        search_text=search_text
    )

    st.caption(f"{len(documents)} document(s) available to you.")

    if not documents:
        st.info("No documents found.")
        return

    for document in documents:

        with st.container(border=True):

            col1, col2, col3 = st.columns([4, 2, 1])

            with col1:
                st.markdown(
                    f"### 📄 {document['original_name']}"
                )

                description = document["description"] or "No description."

                st.write(description)

                st.caption(
                    f"📂 {document['category']}  •  "
                    f"👤 {document['uploader_name'] or 'Unknown'}  •  "
                    f"📦 {format_size(document['file_size'])}"
                )

            with col2:
                st.write(
                    f"**Access:** {document['access_level']}"
                )
                st.write(
                    f"**Uploaded:** {document['created_at']}"
                )

            with col3:
                file_bytes = read_document(document)

                if file_bytes is not None:
                    st.download_button(
                        "⬇️ Download",
                        data=file_bytes,
                        file_name=document["original_name"],
                        mime=document["mime_type"]
                        or "application/octet-stream",
                        key=f"download_document_{document['id']}",
                        use_container_width=True
                    )
                else:
                    st.error("File unavailable.")

                if is_super_admin(staff_id):
                    if st.button(
                        "🗄️ Archive",
                        key=f"archive_document_{document['id']}",
                        use_container_width=True
                    ):
                        if archive_document(
                            document["id"],
                            staff_id
                        ):
                            st.success("Document archived.")
                            st.rerun()


# ============================================================
# MAIN DOCUMENT CENTRE
# ============================================================

def show_document_centre(staff_id=None):

    init_document_database()

    if not staff_id:
        st.error(
            "🔒 Document Centre requires an authenticated Admin or Staff account."
        )
        return

    staff = get_staff(staff_id)

    if not staff or staff["status"] != "Active":
        st.error("Your staff account is not available.")
        return

    st.title("📁 Document Centre")

    st.caption(
        "Pan Ideate Africa — Internal Document Management"
    )

    st.success(
        f"Signed in as: {staff['full_name']} • {staff['role']}"
    )

    tab1, tab2 = st.tabs([
        "📚 Document Library",
        "⬆️ Upload Document"
    ])

    with tab1:
        show_document_library(staff_id)

    with tab2:
        show_upload_area(staff_id)


# ============================================================
# ADMIN COMPATIBILITY ENTRY POINT
# ============================================================

def show_admin_document_centre(admin_staff_id):
    """
    Entry point for the Admin Centre.

    Kept separate so Admin Centre can connect to Document Centre
    without changing the Document Centre's core functions.
    """
    show_document_centre(admin_staff_id)
