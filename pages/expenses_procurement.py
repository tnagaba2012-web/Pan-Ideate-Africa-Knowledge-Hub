import sqlite3
from pathlib import Path
from datetime import datetime, date
import csv
import io
import streamlit as st

try:
    from pages.notification_centre import create_notification
except Exception:
    create_notification = None


# ============================================================
# PAN IDEATE AFRICA
# EXPENSES & PROCUREMENT V1
# ============================================================
# Independent V1 module.
# Uses the existing data/pan_ideate.db and staff_users table.
# Creates only its own expense/procurement tables.
#
# V1 FEATURES
# - Expense claim submission
# - Purchase request submission
# - Approval / rejection workflow
# - Finance / administrator review
# - Status tracking
# - Staff history
# - Admin dashboard
# - Search and filters
# - Audit trail
# - Notification Centre integration
# - CSV export
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "pan_ideate.db"

APPROVER_ROLES = {"Super Admin", "Administrator", "Manager", "Finance"}

EXPENSE_CATEGORIES = [
    "Transport",
    "Fuel",
    "Accommodation",
    "Meals",
    "Communication",
    "Office Supplies",
    "Training",
    "Field Work",
    "Equipment",
    "Utilities",
    "Other",
]

PROCUREMENT_CATEGORIES = [
    "Office Supplies",
    "Equipment",
    "Laboratory Supplies",
    "Agriculture Supplies",
    "Minerals & Chemistry Supplies",
    "IT & Software",
    "Furniture",
    "Maintenance",
    "Transport",
    "Training",
    "Other",
]

CURRENCIES = ["UGX", "USD", "EUR", "GBP"]


# ============================================================
# DATABASE
# ============================================================

def db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def init_database():
    con = db()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS expense_claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'UGX',
            expense_date TEXT NOT NULL,
            description TEXT NOT NULL,
            receipt_reference TEXT,
            status TEXT NOT NULL DEFAULT 'Pending',
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_by INTEGER,
            reviewed_at TEXT,
            review_note TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS purchase_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            item_name TEXT NOT NULL,
            quantity REAL NOT NULL DEFAULT 1,
            unit TEXT NOT NULL DEFAULT 'item',
            estimated_unit_cost REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'UGX',
            supplier TEXT,
            justification TEXT NOT NULL,
            required_by TEXT,
            status TEXT NOT NULL DEFAULT 'Pending',
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_by INTEGER,
            reviewed_at TEXT,
            review_note TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS finance_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_type TEXT NOT NULL,
            record_id INTEGER NOT NULL,
            staff_id INTEGER,
            actor_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_expense_status
        ON expense_claims(status)
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_expense_staff
        ON expense_claims(staff_id)
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_purchase_status
        ON purchase_requests(status)
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_purchase_staff
        ON purchase_requests(staff_id)
    """)

    con.commit()
    con.close()


# ============================================================
# STAFF / PERMISSIONS
# ============================================================

def get_staff(staff_id):
    if not staff_id:
        return None

    con = db()
    try:
        row = con.execute("""
            SELECT id, full_name, username, role, status
            FROM staff_users
            WHERE id = ?
            LIMIT 1
        """, (staff_id,)).fetchone()
    except sqlite3.OperationalError:
        row = None
    con.close()
    return row


def get_active_staff():
    con = db()
    try:
        rows = con.execute("""
            SELECT id, full_name, username, role, status
            FROM staff_users
            WHERE status = 'Active'
            ORDER BY full_name
        """).fetchall()
    except sqlite3.OperationalError:
        rows = []
    con.close()
    return rows


def is_approver(staff_id):
    person = get_staff(staff_id)
    return bool(
        person
        and person["status"] == "Active"
        and person["role"] in APPROVER_ROLES
    )


def staff_label(person):
    return (
        f"{person['full_name']} (@{person['username']}) "
        f"— {person['role']}"
    )


# ============================================================
# NOTIFICATIONS / AUDIT
# ============================================================

def notify(user_id, title, message, priority="normal",
           related_id=None, related_type="finance"):
    try:
        if create_notification and user_id:
            create_notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type="approval",
                priority=priority,
                related_id=related_id,
                related_type=related_type,
            )
    except Exception:
        pass


def notify_approvers(title, message, priority="normal",
                     related_id=None, related_type="finance"):
    for person in get_active_staff():
        if person["role"] in APPROVER_ROLES:
            notify(
                person["id"],
                title,
                message,
                priority=priority,
                related_id=related_id,
                related_type=related_type,
            )


def audit(record_type, record_id, staff_id, actor_id, action, details=""):
    con = db()
    con.execute("""
        INSERT INTO finance_audit
        (record_type, record_id, staff_id, actor_id, action, details)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        record_type,
        record_id,
        staff_id,
        actor_id,
        action,
        details,
    ))
    con.commit()
    con.close()


