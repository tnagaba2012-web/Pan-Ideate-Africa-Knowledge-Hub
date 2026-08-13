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


def get_notifications(user_id, unread_only=False, limit=100):
    if not user_id:
        return []

    init_notification_database()

    try:
        limit = max(1, min(int(limit), 200))
    except (TypeError, ValueError):
        limit = 100

    connection = get_notification_connection()

    if unread_only:
        rows = connection.execute("""
            SELECT *
            FROM notifications
            WHERE user_id = ? AND is_read = 0
            ORDER BY created_at DESC, id DESC
            LIMIT ?
        """, (user_id, limit)).fetchall()
    else:
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
    if not notification_id or not user_id:
        return False

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
    if not user_id:
        return 0

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
    if not notification_id or not user_id:
        return False

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
    if not user_id:
        return 0

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
    icons = {
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
    }
    return icons.get(notification_type, "🔔")


def priority_label(priority):
    return {
        "low": "Low",
        "normal": "Normal",
        "high": "High",
        "urgent": "Urgent",
    }.get(priority, "Normal")


def show_notification_centre(user_id):
    if not user_id:
        st.error("Unable to identify the current user.")
        return

    init_notification_database()
    unread_count = get_notification_count(user_id)

    st.subheader("🔔 Notification Centre")

    if unread_count:
        st.info(f"You have {unread_count} unread notification(s).")
    else:
        st.success("✅ You are all caught up.")

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
            deleted = clear_read_notifications(user_id)
            if deleted:
                st.success(f"{deleted} read notification(s) cleared.")
            else:
                st.info("There are no read notifications to clear.")
            st.rerun()

    st.divider()

    notifications = get_notifications(user_id, limit=100)

    if not notifications:
        st.info("No notifications yet.")
        return

    for notification in notifications:
        icon = notification_icon(notification["notification_type"])
        status = "🔵 UNREAD" if notification["is_read"] == 0 else "⚪ Read"

        with st.container(border=True):
            top1, top2 = st.columns([5, 1])

            with top1:
                st.markdown(f"### {icon} {notification['title']}")

            with top2:
                st.caption(status)

            st.write(notification["message"])

            meta1, meta2 = st.columns(2)

            with meta1:
                st.caption(
                    f"Priority: {priority_label(notification['priority'])}"
                )

            with meta2:
                st.caption(f"Received: {notification['created_at']}")

            actions = st.columns(2)

            with actions[0]:
                if notification["is_read"] == 0:
                    if st.button(
                        "✓ Mark as Read",
                        key=f"notification_read_{notification['id']}",
                        use_container_width=True,
                    ):
                        mark_notification_read(
                            notification["id"],
                            user_id,
                        )
                        st.rerun()

            with actions[1]:
                if st.button(
                    "🗑️ Delete",
                    key=f"notification_delete_{notification['id']}",
                    use_container_width=True,
                ):
                    delete_notification(
                        notification["id"],
                        user_id,
                    )
                    st.rerun()


def notify_new_message(recipient_id, sender_name, subject, message_id=None):
    return create_notification(
        recipient_id,
        "New Staff Message",
        f"{sender_name} sent you a new message: {subject}",
        "message",
        "normal",
        message_id,
        "staff_message",
    )


def notify_message_reply(recipient_id, sender_name, subject, message_id=None):
    return create_notification(
        recipient_id,
        "New Message Reply",
        f"{sender_name} replied to your message: {subject}",
        "message_reply",
        "normal",
        message_id,
        "staff_message",
    )


def notify_message_read(sender_id, reader_name, subject, message_id=None):
    return create_notification(
        sender_id,
        "Message Read",
        f"{reader_name} has read your message: {subject}",
        "message_read",
        "low",
        message_id,
        "staff_message",
    )


def notify_attachment(recipient_id, sender_name, filename, message_id=None):
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
