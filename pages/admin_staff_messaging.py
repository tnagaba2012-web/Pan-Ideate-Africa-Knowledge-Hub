import streamlit as st
import sqlite3
import mimetypes
from pathlib import Path

from utils.database import get_connection


# ============================================================
# PAN IDEATE AFRICA — ADMIN STAFF MESSAGING
# ============================================================

MAX_ATTACHMENT_SIZE = 25 * 1024 * 1024

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ATTACHMENTS_DIR = DATA_DIR / "staff_attachments"


def ensure_staff_messaging_tables():
    """Create/migrate the attachment table safely."""
    DATA_DIR.mkdir(exist_ok=True)
    ATTACHMENTS_DIR.mkdir(exist_ok=True)

    connection = get_connection()
    cursor = connection.cursor()

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

    cursor.execute("PRAGMA table_info(staff_message_attachments)")
    columns = {row["name"] for row in cursor.fetchall()}

    if "file_data" not in columns:
        cursor.execute(
            "ALTER TABLE staff_message_attachments ADD COLUMN file_data BLOB"
        )

    connection.commit()
    connection.close()


def get_admin_staff_id():
    """Get the real Super Admin staff ID used by the internal message system."""
    connection = get_connection()

    row = connection.execute("""
        SELECT id
        FROM staff_users
        WHERE LOWER(username) = 'admin'
          AND status = 'Active'
        LIMIT 1
    """).fetchone()

    connection.close()

    return row["id"] if row else None


def get_active_staff_for_admin():
    """Return active employees other than the Super Admin."""
    connection = get_connection()

    rows = connection.execute("""
        SELECT id, full_name, username, role, status
        FROM staff_users
        WHERE status = 'Active'
          AND LOWER(username) != 'admin'
        ORDER BY full_name
    """).fetchall()

    connection.close()
    return rows


def save_admin_attachment(uploaded_file, message_id, admin_id):
    """Store the complete attachment in SQLite as well as a local fallback."""
    if uploaded_file is None:
        return

    data = uploaded_file.getvalue()

    if len(data) > MAX_ATTACHMENT_SIZE:
        raise ValueError(
            f"{uploaded_file.name} is larger than 25 MB."
        )

    suffix = Path(uploaded_file.name).suffix.lower()
    stored_name = f"{message_id}_{Path(uploaded_file.name).name}"

    # Keep a local copy for compatibility with older versions.
    (ATTACHMENTS_DIR / stored_name).write_bytes(data)

    mime_type = (
        uploaded_file.type
        or mimetypes.guess_type(uploaded_file.name)[0]
        or "application/octet-stream"
    )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO staff_message_attachments
        (
            message_id,
            original_name,
            stored_name,
            mime_type,
            file_size,
            uploaded_by,
            file_data
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        message_id,
        uploaded_file.name,
        stored_name,
        mime_type,
        len(data),
        admin_id,
        sqlite3.Binary(data),
    ))

    connection.commit()
    connection.close()


def show_staff_message_attachments(message_id, viewer_id):
    """Display attachments only to the sender or recipient."""
    connection = get_connection()

    rows = connection.execute("""
        SELECT
            a.id,
            a.original_name,
            a.stored_name,
            a.mime_type,
            a.file_size,
            a.file_data
        FROM staff_message_attachments AS a
        JOIN staff_messages AS m
          ON a.message_id = m.id
        WHERE a.message_id = ?
          AND (m.sender_id = ? OR m.recipient_id = ?)
        ORDER BY a.id
    """, (message_id, viewer_id, viewer_id)).fetchall()

    connection.close()

    if not rows:
        return

    st.markdown("**📎 Attachments**")

    for attachment in rows:
        data = attachment["file_data"]

        # Compatibility with attachments created before the BLOB fix.
        if data is None:
            path = ATTACHMENTS_DIR / attachment["stored_name"]
            if path.exists():
                data = path.read_bytes()

                # Repair the database record so the attachment becomes
                # portable and can be retrieved by the other side.
                repair_connection = get_connection()
                repair_connection.execute("""
                    UPDATE staff_message_attachments
                    SET file_data = ?
                    WHERE id = ?
                """, (sqlite3.Binary(data), attachment["id"]))
                repair_connection.commit()
                repair_connection.close()

        if data is None:
            st.warning(
                f"Attachment unavailable: {attachment['original_name']}"
            )
            continue

        size_kb = attachment["file_size"] / 1024

        st.download_button(
            label=(
                f"📎 {attachment['original_name']} "
                f"({size_kb:.1f} KB)"
            ),
            data=bytes(data),
            file_name=attachment["original_name"],
            mime=attachment["mime_type"] or "application/octet-stream",
            key=f"admin_attachment_{message_id}_{attachment['id']}",
            use_container_width=True,
        )