# ============================================================
# VALIDATION
# ============================================================

def clean_amount(value):
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return None
    if amount <= 0:
        return None
    return round(amount, 2)


def clean_quantity(value):
    try:
        quantity = float(value)
    except (TypeError, ValueError):
        return None
    if quantity <= 0:
        return None
    return round(quantity, 3)


# ============================================================
# EXPENSE CLAIMS
# ============================================================

def submit_expense(
    staff_id,
    category,
    amount,
    currency,
    expense_date,
    description,
    receipt_reference="",
):
    person = get_staff(staff_id)

    if not person or person["status"] != "Active":
        return False, "Active staff account required."

    amount = clean_amount(amount)
    if amount is None:
        return False, "Enter a valid expense amount greater than zero."

    if not description.strip():
        return False, "Please provide a description."

    if expense_date > date.today():
        return False, "Expense date cannot be in the future."

    con = db()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO expense_claims
        (
            staff_id,
            category,
            amount,
            currency,
            expense_date,
            description,
            receipt_reference
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        staff_id,
        category,
        amount,
        currency,
        expense_date.isoformat(),
        description.strip(),
        receipt_reference.strip(),
    ))
    claim_id = cur.lastrowid
    con.commit()
    con.close()

    audit(
        "expense",
        claim_id,
        staff_id,
        staff_id,
        "submitted",
        f"{category}; {amount:.2f} {currency}; {expense_date}",
    )

    notify_approvers(
        "💰 New Expense Claim",
        f"{person['full_name']} submitted an expense claim "
        f"for {amount:,.2f} {currency}.",
        related_id=claim_id,
        related_type="expense_claim",
    )

    return True, "Expense claim submitted for approval."


def expense_claims(staff_id=None, status=None):
    con = db()

    query = """
        SELECT e.*, s.full_name, s.username, s.role
        FROM expense_claims e
        JOIN staff_users s ON s.id = e.staff_id
        WHERE 1=1
    """
    params = []

    if staff_id:
        query += " AND e.staff_id = ?"
        params.append(staff_id)

    if status and status != "All":
        query += " AND e.status = ?"
        params.append(status)

    query += """
        ORDER BY
            CASE WHEN e.status = 'Pending' THEN 0 ELSE 1 END,
            e.submitted_at DESC,
            e.id DESC
        LIMIT 1000
    """

    rows = con.execute(query, params).fetchall()
    con.close()
    return rows


def review_expense(claim_id, admin_id, decision, note=""):
    from utils.approval_engine import (
        can_review_request,
        record_approval_decision,
    )

    allowed, message = can_review_request(
        admin_id,
        "expense",
        claim_id,
    )
    if not allowed:
        return False, message

    if decision not in {"Approved", "Rejected"}:
        return False, "Invalid decision."

    con = db()
    claim = con.execute("""
        SELECT *
        FROM expense_claims
        WHERE id = ?
        LIMIT 1
    """, (claim_id,)).fetchone()

    if not claim:
        con.close()
        return False, "Expense claim not found."

    if claim["status"] != "Pending":
        con.close()
        return False, "This expense claim has already been reviewed."

    now = datetime.now().isoformat(timespec="seconds")

    con.execute("""
        UPDATE expense_claims
        SET status = ?,
            reviewed_by = ?,
            reviewed_at = ?,
            review_note = ?
        WHERE id = ?
    """, (
        decision,
        admin_id,
        now,
        note.strip(),
        claim_id,
    ))

    con.commit()
    con.close()

    audit(
        "expense",
        claim_id,
        claim["staff_id"],
        admin_id,
        decision.lower(),
        note.strip(),
    )

    notify(
        claim["staff_id"],
        "✅ Expense Claim Approved"
        if decision == "Approved"
        else "❌ Expense Claim Rejected",
        f"Your expense claim of "
        f"{claim['amount']:,.2f} {claim['currency']} "
        f"was {decision.lower()}."
        + (f" Note: {note.strip()}" if note.strip() else ""),
        priority="normal" if decision == "Approved" else "high",
        related_id=claim_id,
        related_type="expense_claim",
    )

    record_approval_decision(
        "expense",
        claim_id,
        claim["staff_id"],
        admin_id,
        decision,
        note,
    )

    return True, f"Expense claim {decision.lower()}."


