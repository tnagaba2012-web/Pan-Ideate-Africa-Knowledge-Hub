import sqlite3
import hashlib
import secrets
from pathlib import Path
from datetime import datetime, timedelta


# ============================================================
# PAN IDEATE AFRICA
# CENTRAL DATABASE
# ============================================================
#
# This is the central database layer for the Pan Ideate Africa
# Knowledge Hub.
#
# It manages:
#
# 1. Contact messages
# 2. Donations
# 3. Partnerships
# 4. Memberships & subscriptions
# 5. Staff accounts
# 6. Internal staff messages
#
# Payment processing is NOT performed here.
# Payment records are stored here for administration.
#
# Staff authentication is also supported through this database.
# ============================================================


# ============================================================
# DATABASE LOCATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "pan_ideate.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create and return a connection to the Pan Ideate Africa
    SQLite database.
    """

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ============================================================
# PASSWORD SECURITY
# ============================================================

def hash_password(password):
    """
    Securely hash a password using PBKDF2-HMAC-SHA256.
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

    Supports:
    - New PBKDF2-SHA256 passwords
    - Older SHA-256 passwords
    """

    if not stored_hash:
        return False

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

    # Compatibility with older SHA-256 passwords
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

def init_db():
    """
    Create all Pan Ideate Africa database tables.
    Existing tables are preserved.
    """

    connection = get_connection()
    cursor = connection.cursor()

    # ========================================================
    # CONTACT MESSAGES
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            organisation TEXT,
            subject TEXT,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'New',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ========================================================
    # DONATIONS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            organisation TEXT,
            contribution_type TEXT,
            amount TEXT,
            contact TEXT,
            message TEXT,
            status TEXT DEFAULT 'New',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ========================================================
    # PARTNERSHIPS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS partnerships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            organisation TEXT,
            contact TEXT,
            partnership_type TEXT,
            idea TEXT,
            status TEXT DEFAULT 'New',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ========================================================
    # MEMBERSHIPS & SUBSCRIPTIONS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            plan TEXT NOT NULL,

            status TEXT DEFAULT 'Pending',
            payment_status TEXT DEFAULT 'Unpaid',

            payment_method TEXT,
            payment_reference TEXT,

            start_date TIMESTAMP,
            expiry_date TIMESTAMP,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ========================================================
    # STAFF USERS
    # ========================================================

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

    # ========================================================
    # INTERNAL STAFF MESSAGES
    # ========================================================

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

    # ========================================================
    # INDEXES
    # ========================================================

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_subscriptions_email
        ON subscriptions(email)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_subscriptions_plan
        ON subscriptions(plan)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_subscriptions_status
        ON subscriptions(status)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_subscriptions_payment_status
        ON subscriptions(payment_status)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_staff_username
        ON staff_users(username)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_staff_status
        ON staff_users(status)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_staff_messages_recipient
        ON staff_messages(recipient_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_staff_messages_sender
        ON staff_messages(sender_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_staff_messages_read
        ON staff_messages(is_read)
    """)

    connection.commit()
    connection.close()


# ============================================================
# INITIAL SUPER ADMIN
# ============================================================

def create_initial_admin():
    """
    Create the first Pan Ideate Africa Super Admin if one
    does not already exist.

    Existing accounts are NOT changed.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM staff_users
        WHERE username = ?
    """, ("admin",))

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
# CONTACT MESSAGES
# ============================================================

def save_message(
    name,
    organisation,
    subject,
    message
):
    """
    Save a contact message.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO messages
        (
            name,
            organisation,
            subject,
            message
        )
        VALUES (?, ?, ?, ?)
    """, (
        name,
        organisation,
        subject,
        message
    ))

    connection.commit()
    connection.close()


# ============================================================
# DONATIONS
# ============================================================

def save_donation(
    name,
    organisation,
    contribution_type,
    amount,
    contact,
    message
):
    """
    Save a donation request.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO donations
        (
            name,
            organisation,
            contribution_type,
            amount,
            contact,
            message
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        name,
        organisation,
        contribution_type,
        amount,
        contact,
        message
    ))

    connection.commit()
    connection.close()


# ============================================================
# PARTNERSHIPS
# ============================================================

def save_partnership(
    name,
    organisation,
    contact,
    partnership_type,
    idea
):
    """
    Save a partnership request.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO partnerships
        (
            name,
            organisation,
            contact,
            partnership_type,
            idea
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        organisation,
        contact,
        partnership_type,
        idea
    ))

    connection.commit()
    connection.close()


# ============================================================
# SUBSCRIPTIONS
# ============================================================