def show_admin_staff_messages():
    """
    Complete staff messaging centre for the Super Admin.

    The Admin Centre authentication remains separate, but messages are
    recorded using the real 'admin' staff account. Therefore employees
    receive Admin messages in exactly the same Staff Portal inbox.
    """
    ensure_staff_messaging_tables()

    admin_id = get_admin_staff_id()

    if not admin_id:
        st.error(
            "The active Super Admin account was not found in the staff database."
        )
        return

    active_staff = get_active_staff_for_admin()

    st.subheader("✉️ Staff Messages")
    st.caption(
        "Private internal communication between the Super Admin and employees. "
        "Attachments are restricted to the sender and recipient."
    )

    inbox_tab, compose_tab, sent_tab = st.tabs([
        "📥 Admin Inbox",
        "📝 Compose Message",
        "📤 Sent Messages",
    ])

    # ========================================================
    # ADMIN INBOX
    # ========================================================
    with inbox_tab:
        connection = get_connection()

        messages = connection.execute("""
            SELECT
                m.*,
                s.full_name AS sender_name,
                s.username AS sender_username,
                s.role AS sender_role
            FROM staff_messages AS m
            JOIN staff_users AS s
              ON m.sender_id = s.id
            WHERE m.recipient_id = ?
            ORDER BY m.created_at DESC
        """, (admin_id,)).fetchall()

        connection.close()

        unread = sum(
            1 for row in messages
            if row["is_read"] == 0
        )

        st.metric("✉️ Unread Staff Messages", unread)

        if not messages:
            st.info("Your staff inbox is currently empty.")
        else:
            for message in messages:
                status = (
                    "🔵 Unread"
                    if message["is_read"] == 0
                    else "⚪ Read"
                )

                with st.expander(
                    f"{status} — {message['subject']} — "
                    f"{message['sender_name']} "
                    f"({message['created_at']})"
                ):
                    st.write(
                        f"**From:** {message['sender_name']} "
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

                    show_staff_message_attachments(
                        message["id"],
                        admin_id,
                    )

                    # ------------------------------------------------
                    # DIRECT REPLY FROM ADMIN INBOX
                    # ------------------------------------------------
                    st.divider()

                    with st.form(
                        f"admin_reply_form_{message['id']}",
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
                            key=f"admin_reply_subject_{message['id']}"
                        )

                        reply_text = st.text_area(
                            f"Reply to {message['sender_name']}",
                            placeholder="Write your reply here...",
                            height=150,
                            key=f"admin_reply_text_{message['id']}"
                        )

                        reply_file = st.file_uploader(
                            "📎 Attach file (optional)",
                            type=[
                                "pdf", "doc", "docx", "xls", "xlsx",
                                "ppt", "pptx", "csv", "txt",
                                "jpg", "jpeg", "png", "gif", "webp", "zip"
                            ],
                            key=f"admin_reply_file_{message['id']}"
                        )

                        reply_send = st.form_submit_button(
                            "↩️ Send Reply",
                            use_container_width=True,
                            type="primary"
                        )

                    if reply_send:
                        if not reply_text.strip():
                            st.error("Please write a reply before sending.")
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
                                    admin_id,
                                    message["sender_id"],
                                    reply_subject.strip() or f"Re: {message['subject']}",
                                    reply_text.strip(),
                                )
                            )

                            reply_message_id = cursor.lastrowid
                            connection.commit()
                            connection.close()

                            try:
                                save_admin_attachment(
                                    reply_file,
                                    reply_message_id,
                                    admin_id,
                                )
                            except Exception as exc:
                                st.error(
                                    f"Reply was created, but the attachment "
                                    f"could not be saved: {exc}"
                                )
                                return

                            st.success(
                                "✅ Reply sent successfully."
                                + (
                                    " Attachment securely stored with the reply."
                                    if reply_file else ""
                                )
                            )
                            st.rerun()

                    if message["is_read"] == 0:
                        if st.button(
                            "✅ Mark as Read",
                            key=f"admin_read_{message['id']}",
                        ):
                            connection = get_connection()

                            connection.execute("""
                                UPDATE staff_messages
                                SET
                                    is_read = 1,
                                    read_at = CURRENT_TIMESTAMP
                                WHERE id = ?
                                  AND recipient_id = ?
                            """, (
                                message["id"],
                                admin_id,
                            ))

                            connection.commit()
                            connection.close()

                            st.rerun()

    # ========================================================
    # COMPOSE
    # ========================================================
    with compose_tab:
        if not active_staff:
            st.info(
                "There are currently no other active employees to message."
            )
        else:
            employee_options = {
                f"{employee['full_name']} "
                f"(@{employee['username']}) — {employee['role']}":
                employee["id"]
                for employee in active_staff
            }

            with st.form("admin_staff_compose_form"):
                recipient_label = st.selectbox(
                    "To",
                    list(employee_options.keys()),
                )

                subject = st.text_input(
                    "Subject",
                    placeholder="Enter message subject",
                )

                message = st.text_area(
                    "Message",
                    placeholder="Write your message here...",
                    height=220,
                )

                attachment = st.file_uploader(
                    "📎 Attach file (optional)",
                    type=[
                        "pdf",
                        "doc",
                        "docx",
                        "xls",
                        "xlsx",
                        "ppt",
                        "pptx",
                        "csv",
                        "txt",
                        "jpg",
                        "jpeg",
                        "png",
                        "gif",
                        "webp",
                        "zip",
                    ],
                    key="admin_staff_attachment",
                )

                send = st.form_submit_button(
                    "📨 Send Message",
                    use_container_width=True,
                    type="primary",
                )

            if send:
                if not subject.strip():
                    st.error("Please enter a subject.")
                    return

                if not message.strip():
                    st.error("Please enter a message.")
                    return

                recipient_id = employee_options[recipient_label]

                connection = get_connection()

                cursor = connection.cursor()

                cursor.execute("""
                    INSERT INTO staff_messages
                    (
                        sender_id,
                        recipient_id,
                        subject,
                        message
                    )
                    VALUES (?, ?, ?, ?)
                """, (
                    admin_id,
                    recipient_id,
                    subject.strip(),
                    message.strip(),
                ))

                message_id = cursor.lastrowid

                connection.commit()
                connection.close()

                try:
                    save_admin_attachment(
                        attachment,
                        message_id,
                        admin_id,
                    )
                except Exception:
                    cleanup = get_connection()
                    cleanup.execute(
                        "DELETE FROM staff_messages WHERE id = ?",
                        (message_id,),
                    )
                    cleanup.commit()
                    cleanup.close()
                    raise

                st.success(
                    "✅ Message sent successfully."
                    + (
                        " Attachment securely stored with the message."
                        if attachment
                        else ""
                    )
                )

                st.rerun()

    # ========================================================
    # SENT MESSAGES
    # ========================================================
    with sent_tab:
        connection = get_connection()

        messages = connection.execute("""
            SELECT
                m.*,
                r.full_name AS recipient_name,
                r.username AS recipient_username,
                r.role AS recipient_role
            FROM staff_messages AS m
            JOIN staff_users AS r
              ON m.recipient_id = r.id
            WHERE m.sender_id = ?
            ORDER BY m.created_at DESC
        """, (admin_id,)).fetchall()

        connection.close()

        if not messages:
            st.info(
                "You have not sent any staff messages yet."
            )
        else:
            for message in messages:
                status = (
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
                        f"**To:** {message['recipient_name']} "
                        f"(@{message['recipient_username']})"
                    )
                    st.write(f"**Status:** {status}")
                    st.write(
                        f"**Date:** {message['created_at']}"
                    )

                    st.divider()
                    st.write(message["message"])

                    show_staff_message_attachments(
                        message["id"],
                        admin_id,
                    )