# ============================================================
# PROCUREMENT
# ============================================================

def submit_purchase_request(
    staff_id,
    category,
    item_name,
    quantity,
    unit,
    estimated_unit_cost,
    currency,
    supplier,
    justification,
    required_by,
):
    person = get_staff(staff_id)

    if not person or person["status"] != "Active":
        return False, "Active staff account required."

    if not item_name.strip():
        return False, "Please enter the item or service required."

    quantity = clean_quantity(quantity)
    if quantity is None:
        return False, "Enter a valid quantity greater than zero."

    estimated_unit_cost = clean_amount(estimated_unit_cost)
    if estimated_unit_cost is None:
        return False, "Enter a valid estimated unit cost greater than zero."

    if not justification.strip():
        return False, "Please provide a business justification."

    con = db()
    cur = con.cursor()

    cur.execute("""
        INSERT INTO purchase_requests
        (
            staff_id,
            category,
            item_name,
            quantity,
            unit,
            estimated_unit_cost,
            currency,
            supplier,
            justification,
            required_by
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        staff_id,
        category,
        item_name.strip(),
        quantity,
        unit.strip() or "item",
        estimated_unit_cost,
        currency,
        supplier.strip(),
        justification.strip(),
        required_by.isoformat() if required_by else None,
    ))

    request_id = cur.lastrowid
    con.commit()
    con.close()

    total = quantity * estimated_unit_cost

    audit(
        "procurement",
        request_id,
        staff_id,
        staff_id,
        "submitted",
        f"{item_name.strip()}; estimated total "
        f"{total:,.2f} {currency}",
    )

    notify_approvers(
        "🛒 New Purchase Request",
        f"{person['full_name']} requested "
        f"{quantity:g} {unit} of {item_name.strip()} "
        f"(estimated {total:,.2f} {currency}).",
        related_id=request_id,
        related_type="purchase_request",
    )

    return True, "Purchase request submitted for approval."


def purchase_requests(staff_id=None, status=None):
    con = db()

    query = """
        SELECT p.*, s.full_name, s.username, s.role
        FROM purchase_requests p
        JOIN staff_users s ON s.id = p.staff_id
        WHERE 1=1
    """
    params = []

    if staff_id:
        query += " AND p.staff_id = ?"
        params.append(staff_id)

    if status and status != "All":
        query += " AND p.status = ?"
        params.append(status)

    query += """
        ORDER BY
            CASE WHEN p.status = 'Pending' THEN 0 ELSE 1 END,
            p.submitted_at DESC,
            p.id DESC
        LIMIT 1000
    """

    rows = con.execute(query, params).fetchall()
    con.close()
    return rows


def review_purchase_request(
    request_id,
    admin_id,
    decision,
    note="",
):
    from utils.approval_engine import (
        can_review_request,
        record_approval_decision,
    )

    allowed, message = can_review_request(
        admin_id,
        "procurement",
        request_id,
    )
    if not allowed:
        return False, message

    if decision not in {"Approved", "Rejected"}:
        return False, "Invalid decision."

    con = db()
    request = con.execute("""
        SELECT *
        FROM purchase_requests
        WHERE id = ?
        LIMIT 1
    """, (request_id,)).fetchone()

    if not request:
        con.close()
        return False, "Purchase request not found."

    if request["status"] != "Pending":
        con.close()
        return False, "This purchase request has already been reviewed."

    now = datetime.now().isoformat(timespec="seconds")

    con.execute("""
        UPDATE purchase_requests
        SET status = ?,
            reviewed_by = ?,
            reviewed_at = ?,
            review_note = ?
        WHERE id = ?
    """, (
        decision,
        admin_id,
        now,
        note.strip(),
        request_id,
    ))

    con.commit()
    con.close()

    total = request["quantity"] * request["estimated_unit_cost"]

    audit(
        "procurement",
        request_id,
        request["staff_id"],
        admin_id,
        decision.lower(),
        f"{request['item_name']}; estimated "
        f"{total:,.2f} {request['currency']}; {note.strip()}",
    )

    notify(
        request["staff_id"],
        "✅ Purchase Request Approved"
        if decision == "Approved"
        else "❌ Purchase Request Rejected",
        f"Your purchase request for "
        f"{request['item_name']} was {decision.lower()}."
        + (f" Note: {note.strip()}" if note.strip() else ""),
        priority="normal" if decision == "Approved" else "high",
        related_id=request_id,
        related_type="purchase_request",
    )

    record_approval_decision(
        "procurement",
        request_id,
        request["staff_id"],
        admin_id,
        decision,
        note,
    )

    return True, f"Purchase request {decision.lower()}."


# ============================================================
# DASHBOARD METRICS
# ============================================================

def finance_metrics():
    con = db()

    pending_expenses = con.execute("""
        SELECT COUNT(*)
        FROM expense_claims
        WHERE status = 'Pending'
    """).fetchone()[0]

    approved_expenses = con.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM expense_claims
        WHERE status = 'Approved'
    """).fetchone()[0]

    pending_procurement = con.execute("""
        SELECT COUNT(*)
        FROM purchase_requests
        WHERE status = 'Pending'
    """).fetchone()[0]

    approved_procurement = con.execute("""
        SELECT COALESCE(
            SUM(quantity * estimated_unit_cost), 0
        )
        FROM purchase_requests
        WHERE status = 'Approved'
    """).fetchone()[0]

    con.close()

    return {
        "pending_expenses": pending_expenses,
        "approved_expenses": approved_expenses,
        "pending_procurement": pending_procurement,
        "approved_procurement": approved_procurement,
    }


