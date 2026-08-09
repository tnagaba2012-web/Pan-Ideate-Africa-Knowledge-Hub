import sqlite3
from pathlib import Path


# ==========================================================
# PAN IDEATE AFRICA DATABASE
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "pan_ideate.db"


def get_connection():
    """
    Create and return a connection to the Pan Ideate Africa database.
    """
    DATA_DIR.mkdir(exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    return connection


def init_db():
    """
    Create all required Admin tables if they do not already exist.
    """

    connection = get_connection()
    cursor = connection.cursor()

    # ======================================================
    # CONTACT MESSAGES
    # ======================================================

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

    # ======================================================
    # DONATION REQUESTS
    # ======================================================

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

    # ======================================================
    # PARTNERSHIP REQUESTS
    # ======================================================

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

    connection.commit()
    connection.close()


# ==========================================================
# CONTACT MESSAGE
# ==========================================================

def save_message(name, organisation, subject, message):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO messages
        (name, organisation, subject, message)
        VALUES (?, ?, ?, ?)
    """, (
        name,
        organisation,
        subject,
        message
    ))

    connection.commit()
    connection.close()


# ==========================================================
# DONATION
# ==========================================================

def save_donation(
    name,
    organisation,
    contribution_type,
    amount,
    contact,
    message
):

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


# ==========================================================
# PARTNERSHIP
# ==========================================================

def save_partnership(
    name,
    organisation,
    contact,
    partnership_type,
    idea
):

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


# ==========================================================
# DATABASE INITIALIZATION
# ==========================================================

if __name__ == "__main__":

    init_db()

    print("======================================")
    print("Pan Ideate Africa database initialized")
    print("======================================")
    print(f"Database location: {DATABASE_PATH}")