def save_subscription(
    full_name,
    email,
    plan,
    status="Pending",
    payment_status="Unpaid",
    payment_method=None,
    payment_reference=None,
    start_date=None,
    expiry_date=None
):
    """
    Save a membership/subscription record.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO subscriptions
        (
            full_name,
            email,
            plan,
            status,
            payment_status,
            payment_method,
            payment_reference,
            start_date,
            expiry_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        full_name,
        email,
        plan,
        status,
        payment_status,
        payment_method,
        payment_reference,
        start_date,
        expiry_date
    ))

    subscription_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return subscription_id


def get_subscriptions():
    """
    Return all subscriptions.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM subscriptions
        ORDER BY created_at DESC
    """)

    records = cursor.fetchall()

    connection.close()

    return records


def get_subscription(subscription_id):
    """
    Return one subscription.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM subscriptions
        WHERE id = ?
    """, (subscription_id,))

    record = cursor.fetchone()

    connection.close()

    return record


def update_subscription_status(
    subscription_id,
    status
):
    """
    Update subscription status.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE subscriptions
        SET
            status = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        status,
        subscription_id
    ))

    connection.commit()
    connection.close()


def update_payment_status(
    subscription_id,
    payment_status,
    payment_method=None,
    payment_reference=None
):
    """
    Update payment information.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE subscriptions
        SET
            payment_status = ?,
            payment_method = ?,
            payment_reference = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        payment_status,
        payment_method,
        payment_reference,
        subscription_id
    ))

    connection.commit()
    connection.close()


def activate_subscription(
    subscription_id,
    duration_days=30
):
    """
    Activate a subscription and calculate expiry.
    """

    start_date = datetime.now()

    expiry_date = (
        start_date +
        timedelta(days=duration_days)
    )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE subscriptions
        SET
            status = 'Active',
            payment_status = 'Paid',
            start_date = ?,
            expiry_date = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        start_date.isoformat(),
        expiry_date.isoformat(),
        subscription_id
    ))

    connection.commit()
    connection.close()


def expire_old_subscriptions():
    """
    Mark expired subscriptions automatically.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE subscriptions
        SET
            status = 'Expired',
            updated_at = CURRENT_TIMESTAMP
        WHERE
            status = 'Active'
            AND expiry_date IS NOT NULL
            AND expiry_date < CURRENT_TIMESTAMP
    """)

    connection.commit()
    connection.close()


def get_subscription_counts():
    """
    Return subscription statistics.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM subscriptions
    """)
    total = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS active
        FROM subscriptions
        WHERE status = 'Active'
    """)
    active = cursor.fetchone()["active"]

    cursor.execute("""
        SELECT COUNT(*) AS pending
        FROM subscriptions
        WHERE status = 'Pending'
    """)
    pending = cursor.fetchone()["pending"]

    cursor.execute("""
        SELECT COUNT(*) AS expired
        FROM subscriptions
        WHERE status = 'Expired'
    """)
    expired = cursor.fetchone()["expired"]

    cursor.execute("""
        SELECT COUNT(*) AS paid
        FROM subscriptions
        WHERE payment_status = 'Paid'
    """)
    paid = cursor.fetchone()["paid"]

    connection.close()

    return {
        "total": total,
        "active": active,
        "pending": pending,
        "expired": expired,
        "paid": paid
    }


def get_subscriptions_by_email(email):
    """
    Find subscriptions by email.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM subscriptions
        WHERE LOWER(email) = LOWER(?)
        ORDER BY created_at DESC
    """, (email,))

    records = cursor.fetchall()

    connection.close()

    return records


def delete_subscription(subscription_id):
    """
    Delete a subscription.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM subscriptions
        WHERE id = ?
    """, (subscription_id,))

    connection.commit()
    connection.close()


# ============================================================
# STAFF MANAGEMENT
# ============================================================