# ============================================================
# CSV EXPORT
# ============================================================

def rows_to_csv(rows, fields):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(fields)

    for row in rows:
        writer.writerow([row[field] for field in fields])

    return output.getvalue().encode("utf-8")


# ============================================================
# STAFF INTERFACE
# ============================================================

def show_staff_expenses_procurement(staff_id):
    init_database()

    person = get_staff(staff_id)

    if not person or person["status"] != "Active":
        st.error("Active staff account required.")
        return

    st.title("💰 Expenses & Procurement")
    st.caption(
        "Pan Ideate Africa — Expense Claims & Purchase Requests"
    )
    st.success(
        f"Signed in as: {person['full_name']} • {person['role']}"
    )

    tabs = st.tabs([
        "💰 Submit Expense",
        "🛒 Purchase Request",
        "📋 My Requests",
    ])

    # --------------------------------------------------------
    # EXPENSE SUBMISSION
    # --------------------------------------------------------
    with tabs[0]:
        st.subheader("💰 Submit Expense Claim")

        with st.form("submit_expense_form"):
            category = st.selectbox(
                "Expense Category",
                EXPENSE_CATEGORIES,
            )

            c1, c2 = st.columns(2)

            with c1:
                amount = st.number_input(
                    "Amount",
                    min_value=0.0,
                    step=1000.0,
                    format="%.2f",
                )

            with c2:
                currency = st.selectbox(
                    "Currency",
                    CURRENCIES,
                )

            expense_date = st.date_input(
                "Expense Date",
                value=date.today(),
                max_value=date.today(),
            )

            description = st.text_area(
                "Description / Purpose",
                placeholder=(
                    "Explain what the expense was for "
                    "and how it relates to Pan Ideate Africa work."
                ),
            )

            receipt_reference = st.text_input(
                "Receipt / Reference Number (optional)",
                placeholder="e.g. Receipt 00482",
            )

            submit = st.form_submit_button(
                "📨 Submit Expense Claim",
                use_container_width=True,
                type="primary",
            )

            if submit:
                ok, msg = submit_expense(
                    staff_id,
                    category,
                    amount,
                    currency,
                    expense_date,
                    description,
                    receipt_reference,
                )
                (st.success if ok else st.error)(msg)

                if ok:
                    st.rerun()

    # --------------------------------------------------------
    # PURCHASE REQUEST
    # --------------------------------------------------------
    with tabs[1]:
        st.subheader("🛒 Submit Purchase Request")

        with st.form("submit_purchase_form"):
            category = st.selectbox(
                "Procurement Category",
                PROCUREMENT_CATEGORIES,
            )

            item_name = st.text_input(
                "Item / Service Required",
                placeholder="e.g. Laboratory glassware",
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                quantity = st.number_input(
                    "Quantity",
                    min_value=0.0,
                    value=1.0,
                    step=1.0,
                )

            with c2:
                unit = st.text_input(
                    "Unit",
                    value="item",
                    placeholder="item, box, litre, set...",
                )

            with c3:
                estimated_unit_cost = st.number_input(
                    "Estimated Unit Cost",
                    min_value=0.0,
                    step=1000.0,
                    format="%.2f",
                )

            currency = st.selectbox(
                "Currency",
                CURRENCIES,
                key="procurement_currency",
            )

            supplier = st.text_input(
                "Preferred Supplier (optional)",
            )

            required_by = st.date_input(
                "Required By (optional)",
                value=None,
            )

            justification = st.text_area(
                "Business Justification",
                placeholder=(
                    "Explain why this purchase is needed, "
                    "what activity it supports, and why it is important."
                ),
            )

            submit = st.form_submit_button(
                "📨 Submit Purchase Request",
                use_container_width=True,
                type="primary",
            )

            if submit:
                ok, msg = submit_purchase_request(
                    staff_id,
                    category,
                    item_name,
                    quantity,
                    unit,
                    estimated_unit_cost,
                    currency,
                    supplier,
                    justification,
                    required_by,
                )
                (st.success if ok else st.error)(msg)

                if ok:
                    st.rerun()

    # --------------------------------------------------------
    # STAFF HISTORY
    # --------------------------------------------------------
    with tabs[2]:
        st.subheader("📋 My Expense Claims")

        expense_rows = expense_claims(staff_id=staff_id)

        if not expense_rows:
            st.info("No expense claims submitted yet.")
        else:
            for row in expense_rows:
                with st.container(border=True):
                    st.write(
                        f"**#{row['id']} — {row['category']}**"
                    )
                    st.write(
                        f"{row['amount']:,.2f} {row['currency']} • "
                        f"{row['expense_date']} • "
                        f"**{row['status']}**"
                    )
                    st.write(row["description"])

                    if row["receipt_reference"]:
                        st.caption(
                            f"Receipt/reference: "
                            f"{row['receipt_reference']}"
                        )

                    if row["review_note"]:
                        st.caption(
                            f"Review note: {row['review_note']}"
                        )

        st.divider()
        st.subheader("🛒 My Purchase Requests")

        procurement_rows = purchase_requests(staff_id=staff_id)

        if not procurement_rows:
            st.info("No purchase requests submitted yet.")
        else:
            for row in procurement_rows:
                total = (
                    row["quantity"]
                    * row["estimated_unit_cost"]
                )

                with st.container(border=True):
                    st.write(
                        f"**#{row['id']} — "
                        f"{row['item_name']}**"
                    )
                    st.write(
                        f"{row['quantity']:g} {row['unit']} • "
                        f"Estimated total: "
                        f"**{total:,.2f} {row['currency']}** • "
                        f"**{row['status']}**"
                    )
                    st.write(row["justification"])

                    if row["supplier"]:
                        st.caption(
                            f"Preferred supplier: {row['supplier']}"
                        )

                    if row["required_by"]:
                        st.caption(
                            f"Required by: {row['required_by']}"
                        )

                    if row["review_note"]:
                        st.caption(
                            f"Review note: {row['review_note']}"
                        )


# ============================================================
# ADMIN INTERFACE
# ============================================================

def show_admin_expenses_procurement(admin_id):
    init_database()

    admin = get_staff(admin_id)

    if not admin or not is_approver(admin_id):
        st.error(
            "🔒 Authorized Administrator / Finance access required."
        )
        return

    st.title("💰 Expenses & Procurement")
    st.caption(
        "Pan Ideate Africa — Finance & Procurement Control"
    )
    st.success(
        f"Signed in as: {admin['full_name']} • {admin['role']}"
    )

    metrics = finance_metrics()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "💰 Pending Expenses",
            metrics["pending_expenses"],
        )

    with c2:
        st.metric(
            "🛒 Pending Purchases",
            metrics["pending_procurement"],
        )

    with c3:
        st.metric(
            "✅ Approved Expenses",
            f"{metrics['approved_expenses']:,.0f}",
        )

    with c4:
        st.metric(
            "✅ Approved Purchases",
            f"{metrics['approved_procurement']:,.0f}",
        )

    st.divider()

    tabs = st.tabs([
        "💰 Expense Claims",
        "🛒 Procurement",
        "📊 Reports",
    ])

    # --------------------------------------------------------
    # EXPENSE REVIEW
    # --------------------------------------------------------
    with tabs[0]:
        status_filter = st.selectbox(
            "Expense Status",
            ["All", "Pending", "Approved", "Rejected"],
            key="admin_expense_status",
        )

        rows = expense_claims(status=status_filter)

        if not rows:
            st.info("No expense claims found.")
        else:
            for row in rows:
                icon = {
                    "Pending": "🟡",
                    "Approved": "🟢",
                    "Rejected": "🔴",
                }.get(row["status"], "⚪")

                with st.expander(
                    f"{icon} #{row['id']} — "
                    f"{row['full_name']} — "
                    f"{row['amount']:,.2f} "
                    f"{row['currency']}"
                ):
                    st.write(
                        f"**Staff:** {row['full_name']} "
                        f"(@{row['username']})"
                    )
                    st.write(
                        f"**Category:** {row['category']}"
                    )
                    st.write(
                        f"**Amount:** "
                        f"{row['amount']:,.2f} {row['currency']}"
                    )
                    st.write(
                        f"**Expense Date:** "
                        f"{row['expense_date']}"
                    )
                    st.write(
                        f"**Description:** "
                        f"{row['description']}"
                    )

                    if row["receipt_reference"]:
                        st.write(
                            f"**Receipt/Reference:** "
                            f"{row['receipt_reference']}"
                        )

                    st.write(
                        f"**Status:** {row['status']}"
                    )

                    if row["status"] == "Pending":
                        note = st.text_area(
                            "Review Note",
                            key=f"expense_note_{row['id']}",
                        )

                        a, b = st.columns(2)

                        with a:
                            if st.button(
                                "✅ Approve",
                                key=f"approve_expense_{row['id']}",
                                use_container_width=True,
                            ):
                                ok, msg = review_expense(
                                    row["id"],
                                    admin_id,
                                    "Approved",
                                    note,
                                )
                                (st.success if ok else st.error)(msg)
                                if ok:
                                    st.rerun()

                        with b:
                            if st.button(
                                "❌ Reject",
                                key=f"reject_expense_{row['id']}",
                                use_container_width=True,
                            ):
                                ok, msg = review_expense(
                                    row["id"],
                                    admin_id,
                                    "Rejected",
                                    note,
                                )
                                (st.success if ok else st.error)(msg)
                                if ok:
                                    st.rerun()

    # --------------------------------------------------------
    # PROCUREMENT REVIEW
    # --------------------------------------------------------
    with tabs[1]:
        status_filter = st.selectbox(
            "Procurement Status",
            ["All", "Pending", "Approved", "Rejected"],
            key="admin_procurement_status",
        )

        rows = purchase_requests(status=status_filter)

        if not rows:
            st.info("No purchase requests found.")
        else:
            for row in rows:
                total = (
                    row["quantity"]
                    * row["estimated_unit_cost"]
                )

                icon = {
                    "Pending": "🟡",
                    "Approved": "🟢",
                    "Rejected": "🔴",
                }.get(row["status"], "⚪")

                with st.expander(
                    f"{icon} #{row['id']} — "
                    f"{row['full_name']} — "
                    f"{row['item_name']}"
                ):
                    st.write(
                        f"**Staff:** {row['full_name']} "
                        f"(@{row['username']})"
                    )
                    st.write(
                        f"**Category:** {row['category']}"
                    )
                    st.write(
                        f"**Item:** {row['item_name']}"
                    )
                    st.write(
                        f"**Quantity:** "
                        f"{row['quantity']:g} {row['unit']}"
                    )
                    st.write(
                        f"**Estimated Unit Cost:** "
                        f"{row['estimated_unit_cost']:,.2f} "
                        f"{row['currency']}"
                    )
                    st.write(
                        f"**Estimated Total:** "
                        f"**{total:,.2f} {row['currency']}**"
                    )

                    if row["supplier"]:
                        st.write(
                            f"**Preferred Supplier:** "
                            f"{row['supplier']}"
                        )

                    if row["required_by"]:
                        st.write(
                            f"**Required By:** "
                            f"{row['required_by']}"
                        )

                    st.write(
                        f"**Justification:** "
                        f"{row['justification']}"
                    )

                    st.write(
                        f"**Status:** {row['status']}"
                    )

                    if row["status"] == "Pending":
                        note = st.text_area(
                            "Review Note",
                            key=f"procurement_note_{row['id']}",
                        )

                        a, b = st.columns(2)

                        with a:
                            if st.button(
                                "✅ Approve",
                                key=f"approve_procurement_{row['id']}",
                                use_container_width=True,
                            ):
                                ok, msg = review_purchase_request(
                                    row["id"],
                                    admin_id,
                                    "Approved",
                                    note,
                                )
                                (st.success if ok else st.error)(msg)
                                if ok:
                                    st.rerun()

                        with b:
                            if st.button(
                                "❌ Reject",
                                key=f"reject_procurement_{row['id']}",
                                use_container_width=True,
                            ):
                                ok, msg = review_purchase_request(
                                    row["id"],
                                    admin_id,
                                    "Rejected",
                                    note,
                                )
                                (st.success if ok else st.error)(msg)
                                if ok:
                                    st.rerun()

    # --------------------------------------------------------
    # REPORTS
    # --------------------------------------------------------
    with tabs[2]:
        st.subheader("📊 Expense Report")

        all_expenses = expense_claims()

        if all_expenses:
            expense_data = [{
                "ID": r["id"],
                "Staff": r["full_name"],
                "Category": r["category"],
                "Amount": r["amount"],
                "Currency": r["currency"],
                "Date": r["expense_date"],
                "Status": r["status"],
                "Description": r["description"],
            } for r in all_expenses]

            st.dataframe(
                expense_data,
                use_container_width=True,
                hide_index=True,
            )

            st.download_button(
                "⬇️ Export Expense Claims CSV",
                data=rows_to_csv(
                    all_expenses,
                    [
                        "id",
                        "full_name",
                        "category",
                        "amount",
                        "currency",
                        "expense_date",
                        "status",
                        "description",
                        "receipt_reference",
                        "submitted_at",
                        "reviewed_by",
                        "reviewed_at",
                        "review_note",
                    ],
                ),
                file_name="pan_ideate_expense_claims.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.info("No expense records available.")

        st.divider()
        st.subheader("📊 Procurement Report")

        all_procurement = purchase_requests()

        if all_procurement:
            procurement_data = [{
                "ID": r["id"],
                "Staff": r["full_name"],
                "Category": r["category"],
                "Item": r["item_name"],
                "Quantity": r["quantity"],
                "Unit": r["unit"],
                "Unit Cost": r["estimated_unit_cost"],
                "Currency": r["currency"],
                "Estimated Total": (
                    r["quantity"]
                    * r["estimated_unit_cost"]
                ),
                "Supplier": r["supplier"],
                "Required By": r["required_by"],
                "Status": r["status"],
            } for r in all_procurement]

            st.dataframe(
                procurement_data,
                use_container_width=True,
                hide_index=True,
            )

            st.download_button(
                "⬇️ Export Procurement CSV",
                data=rows_to_csv(
                    all_procurement,
                    [
                        "id",
                        "full_name",
                        "category",
                        "item_name",
                        "quantity",
                        "unit",
                        "estimated_unit_cost",
                        "currency",
                        "supplier",
                        "justification",
                        "required_by",
                        "status",
                        "submitted_at",
                        "reviewed_by",
                        "reviewed_at",
                        "review_note",
                    ],
                ),
                file_name="pan_ideate_procurement_requests.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.info("No procurement records available.")


# ============================================================
# GENERIC ENTRY POINTS
# ============================================================

def show_staff(staff_id):
    show_staff_expenses_procurement(staff_id)


def show_admin(admin_id):
    show_admin_expenses_procurement(admin_id)


def show(user_id=None, admin=False):
    if admin:
        show_admin_expenses_procurement(user_id)
    else:
        show_staff_expenses_procurement(user_id)
