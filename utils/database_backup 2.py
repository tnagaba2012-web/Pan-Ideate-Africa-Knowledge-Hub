import sqlite3
from pathlib import Path
from datetime import datetime, timedelta


# ============================================================
# PAN IDEATE AFRICA DATABASE
# ============================================================
# Central database for:
# - Contact messages
# - Donations
# - Partnerships
# - Memberships & Subscriptions
#
# Payment processing is NOT handled here.
# This file stores subscription/payment records only.
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
    Create and return a connection to the Pan Ideate Africa database.
    """

    DATA_DIR.mkdir(exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)

    # Allows rows to be accessed by column name
    connection.row_factory = sqlite3.Row

    # Improve reliability when several operations occur
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_db():
    """
    Create all required Pan Ideate Africa tables if they
    do not already exist.
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
    # DONATION REQUESTS
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
    # PARTNERSHIP REQUESTS
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
    #
    # This is the important new section.
    #
    # It prepares Pan Ideate Africa for:
    # - Free memberships
    # - Student memberships
    # - Professional memberships
    # - Enterprise memberships
    # - Subscription status
    # - Payment status
    # - Expiry dates
    # - Payment references
    # - Future subscription history
    #
    # NO REAL PAYMENT IS PROCESSED HERE.
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
    # SUBSCRIPTION INDEXES
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

    connection.commit()
    connection.close()


# ============================================================
# CONTACT MESSAGES
# ============================================================

def save_message(name, organisation, subject, message):
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
    Save a new membership/subscription request.

    This function does NOT process payments.
    It simply records the subscription information.
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


# ============================================================
# GET SUBSCRIPTIONS
# ============================================================

def get_subscriptions():
    """
    Return all subscription records.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM subscriptions
        ORDER BY created_at DESC
    """)

    subscriptions = cursor.fetchall()

    connection.close()

    return subscriptions


# ============================================================
# GET SUBSCRIPTION BY ID
# ============================================================

def get_subscription(subscription_id):
    """
    Return one subscription using its ID.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM subscriptions
        WHERE id = ?
    """, (subscription_id,))

    subscription = cursor.fetchone()

    connection.close()

    return subscription


# ============================================================
# UPDATE SUBSCRIPTION STATUS
# ============================================================

def update_subscription_status(subscription_id, status):
    """
    Update the membership status.

    Examples:
    - Pending
    - Active
    - Suspended
    - Expired
    - Cancelled
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


# ============================================================
# UPDATE PAYMENT STATUS
# ============================================================

def update_payment_status(
    subscription_id,
    payment_status,
    payment_method=None,
    payment_reference=None
):
    """
    Update payment information.

    Examples:
    - Unpaid
    - Pending
    - Paid
    - Failed
    - Refunded
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


# ============================================================
# ACTIVATE SUBSCRIPTION
# ============================================================

def activate_subscription(
    subscription_id,
    duration_days=30
):
    """
    Activate a subscription and calculate its expiry date.

    Default duration is 30 days.
    """

    start_date = datetime.now()
    expiry_date = start_date + timedelta(days=duration_days)

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


# ============================================================
# EXPIRE OLD SUBSCRIPTIONS
# ============================================================

def expire_old_subscriptions():
    """
    Automatically mark subscriptions as Expired when
    their expiry date has passed.
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


# ============================================================
# SUBSCRIPTION COUNTS
# ============================================================

def get_subscription_counts():
    """
    Return useful subscription statistics for the
    Administration Dashboard.
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


# ============================================================
# FIND SUBSCRIPTIONS BY EMAIL
# ============================================================

def get_subscriptions_by_email(email):
    """
    Find all subscriptions belonging to an email address.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM subscriptions
        WHERE LOWER(email) = LOWER(?)
        ORDER BY created_at DESC
    """, (email,))

    subscriptions = cursor.fetchall()

    connection.close()

    return subscriptions


# ============================================================
# DELETE SUBSCRIPTION
# ============================================================

def delete_subscription(subscription_id):
    """
    Delete a subscription record.

    This should normally be restricted to administrators.
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
# DATABASE INITIALIZATION
# ============================================================

# Initialize automatically when this module is imported.
init_db()


# ============================================================
# DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":

    print("==============================================")
    print("Pan Ideate Africa database initialized")
    print("==============================================")
    print(f"Database location: {DATABASE_PATH}")
    print("==============================================")