def add_staff(
    full_name,
    username,
    password,
    role="Staff",
    status="Active"
):
    """
    Create a new staff account.

    Returns:
        staff_id
    """

    full_name = full_name.strip()
    username = username.strip().lower()

    if not full_name:
        raise ValueError("Full name is required.")

    if not username:
        raise ValueError("Username is required.")

    if not password:
        raise ValueError("Password is required.")

    if len(password) < 8:
        raise ValueError(
            "Password must contain at least 8 characters."
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM staff_users
        WHERE LOWER(username) = LOWER(?)
    """, (username,))

    existing = cursor.fetchone()

    if existing:
        connection.close()
        raise ValueError(
            "That username is already in use."
        )

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
        full_name,
        username,
        hash_password(password),
        role,
        status
    ))

    staff_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return staff_id


def get_staff(staff_id):
    """
    Return one staff member.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM staff_users
        WHERE id = ?
    """, (staff_id,))

    staff = cursor.fetchone()

    connection.close()

    return staff


def get_staff_by_username(username):
    """
    Return a staff member by username.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM staff_users
        WHERE LOWER(username) = LOWER(?)
    """, (username.strip(),))

    staff = cursor.fetchone()

    connection.close()

    return staff


def get_all_staff():
    """
    Return all staff members.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            full_name,
            username,
            role,
            status,
            created_at,
            last_login
        FROM staff_users
        ORDER BY
            CASE
                WHEN role = 'Super Admin' THEN 0
                ELSE 1
            END,
            full_name
    """)

    staff = cursor.fetchall()

    connection.close()

    return staff


def get_active_staff():
    """
    Return active staff members.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            full_name,
            username,
            role,
            status,
            created_at,
            last_login
        FROM staff_users
        WHERE status = 'Active'
        ORDER BY full_name
    """)

    staff = cursor.fetchall()

    connection.close()

    return staff


def get_staff_counts():
    """
    Return staff statistics for the Admin Centre.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM staff_users
    """)
    total = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS active
        FROM staff_users
        WHERE status = 'Active'
    """)
    active = cursor.fetchone()["active"]

    cursor.execute("""
        SELECT COUNT(*) AS inactive
        FROM staff_users
        WHERE status != 'Active'
    """)
    inactive = cursor.fetchone()["inactive"]

    cursor.execute("""
        SELECT COUNT(*) AS admins
        FROM staff_users
        WHERE role IN ('Super Admin', 'Admin')
    """)
    admins = cursor.fetchone()["admins"]

    connection.close()

    return {
        "total": total,
        "active": active,
        "inactive": inactive,
        "admins": admins
    }


def update_staff(
    staff_id,
    full_name,
    username,
    role,
    status
):
    """
    Update staff profile information.
    """

    full_name = full_name.strip()
    username = username.strip().lower()

    if not full_name:
        raise ValueError("Full name is required.")

    if not username:
        raise ValueError("Username is required.")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM staff_users
        WHERE LOWER(username) = LOWER(?)
        AND id != ?
    """, (
        username,
        staff_id
    ))

    duplicate = cursor.fetchone()

    if duplicate:
        connection.close()
        raise ValueError(
            "That username is already assigned to another staff member."
        )

    cursor.execute("""
        UPDATE staff_users
        SET
            full_name = ?,
            username = ?,
            role = ?,
            status = ?
        WHERE id = ?
    """, (
        full_name,
        username,
        role,
        status,
        staff_id
    ))

    connection.commit()
    connection.close()


def update_staff_status(
    staff_id,
    status
):
    """
    Activate or deactivate a staff account.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE staff_users
        SET status = ?
        WHERE id = ?
    """, (
        status,
        staff_id
    ))

    connection.commit()
    connection.close()


def update_staff_role(
    staff_id,
    role
):
    """
    Change a staff member's role.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE staff_users
        SET role = ?
        WHERE id = ?
    """, (
        role,
        staff_id
    ))

    connection.commit()
    connection.close()


def reset_staff_password(
    staff_id,
    new_password
):
    """
    Reset a staff member's password.
    """

    if len(new_password) < 8:
        raise ValueError(
            "Password must contain at least 8 characters."
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE staff_users
        SET password_hash = ?
        WHERE id = ?
    """, (
        hash_password(new_password),
        staff_id
    ))

    connection.commit()
    connection.close()


def delete_staff(staff_id):
    """
    Delete a staff account.

    Staff messages belonging to the account are removed first
    so foreign-key restrictions do not cause errors.
    """

    connection = get_connection()
    cursor = connection.cursor()

    # Do not allow deletion of a Super Admin through this
    # basic database function.
    cursor.execute("""
        SELECT role
        FROM staff_users
        WHERE id = ?
    """, (staff_id,))

    staff = cursor.fetchone()

    if not staff:
        connection.close()
        return False

    if staff["role"] == "Super Admin":
        connection.close()
        raise ValueError(
            "The Super Admin account cannot be deleted."
        )

    cursor.execute("""
        DELETE FROM staff_messages
        WHERE sender_id = ?
        OR recipient_id = ?
    """, (
        staff_id,
        staff_id
    ))

    cursor.execute("""
        DELETE FROM staff_users
        WHERE id = ?
    """, (staff_id,))

    connection.commit()
    connection.close()

    return True


# ============================================================
# STAFF AUTHENTICATION
# ============================================================

