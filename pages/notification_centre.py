
import streamlit as st
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "pan_ideate.db"


def get_notification_connection():
    DATA_DIR.mkdir(exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def init_notification_database():
    connection = get_notification_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            notification_type TEXT NOT NULL DEFAULT 'general',
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'normal',
            related_id INTEGER,
            related_type TEXT,
            is_read INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            read_at TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES staff_users(id)
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_notifications_user
        ON notifications(user_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_notifications_unread
        ON notifications(user_id, is_read)
    """)

    connection.commit()
    connection.close()


def create_notification(
    user_id,
    title,
    message,
    notification_type="general",
    priority="normal",
    related_id=None,
    related_type=None,
):
    if not user_id:
        return None

    title = str(title).strip()
    message = str(message).strip()

    if not title or not message:
        return None

    if priority not in {"low", "normal", "high", "urgent"}:
        priority = "normal"

    init_notification_database()
    connection = get_notification_connection()

    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO notifications
        (user_id, notification_type, title, message, priority,
         related_id, related_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        notification_type,
        title,
        message,
        priority,
        related_id,
        related_type,
    ))

    notification_id = cursor.lastrowid
    connection.commit()
    connection.close()

    return notification_id


def create_notifications(
    user_ids,
    title,
    message,
    notification_type="general",
    priority="normal",
    related_id=None,
    related_type=None,
):
    created = []

    for user_id in user_ids or []:
        notification_id = create_notification(
            user_id,
            title,
            message,
            notification_type,
            priority,
            related_id,
            related_type,
        )
        if notification_id:
            created.append(notification_id)

    return created


def get_notifications(user_id, limit=100):
    if not user_id:
        return []

    init_notification_database()

    try:
        limit = max(1, min(int(limit), 200))
    except (TypeError, ValueError):
        limit = 100

    connection = get_notification_connection()

    rows = connection.execute("""
        SELECT *
        FROM notifications
        WHERE user_id = ?
        ORDER BY created_at DESC, id DESC
        LIMIT ?
    """, (user_id, limit)).fetchall()

    connection.close()
    return rows


def get_notification_count(user_id):
    if not user_id:
        return 0

    init_notification_database()
    connection = get_notification_connection()

    row = connection.execute("""
        SELECT COUNT(*) AS total
        FROM notifications
        WHERE user_id = ? AND is_read = 0
    """, (user_id,)).fetchone()

    connection.close()
    return int(row["total"]) if row else 0


def mark_notification_read(notification_id, user_id):
    init_notification_database()
    connection = get_notification_connection()

    cursor = connection.cursor()
    cursor.execute("""
        UPDATE notifications
        SET is_read = 1, read_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
    """, (notification_id, user_id))

    changed = cursor.rowcount > 0
    connection.commit()
    connection.close()
    return changed


def mark_all_notifications_read(user_id):
    init_notification_database()
    connection = get_notification_connection()

    cursor = connection.cursor()
    cursor.execute("""
        UPDATE notifications
        SET is_read = 1, read_at = CURRENT_TIMESTAMP
        WHERE user_id = ? AND is_read = 0
    """, (user_id,))

    changed = cursor.rowcount
    connection.commit()
    connection.close()
    return changed


def delete_notification(notification_id, user_id):
    init_notification_database()
    connection = get_notification_connection()

    cursor = connection.cursor()
    cursor.execute("""
        DELETE FROM notifications
        WHERE id = ? AND user_id = ?
    """, (notification_id, user_id))

    deleted = cursor.rowcount > 0
    connection.commit()
    connection.close()
    return deleted


def clear_read_notifications(user_id):
    init_notification_database()
    connection = get_notification_connection()

    cursor = connection.cursor()
    cursor.execute("""
        DELETE FROM notifications
        WHERE user_id = ? AND is_read = 1
    """, (user_id,))

    deleted = cursor.rowcount
    connection.commit()
    connection.close()
    return deleted


def notification_icon(notification_type):
    return {
        "message": "✉️",
        "message_reply": "↩️",
        "message_read": "✓✓",
        "attachment": "📎",
        "task": "📋",
        "task_due": "⏰",
        "calendar": "📅",
        "announcement": "📢",
        "approval": "✅",
        "document": "📄",
        "security": "🔐",
        "system": "⚙️",
        "general": "🔔",
    }.get(notification_type, "🔔")


def priority_label(priority):
    return {
        "low": "Low",
        "normal": "Normal",
        "high": "High",
        "urgent": "Urgent",
    }.get(priority, "Normal")


def get_staff_role(user_id):
    connection = get_notification_connection()

    row = connection.execute("""
        SELECT role
        FROM staff_users
        WHERE id = ? AND status = 'Active'
        LIMIT 1
    """, (user_id,)).fetchone()

    connection.close()
    return row["role"] if row else None


def get_active_staff(exclude_user_id=None):
    connection = get_notification_connection()

    if exclude_user_id:
        rows = connection.execute("""
            SELECT id, full_name, username, role
            FROM staff_users
            WHERE status = 'Active' AND id != ?
            ORDER BY full_name
        """, (exclude_user_id,)).fetchall()
    else:
        rows = connection.execute("""
            SELECT id, full_name, username, role
            FROM staff_users
            WHERE status = 'Active'
            ORDER BY full_name
        """).fetchall()

    connection.close()
    return rows


def show_send_notification(user_id):
    """Send authorized internal notifications."""
    role = get_staff_role(user_id)

    if not role:
        st.error("Your staff account could not be identified.")
        return

    staff = get_active_staff(exclude_user_id=user_id)

    if not staff:
        st.info("There are no other active staff members.")
        return

    st.markdown("### 📢 Send Notification")

    if role == "Super Admin":
        mode = st.radio(
            "Recipients",
            [
                "👤 One Employee",
                "👥 Selected Employees",
                "📢 All Active Staff",
            ],
            horizontal=True,
            key="notification_recipient_mode",
        )

        labels = [
            f"{p['full_name']} (@{p['username']}) — {p['role']}"
            for p in staff
        ]

        if mode == "👤 One Employee":
            selected = st.selectbox(
                "Select employee",
                labels,
                key="notification_one_employee",
            )
            recipient_ids = [
                staff[labels.index(selected)]["id"]
            ]

        elif mode == "👥 Selected Employees":
            selected = st.multiselect(
                "Select employees",
                labels,
                key="notification_selected_employees",
            )
            recipient_ids = [
                staff[labels.index(label)]["id"]
                for label in selected
            ]

        else:
            recipient_ids = [p["id"] for p in staff]
            st.info(
                f"Broadcast will reach {len(recipient_ids)} "
                "active employee(s)."
            )

    else:
        labels = [
            f"{p['full_name']} (@{p['username']}) — {p['role']}"
            for p in staff
        ]

        selected = st.selectbox(
            "Send directly to",
            labels,
            key="staff_notification_recipient",
        )

        recipient_ids = [
            staff[labels.index(selected)]["id"]
        ]

        st.caption(
            "Staff can send direct notifications to another colleague. "
            "Organization-wide broadcasts are reserved for Super Admin."
        )

    with st.form("send_notification_form", clear_on_submit=True):
        title = st.text_input(
            "Notification Title",
            placeholder="e.g. Staff Meeting Tomorrow",
        )

        message = st.text_area(
            "Notification Message",
            placeholder="Write the alert or notice...",
            height=140,
        )

        notification_type = st.selectbox(
            "Notification Type",
            [
                ("general", "🔔 General"),
                ("message", "✉️ Message Alert"),
                ("message_reply", "↩️ Reply Alert"),
                ("attachment", "📎 Attachment Alert"),
                ("task", "📋 Task"),
                ("task_due", "⏰ Deadline"),
                ("calendar", "📅 Calendar"),
                ("announcement", "📢 Announcement"),
                ("approval", "✅ Approval"),
                ("document", "📄 Document"),
                ("security", "🔐 Security"),
            ],
            format_func=lambda x: x[1],
        )

        priority = st.selectbox(
            "Priority",
            [
                ("low", "🟢 Low"),
                ("normal", "🔵 Normal"),
                ("high", "🟠 High"),
                ("urgent", "🔴 Urgent"),
            ],
            format_func=lambda x: x[1],
        )

        send = st.form_submit_button(
            "📨 Send Notification",
            use_container_width=True,
            type="primary",
        )

    if send:
        if not recipient_ids:
            st.error("Please select at least one recipient.")
            return

        if not title.strip():
            st.error("Please enter a notification title.")
            return

        if not message.strip():
            st.error("Please enter a notification message.")
            return

        created = create_notifications(
            recipient_ids,
            title.strip(),
            message.strip(),
            notification_type[0],
            priority[0],
            related_type="manual_notification",
        )

        st.success(
            f"✅ Notification sent to {len(created)} recipient(s)."
        )
        st.rerun()


def show_notification_centre(user_id):
    if not user_id:
        st.error("Unable to identify the current user.")
        return

    init_notification_database()
    unread_count = get_notification_count(user_id)

    st.subheader("🔔 Notification Centre")

    if unread_count:
        st.info(
            f"You have {unread_count} unread notification(s)."
        )
    else:
        st.success("✅ You are all caught up.")

    inbox_tab, send_tab = st.tabs([
        "🔔 My Notifications",
        "📢 Send Notification",
    ])

    with inbox_tab:
        col1, col2 = st.columns(2)

        with col1:
            if unread_count and st.button(
                "✓✓ Mark All as Read",
                use_container_width=True,
                key="notification_mark_all_read",
            ):
                mark_all_notifications_read(user_id)
                st.rerun()

        with col2:
            if st.button(
                "🧹 Clear Read Notifications",
                use_container_width=True,
                key="notification_clear_read",
            ):
                clear_read_notifications(user_id)
                st.rerun()

        st.divider()

        notifications = get_notifications(user_id)

        if not notifications:
            st.info("No notifications yet.")
        else:
            for item in notifications:
                icon = notification_icon(
                    item["notification_type"]
                )
                status = (
                    "🔵 UNREAD"
                    if item["is_read"] == 0
                    else "⚪ Read"
                )

                with st.container(border=True):
                    left, right = st.columns([5, 1])

                    with left:
                        st.markdown(
                            f"### {icon} {item['title']}"
                        )

                    with right:
                        st.caption(status)

                    st.write(item["message"])

                    c1, c2 = st.columns(2)

                    with c1:
                        st.caption(
                            f"Priority: "
                            f"{priority_label(item['priority'])}"
                        )

                    with c2:
                        st.caption(
                            f"Received: {item['created_at']}"
                        )

                    a1, a2 = st.columns(2)

                    with a1:
                        if item["is_read"] == 0:
                            if st.button(
                                "✓ Mark as Read",
                                key=f"notification_read_{item['id']}",
                                use_container_width=True,
                            ):
                                mark_notification_read(
                                    item["id"],
                                    user_id,
                                )
                                st.rerun()

                    with a2:
                        if st.button(
                            "🗑️ Delete",
                            key=f"notification_delete_{item['id']}",
                            use_container_width=True,
                        ):
                            delete_notification(
                                item["id"],
                                user_id,
                            )
                            st.rerun()

    with send_tab:
        show_send_notification(user_id)


def notify_new_message(
    recipient_id,
    sender_name,
    subject,
    message_id=None,
):
    return create_notification(
        recipient_id,
        "New Staff Message",
        f"{sender_name} sent you a new message: {subject}",
        "message",
        "normal",
        message_id,
        "staff_message",
    )


def notify_message_reply(
    recipient_id,
    sender_name,
    subject,
    message_id=None,
):
    return create_notification(
        recipient_id,
        "New Message Reply",
        f"{sender_name} replied to your message: {subject}",
        "message_reply",
        "normal",
        message_id,
        "staff_message",
    )


def notify_message_read(
    sender_id,
    reader_name,
    subject,
    message_id=None,
):
    return create_notification(
        sender_id,
        "Message Read",
        f"{reader_name} has read your message: {subject}",
        "message_read",
        "low",
        message_id,
        "staff_message",
    )


def notify_attachment(
    recipient_id,
    sender_name,
    filename,
    message_id=None,
):
    return create_notification(
        recipient_id,
        "Attachment Received",
        f"{sender_name} sent you an attachment: {filename}",
        "attachment",
        "normal",
        message_id,
        "staff_message",
    )


init_notification_database()