def authenticate_staff(
    username,
    password
):
    """
    Authenticate an active staff member.

    Returns the staff database row when successful.
    Returns None when authentication fails.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM staff_users
        WHERE LOWER(username) = LOWER(?)
        AND status = 'Active'
    """, (
        username.strip(),
    ))

    staff = cursor.fetchone()

    if not staff:
        connection.close()
        return None

    if not verify_password(
        password,
        staff["password_hash"]
    ):
        connection.close()
        return None

    cursor.execute("""
        UPDATE staff_users
        SET last_login = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        staff["id"],
    ))

    connection.commit()

    # Fetch updated record
    cursor.execute("""
        SELECT *
        FROM staff_users
        WHERE id = ?
    """, (
        staff["id"],
    ))

    updated_staff = cursor.fetchone()

    connection.close()

    return updated_staff


# ============================================================
# STAFF MESSAGING
# ============================================================

def send_staff_message(
    sender_id,
    recipient_id,
    subject,
    message
):
    """
    Send an internal message from one employee to another.
    """

    subject = subject.strip()
    message = message.strip()

    if not subject:
        raise ValueError(
            "Message subject is required."
        )

    if not message:
        raise ValueError(
            "Message body is required."
        )

    if sender_id == recipient_id:
        raise ValueError(
            "You cannot send a message to yourself."
        )

    connection = get_connection()
    cursor = connection.cursor()

    # Confirm sender exists
    cursor.execute("""
        SELECT id
        FROM staff_users
        WHERE id = ?
        AND status = 'Active'
    """, (
        sender_id,
    ))

    sender = cursor.fetchone()

    if not sender:
        connection.close()
        raise ValueError(
            "Sender account is not active."
        )

    # Confirm recipient exists
    cursor.execute("""
        SELECT id
        FROM staff_users
        WHERE id = ?
        AND status = 'Active'
    """, (
        recipient_id,
    ))

    recipient = cursor.fetchone()

    if not recipient:
        connection.close()
        raise ValueError(
            "Recipient account is not active."
        )

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
        sender_id,
        recipient_id,
        subject,
        message
    ))

    message_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return message_id


def get_staff_inbox(
    staff_id
):
    """
    Return all messages received by a staff member.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            messages.*,

            sender.full_name AS sender_name,
            sender.username AS sender_username,
            sender.role AS sender_role

        FROM staff_messages AS messages

        JOIN staff_users AS sender
        ON messages.sender_id = sender.id

        WHERE messages.recipient_id = ?

        ORDER BY messages.created_at DESC
    """, (
        staff_id,
    ))

    messages = cursor.fetchall()

    connection.close()

    return messages


def get_staff_sent_messages(
    staff_id
):
    """
    Return messages sent by a staff member.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            messages.*,

            recipient.full_name AS recipient_name,
            recipient.username AS recipient_username,
            recipient.role AS recipient_role

        FROM staff_messages AS messages

        JOIN staff_users AS recipient
        ON messages.recipient_id = recipient.id

        WHERE messages.sender_id = ?

        ORDER BY messages.created_at DESC
    """, (
        staff_id,
    ))

    messages = cursor.fetchall()

    connection.close()

    return messages


def mark_staff_message_read(
    message_id,
    staff_id
):
    """
    Mark a received message as read.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE staff_messages
        SET
            is_read = 1,
            read_at = CURRENT_TIMESTAMP
        WHERE
            id = ?
            AND recipient_id = ?
    """, (
        message_id,
        staff_id
    ))

    connection.commit()
    connection.close()


def get_unread_staff_messages(
    staff_id
):
    """
    Return unread messages for a staff member.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            messages.*,

            sender.full_name AS sender_name,
            sender.username AS sender_username,
            sender.role AS sender_role

        FROM staff_messages AS messages

        JOIN staff_users AS sender
        ON messages.sender_id = sender.id

        WHERE
            messages.recipient_id = ?
            AND messages.is_read = 0

        ORDER BY messages.created_at DESC
    """, (
        staff_id,
    ))

    messages = cursor.fetchall()

    connection.close()

    return messages


def get_unread_staff_count(
    staff_id
):
    """
    Return the number of unread staff messages.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM staff_messages
        WHERE
            recipient_id = ?
            AND is_read = 0
    """, (
        staff_id,
    ))

    count = cursor.fetchone()["total"]

    connection.close()

    return count


# ============================================================
# ADMIN / DASHBOARD COUNTS
# ============================================================

def get_contact_message_count():
    """
    Return total contact messages.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM messages
    """)

    total = cursor.fetchone()["total"]

    connection.close()

    return total


def get_donation_count():
    """
    Return total donation records.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM donations
    """)

    total = cursor.fetchone()["total"]

    connection.close()

    return total


def get_partnership_count():
    """
    Return total partnership records.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM partnerships
    """)

    total = cursor.fetchone()["total"]

    connection.close()

    return total


# ============================================================
# INITIALIZE DATABASE
# ============================================================

init_db()

create_initial_admin()


# ============================================================
# DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":

    print("==============================================")
    print("Pan Ideate Africa Database")
    print("==============================================")

    print("Database initialized successfully.")

    print(f"Database location:")
    print(DATABASE_PATH)

    print("----------------------------------------------")

    staff_counts = get_staff_counts()

    print(
        f"Total staff: {staff_counts['total']}"
    )

    print(
        f"Active staff: {staff_counts['active']}"
    )

    print(
        f"Inactive staff: {staff_counts['inactive']}"
    )

    print("==============================================")