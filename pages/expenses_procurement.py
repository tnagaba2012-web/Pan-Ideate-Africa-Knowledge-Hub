import sqlite3
from pathlib import Path
from datetime import datetime, date
import csv
import io
import streamlit as st

try:
    from utils.approval_engine import (
        init_approval_engine,
        get_authority_profile,
        get_active_staff as get_active_approval_staff,
        can_review_request,
        is_super_admin,
    )
except Exception:
    init_approval_engine = None
    get_authority_profile = None
    get_active_approval_staff = None
    can_review_request = None
    is_super_admin = None

try:
    from pages.audit_log import log_audit_event as shared_audit_event
except Exception:
    shared_audit_event = None

try:
    from pages.notification_centre import create_notification
except Exception:
    create_notification = None


# ============================================================
# PAN IDEATE AFRICA
# EXPENSES & PROCUREMENT V2 — ADVANCED FINANCE & EXPENDITURE CONTROL
# ============================================================
# Independent V1 module.
# Uses the existing data/pan_ideate.db and staff_users table.
# Creates only its own expense/procurement tables.
#
# V2 FEATURES
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
# - Automatic expenditure ledger
# - Daily / monthly / yearly totals
# - Category expenditure analysis
# - Budget vs actual tracking
# - Actual procurement capture
# - Automatic posting of approved expenses
# - Multi-currency totals (kept separate for accuracy)
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
            project TEXT DEFAULT 'General Operations',
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
            project TEXT DEFAULT 'General Operations',
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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS finance_permissions (
            staff_id INTEGER PRIMARY KEY,
            can_submit_expense INTEGER NOT NULL DEFAULT 1,
            can_submit_procurement INTEGER NOT NULL DEFAULT 1,
            can_review_expenses INTEGER NOT NULL DEFAULT 0,
            can_review_procurement INTEGER NOT NULL DEFAULT 0,
            can_view_reports INTEGER NOT NULL DEFAULT 0,
            can_export_reports INTEGER NOT NULL DEFAULT 0,
            can_manage_suppliers INTEGER NOT NULL DEFAULT 0,
            updated_by INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS finance_suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_name TEXT NOT NULL UNIQUE,
            contact_person TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            category TEXT,
            status TEXT NOT NULL DEFAULT 'Active',
            notes TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    active_people = cur.execute(
        "SELECT id, role FROM staff_users WHERE status = 'Active'"
    ).fetchall()
    for person in active_people:
        reviewer = 1 if person["role"] in APPROVER_ROLES else 0
        cur.execute("""
            INSERT OR IGNORE INTO finance_permissions (
                staff_id, can_submit_expense, can_submit_procurement,
                can_review_expenses, can_review_procurement,
                can_view_reports, can_export_reports, can_manage_suppliers
            ) VALUES (?, 1, 1, ?, ?, ?, ?, ?)
        """, (
            person["id"], reviewer, reviewer,
            1 if person["role"] in {"Super Admin", "Administrator", "Finance"} else 0,
            1 if person["role"] in {"Super Admin", "Administrator", "Finance"} else 0,
            1 if person["role"] in {"Super Admin", "Administrator", "Finance"} else 0,
        ))

    con.commit()

    # ========================================================
    # ADVANCED FINANCE TABLES / MIGRATIONS
    # ========================================================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS finance_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_date TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            category TEXT NOT NULL,
            item_description TEXT NOT NULL,
            quantity REAL DEFAULT 1,
            unit TEXT DEFAULT 'item',
            unit_cost REAL DEFAULT 0,
            amount REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'UGX',
            payment_method TEXT DEFAULT 'Not specified',
            supplier TEXT,
            department TEXT,
            project TEXT,
            staff_id INTEGER,
            source_type TEXT,
            source_id INTEGER,
            receipt_reference TEXT,
            notes TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(source_type, source_id, transaction_type)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS finance_budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            budget_year INTEGER NOT NULL,
            category TEXT NOT NULL,
            budget_amount REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'UGX',
            notes TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(budget_year, category, currency)
        )
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_ledger_date
        ON finance_ledger(transaction_date)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_ledger_category
        ON finance_ledger(category)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_ledger_currency
        ON finance_ledger(currency)
    """)

    # Add actual-purchase fields to the existing procurement table without
    # destroying any existing database/data.
    existing_purchase_cols = {
        row["name"]
        for row in cur.execute("PRAGMA table_info(purchase_requests)").fetchall()
    }
    # Project / cost-centre fields for both ordinary expenses and procurement.
    # Existing databases are migrated safely; no records are deleted.
    expense_cols = {row["name"] for row in cur.execute("PRAGMA table_info(expense_claims)").fetchall()}
    if "project" not in expense_cols:
        cur.execute("ALTER TABLE expense_claims ADD COLUMN project TEXT DEFAULT 'General Operations'")

    purchase_migrations = {
        "project": "ALTER TABLE purchase_requests ADD COLUMN project TEXT DEFAULT 'General Operations'",
        "actual_unit_cost": "ALTER TABLE purchase_requests ADD COLUMN actual_unit_cost REAL",
        "actual_quantity": "ALTER TABLE purchase_requests ADD COLUMN actual_quantity REAL",
        "actual_purchase_date": "ALTER TABLE purchase_requests ADD COLUMN actual_purchase_date TEXT",
        "actual_payment_method": "ALTER TABLE purchase_requests ADD COLUMN actual_payment_method TEXT",
        "actual_receipt_reference": "ALTER TABLE purchase_requests ADD COLUMN actual_receipt_reference TEXT",
        "actual_notes": "ALTER TABLE purchase_requests ADD COLUMN actual_notes TEXT",
    }
    for col, statement in purchase_migrations.items():
        if col not in existing_purchase_cols:
            cur.execute(statement)

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
# ADVANCED FINANCE & PROCUREMENT CONTROLS
# ============================================================

def get_finance_permissions(staff_id):
    init_database()
    con = db()
    row = con.execute(
        "SELECT * FROM finance_permissions WHERE staff_id = ? LIMIT 1",
        (staff_id,),
    ).fetchone()
    con.close()
    return row


def has_finance_permission(staff_id, permission):
    person = get_staff(staff_id)
    if not person or person["status"] != "Active":
        return False
    if person["role"] == "Super Admin":
        return True
    row = get_finance_permissions(staff_id)
    return bool(row and row[permission])


def save_finance_permissions(staff_id, updated_by, values):
    if is_super_admin and not is_super_admin(updated_by):
        return False, "Only the Super Admin can change Finance & Procurement access."
    init_database()
    con = db()
    con.execute("""
        INSERT INTO finance_permissions (
            staff_id, can_submit_expense, can_submit_procurement,
            can_review_expenses, can_review_procurement,
            can_view_reports, can_export_reports, can_manage_suppliers,
            updated_by, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(staff_id) DO UPDATE SET
            can_submit_expense=excluded.can_submit_expense,
            can_submit_procurement=excluded.can_submit_procurement,
            can_review_expenses=excluded.can_review_expenses,
            can_review_procurement=excluded.can_review_procurement,
            can_view_reports=excluded.can_view_reports,
            can_export_reports=excluded.can_export_reports,
            can_manage_suppliers=excluded.can_manage_suppliers,
            updated_by=excluded.updated_by,
            updated_at=CURRENT_TIMESTAMP
    """, (
        staff_id,
        int(values["can_submit_expense"]),
        int(values["can_submit_procurement"]),
        int(values["can_review_expenses"]),
        int(values["can_review_procurement"]),
        int(values["can_view_reports"]),
        int(values["can_export_reports"]),
        int(values["can_manage_suppliers"]),
        updated_by,
    ))
    con.commit()
    con.close()
    return True, "Finance & Procurement permissions saved."


def finance_summary():
    con = db()
    result = {
        "pending_expenses": con.execute(
            "SELECT COUNT(*) FROM expense_claims WHERE status='Pending'"
        ).fetchone()[0],
        "approved_expenses": con.execute(
            "SELECT COALESCE(SUM(amount),0) FROM expense_claims WHERE status='Approved'"
        ).fetchone()[0],
        "pending_procurement": con.execute(
            "SELECT COUNT(*) FROM purchase_requests WHERE status='Pending'"
        ).fetchone()[0],
        "approved_procurement": con.execute(
            "SELECT COALESCE(SUM(quantity*estimated_unit_cost),0) FROM purchase_requests WHERE status='Approved'"
        ).fetchone()[0],
        "rejected_expenses": con.execute(
            "SELECT COUNT(*) FROM expense_claims WHERE status='Rejected'"
        ).fetchone()[0],
        "rejected_procurement": con.execute(
            "SELECT COUNT(*) FROM purchase_requests WHERE status='Rejected'"
        ).fetchone()[0],
        "active_suppliers": con.execute(
            "SELECT COUNT(*) FROM finance_suppliers WHERE status='Active'"
        ).fetchone()[0],
    }
    con.close()
    return result


def supplier_rows(search="", status="All"):
    init_database()
    con = db()
    clauses=[]
    params=[]
    if status != "All":
        clauses.append("status = ?")
        params.append(status)
    if search.strip():
        q=f"%{search.strip()}%"
        clauses.append("(supplier_name LIKE ? OR contact_person LIKE ? OR phone LIKE ? OR email LIKE ? OR category LIKE ?)")
        params.extend([q,q,q,q,q])
    where=" WHERE " + " AND ".join(clauses) if clauses else ""
    rows=con.execute(
        f"SELECT * FROM finance_suppliers{where} ORDER BY supplier_name COLLATE NOCASE",
        params,
    ).fetchall()
    con.close()
    return rows


def save_supplier(supplier_name, contact_person, phone, email, address, category, status, notes, created_by):
    if not supplier_name.strip():
        return False, "Supplier name is required."
    init_database()
    con=db()
    try:
        con.execute("""
            INSERT INTO finance_suppliers
            (supplier_name, contact_person, phone, email, address, category, status, notes, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (supplier_name.strip(), contact_person.strip(), phone.strip(), email.strip(), address.strip(), category.strip(), status, notes.strip(), created_by))
        con.commit()
        con.close()
        return True, "Supplier saved successfully."
    except sqlite3.IntegrityError:
        con.close()
        return False, "A supplier with that name already exists."


def _review_permission(staff_id, source_type, source_id):
    required = "can_review_expenses" if source_type == "expense" else "can_review_procurement"
    if not has_finance_permission(staff_id, required):
        return False, "You have not been granted this review permission."
    if can_review_request:
        return can_review_request(staff_id, source_type, source_id)
    return is_approver(staff_id), ""


def _audit_finance(action, summary, actor_id, severity="INFO", target_type=None, target_id=None):
    try:
        if shared_audit_event:
            actor = get_staff(actor_id)
            return shared_audit_event(
                "Finance & Procurement",
                action,
                summary,
                actor_id=actor_id,
                actor_name=actor["full_name"] if actor else "System",
                actor_role=actor["role"] if actor else None,
                severity=severity,
                target_type=target_type,
                target_id=str(target_id) if target_id is not None else None,
            )
    except Exception:
        pass
    return None


def show_finance_access_control(admin_id):
    if not (is_super_admin and is_super_admin(admin_id)):
        st.error("🔒 Only the Super Admin can assign Finance & Procurement access.")
        return
    if init_approval_engine:
        init_approval_engine()
    st.subheader("🔐 Finance & Procurement Access Control")
    st.caption("The Super Admin can choose exactly which staff members may submit, review, report on, or manage Finance & Procurement.")
    staff = get_active_approval_staff() if get_active_approval_staff else get_active_staff()
    options = {f"{p['full_name']} (@{p['username']}) — {p['role']}": p["id"] for p in staff}
    if not options:
        st.info("No active staff members are available.")
        return
    selected = st.selectbox("Staff Member", list(options), key="finance_permission_staff")
    staff_id = options[selected]
    current = get_finance_permissions(staff_id)
    profile = get_authority_profile(staff_id) if get_authority_profile else None
    with st.form("finance_permission_form"):
        left,right=st.columns(2)
        with left:
            can_submit_expense=st.checkbox("Submit expense claims", value=bool(current["can_submit_expense"]) if current else True)
            can_submit_procurement=st.checkbox("Submit procurement requests", value=bool(current["can_submit_procurement"]) if current else True)
            can_review_expenses=st.checkbox("Review / approve expenses", value=bool(current["can_review_expenses"]) if current else False)
            can_review_procurement=st.checkbox("Review / approve procurement", value=bool(current["can_review_procurement"]) if current else False)
        with right:
            can_view_reports=st.checkbox("View finance reports", value=bool(current["can_view_reports"]) if current else False)
            can_export_reports=st.checkbox("Export finance reports", value=bool(current["can_export_reports"]) if current else False)
            can_manage_suppliers=st.checkbox("Manage suppliers", value=bool(current["can_manage_suppliers"]) if current else False)
            st.markdown("**Approval Authority**")
            if profile:
                st.write(str(profile["authority_level"]))
                expense_limit = "Unlimited" if profile["expense_limit"] == -1 else f"{profile['expense_limit']:,.0f} {profile['expense_currency']}"
                proc_limit = "Unlimited" if profile["procurement_limit"] == -1 else f"{profile['procurement_limit']:,.0f} {profile['procurement_currency']}"
                st.caption(f"Expense approval limit: {expense_limit}")
                st.caption(f"Procurement approval limit: {proc_limit}")
            else:
                st.info("Approval Authority Profile not configured yet.")
        save=st.form_submit_button("💾 Save Finance Permissions", use_container_width=True, type="primary")
    if save:
        ok,msg=save_finance_permissions(staff_id,admin_id,{"can_submit_expense":can_submit_expense,"can_submit_procurement":can_submit_procurement,"can_review_expenses":can_review_expenses,"can_review_procurement":can_review_procurement,"can_view_reports":can_view_reports,"can_export_reports":can_export_reports,"can_manage_suppliers":can_manage_suppliers})
        (st.success if ok else st.error)(msg)
        if ok:
            _audit_finance("PERMISSIONS_UPDATED", f"Finance permissions updated for {selected}", admin_id, "HIGH", "staff", staff_id)
            st.rerun()


def show_suppliers(admin_id):
    if not has_finance_permission(admin_id,"can_manage_suppliers"):
        st.error("🔒 Supplier management permission required.")
        return
    st.subheader("🏢 Supplier Directory")
    st.caption("Maintain a controlled list of suppliers for procurement requests.")
    with st.form("add_supplier_form"):
        c1,c2=st.columns(2)
        name=c1.text_input("Supplier Name")
        contact=c2.text_input("Contact Person")
        c1,c2=st.columns(2)
        phone=c1.text_input("Phone")
        email=c2.text_input("Email")
        address=st.text_input("Address")
        category=st.text_input("Category")
        status=st.selectbox("Status",["Active","Inactive"])
        notes=st.text_area("Notes")
        save=st.form_submit_button("💾 Save Supplier", use_container_width=True)
    if save:
        ok,msg=save_supplier(name,contact,phone,email,address,category,status,notes,admin_id)
        (st.success if ok else st.error)(msg)
        if ok:
            _audit_finance("SUPPLIER_CREATED", f"Supplier created: {name.strip()}", admin_id, "INFO", "supplier", name.strip())
            st.rerun()
    search=st.text_input("🔎 Search suppliers", key="supplier_search")
    status_filter=st.selectbox("Supplier Status",["All","Active","Inactive"],key="supplier_status")
    rows=supplier_rows(search,status_filter)
    st.caption(f"{len(rows)} supplier(s) found")
    for row in rows:
        with st.container(border=True):
            c1,c2=st.columns([3,1])
            c1.markdown(f"### 🏢 {row['supplier_name']}")
            c1.caption(f"{row['contact_person'] or 'No contact'} • {row['phone'] or 'No phone'} • {row['email'] or 'No email'}")
            c2.write(f"**{row['status']}**")
            st.write(f"**Category:** {row['category'] or 'Not specified'}")
            st.caption(row["address"] or "No address recorded")
            if row["notes"]:
                st.caption(f"Notes: {row['notes']}")

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
    project="General Operations",
):
    person = get_staff(staff_id)

    if not person or person["status"] != "Active":
        return False, "Active staff account required."
    if not has_finance_permission(staff_id, "can_submit_expense"):
        return False, "You have not been granted permission to submit expense claims."

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
            project,
            receipt_reference
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        staff_id,
        category,
        amount,
        currency,
        expense_date.isoformat(),
        description.strip(),
        (project or "General Operations").strip(),
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
        f"{category}; {amount:.2f} {currency}; {expense_date}; project={project}",
    )

    notify_approvers(
        "💰 New Expense Claim",
        f"{person['full_name']} submitted an expense claim "
        f"for {amount:,.2f} {currency} ({project}).",
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

    allowed, message = _review_permission(
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
    project="General Operations",
):
    person = get_staff(staff_id)

    if not person or person["status"] != "Active":
        return False, "Active staff account required."
    if not has_finance_permission(staff_id, "can_submit_procurement"):
        return False, "You have not been granted permission to submit procurement requests."

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
            project,
            justification,
            required_by
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        staff_id,
        category,
        item_name.strip(),
        quantity,
        unit.strip() or "item",
        estimated_unit_cost,
        currency,
        supplier.strip(),
        (project or "General Operations").strip(),
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
        f"{item_name.strip()}; project={project}; estimated total "
        f"{total:,.2f} {currency}",
    )

    notify_approvers(
        "🛒 New Purchase Request",
        f"{person['full_name']} requested "
        f"{quantity:g} {unit} of {item_name.strip()} "
        f"for {project} (estimated {total:,.2f} {currency}).",
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

    allowed, message = _review_permission(
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
# ADVANCED FINANCE LEDGER / AUTOMATIC REPORTING
# ============================================================

def ensure_ledger_from_approved_expenses():
    """Automatically post every approved expense to the finance ledger."""
    init_database()
    con = db()
    rows = con.execute("""
        SELECT e.*, s.full_name
        FROM expense_claims e
        LEFT JOIN staff_users s ON s.id = e.staff_id
        WHERE e.status = 'Approved'
          AND NOT EXISTS (
              SELECT 1 FROM finance_ledger l
              WHERE l.source_type = 'expense'
                AND l.source_id = e.id
                AND l.transaction_type = 'Expense'
          )
    """).fetchall()

    for row in rows:
        con.execute("""
            INSERT OR IGNORE INTO finance_ledger (
                transaction_date, transaction_type, category,
                item_description, quantity, unit, unit_cost, amount,
                currency, payment_method, supplier, department, project,
                staff_id, source_type, source_id, receipt_reference, notes,
                created_by
            ) VALUES (?, 'Expense', ?, ?, 1, 'item', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["expense_date"],
            row["category"],
            row["description"],
            row["amount"],
            row["amount"],
            row["currency"],
            "Not specified",
            None,
            None,
            row["project"] if "project" in row.keys() else "General Operations",
            row["staff_id"],
            "expense",
            row["id"],
            row["receipt_reference"],
            f"Automatically posted after approval; submitted by {row['full_name'] or 'staff'}",
            row["reviewed_by"] or row["staff_id"],
        ))
    con.commit()
    con.close()


def record_actual_purchase(
    request_id, admin_id, actual_quantity, actual_unit_cost,
    purchase_date, payment_method, receipt_reference="", notes=""
):
    """Convert an approved procurement request into actual expenditure."""
    if not has_finance_permission(admin_id, "can_review_procurement"):
        return False, "You do not have procurement review permission."

    qty = clean_quantity(actual_quantity)
    unit_cost = clean_amount(actual_unit_cost)
    if qty is None or unit_cost is None:
        return False, "Enter valid actual quantity and actual unit cost."

    con = db()
    request = con.execute("""
        SELECT p.*, s.full_name
        FROM purchase_requests p
        LEFT JOIN staff_users s ON s.id = p.staff_id
        WHERE p.id = ?
        LIMIT 1
    """, (request_id,)).fetchone()

    if not request:
        con.close()
        return False, "Purchase request not found."
    if request["status"] != "Approved":
        con.close()
        return False, "Only approved purchase requests can be recorded as actual purchases."

    already = con.execute("""
        SELECT id FROM finance_ledger
        WHERE source_type='procurement'
          AND source_id=?
          AND transaction_type='Procurement'
        LIMIT 1
    """, (request_id,)).fetchone()
    if already:
        con.close()
        return False, "This purchase has already been recorded in the finance ledger."

    total = round(qty * unit_cost, 2)
    con.execute("""
        UPDATE purchase_requests
        SET actual_quantity=?,
            actual_unit_cost=?,
            actual_purchase_date=?,
            actual_payment_method=?,
            actual_receipt_reference=?,
            actual_notes=?
        WHERE id=?
    """, (
        qty, unit_cost, purchase_date.isoformat(),
        payment_method, receipt_reference.strip(),
        notes.strip(), request_id
    ))

    con.execute("""
        INSERT INTO finance_ledger (
            transaction_date, transaction_type, category,
            item_description, quantity, unit, unit_cost, amount,
            currency, payment_method, supplier, department, project,
            staff_id, source_type, source_id, receipt_reference, notes,
            created_by
        ) VALUES (?, 'Procurement', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        purchase_date.isoformat(),
        request["category"],
        request["item_name"],
        qty,
        request["unit"],
        unit_cost,
        total,
        request["currency"],
        payment_method,
        request["supplier"],
        None,
        None,
        request["staff_id"],
        "procurement",
        request_id,
        receipt_reference.strip(),
        notes.strip(),
        admin_id,
    ))
    con.commit()
    con.close()

    audit(
        "procurement", request_id, request["staff_id"], admin_id,
        "actual_purchase_recorded",
        f"Actual purchase {total:,.2f} {request['currency']}; {purchase_date.isoformat()}"
    )
    _audit_finance(
        "ACTUAL_PURCHASE_RECORDED",
        f"{request['item_name']} — {total:,.2f} {request['currency']}",
        admin_id, "HIGH", "procurement", request_id
    )
    return True, f"Actual purchase recorded: {total:,.2f} {request['currency']}."


def ledger_rows(start_date=None, end_date=None, category="All",
                currency="All", transaction_type="All", search="", project="All"):
    init_database()
    con = db()
    clauses = ["1=1"]
    params = []

    if start_date:
        clauses.append("transaction_date >= ?")
        params.append(start_date.isoformat() if hasattr(start_date, "isoformat") else str(start_date))
    if end_date:
        clauses.append("transaction_date <= ?")
        params.append(end_date.isoformat() if hasattr(end_date, "isoformat") else str(end_date))
    if category != "All":
        clauses.append("category = ?")
        params.append(category)
    if currency != "All":
        clauses.append("currency = ?")
        params.append(currency)
    if transaction_type != "All":
        clauses.append("transaction_type = ?")
        params.append(transaction_type)
    if project != "All":
        clauses.append("COALESCE(project, 'General Operations') = ?")
        params.append(project)
    if search.strip():
        q = f"%{search.strip()}%"
        clauses.append("""
            (item_description LIKE ? OR supplier LIKE ? OR
             receipt_reference LIKE ? OR notes LIKE ?)
        """)
        params.extend([q, q, q, q])

    rows = con.execute(
        f"""
        SELECT l.*, s.full_name
        FROM finance_ledger l
        LEFT JOIN staff_users s ON s.id = l.staff_id
        WHERE {' AND '.join(clauses)}
        ORDER BY transaction_date DESC, id DESC
        """,
        params,
    ).fetchall()
    con.close()
    return rows


def ledger_totals(rows):
    totals = {}
    for row in rows:
        currency = row["currency"]
        totals[currency] = totals.get(currency, 0.0) + float(row["amount"] or 0)
    return totals


def category_totals(rows):
    totals = {}
    for row in rows:
        key = (row["category"], row["currency"])
        totals[key] = totals.get(key, 0.0) + float(row["amount"] or 0)
    return totals


def finance_period_summary(year, month=None):
    """Return automatic totals by currency for a month or whole year."""
    init_database()
    con = db()
    if month:
        start = f"{year:04d}-{month:02d}-01"
        if month == 12:
            end = f"{year + 1:04d}-01-01"
        else:
            end = f"{year:04d}-{month + 1:02d}-01"
        rows = con.execute("""
            SELECT currency, COALESCE(SUM(amount),0) AS total, COUNT(*) AS count
            FROM finance_ledger
            WHERE transaction_date >= ? AND transaction_date < ?
            GROUP BY currency
            ORDER BY currency
        """, (start, end)).fetchall()
    else:
        rows = con.execute("""
            SELECT currency, COALESCE(SUM(amount),0) AS total, COUNT(*) AS count
            FROM finance_ledger
            WHERE transaction_date >= ? AND transaction_date < ?
            GROUP BY currency
            ORDER BY currency
        """, (f"{year:04d}-01-01", f"{year + 1:04d}-01-01")).fetchall()
    con.close()
    return rows


def monthly_totals(year, currency):
    init_database()
    con = db()
    rows = con.execute("""
        SELECT substr(transaction_date,1,7) AS month,
               COALESCE(SUM(amount),0) AS total,
               COUNT(*) AS count
        FROM finance_ledger
        WHERE transaction_date >= ?
          AND transaction_date < ?
          AND currency = ?
        GROUP BY substr(transaction_date,1,7)
        ORDER BY month
    """, (f"{year:04d}-01-01", f"{year + 1:04d}-01-01", currency)).fetchall()
    con.close()
    return rows


def budget_rows(year):
    init_database()
    con = db()
    rows = con.execute("""
        SELECT * FROM finance_budgets
        WHERE budget_year=?
        ORDER BY category, currency
    """, (year,)).fetchall()
    con.close()
    return rows


def save_budget(year, category, amount, currency, notes, created_by):
    amount = clean_amount(amount)
    if amount is None:
        return False, "Enter a valid budget amount greater than zero."
    init_database()
    con = db()
    con.execute("""
        INSERT INTO finance_budgets
            (budget_year, category, budget_amount, currency, notes, created_by)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(budget_year, category, currency)
        DO UPDATE SET
            budget_amount=excluded.budget_amount,
            notes=excluded.notes
    """, (year, category, amount, currency, notes.strip(), created_by))
    con.commit()
    con.close()
    return True, "Budget saved."


def budget_vs_actual(year):
    budgets = budget_rows(year)
    actuals = ledger_rows(
        start_date=date(year, 1, 1),
        end_date=date(year, 12, 31),
    )
    actual_map = category_totals(actuals)
    result = []
    for b in budgets:
        actual = actual_map.get((b["category"], b["currency"]), 0.0)
        budget = float(b["budget_amount"])
        result.append({
            "Category": b["category"],
            "Currency": b["currency"],
            "Budget": budget,
            "Actual": actual,
            "Remaining": budget - actual,
            "Utilization %": round((actual / budget) * 100, 1) if budget else 0,
        })
    return result


def ledger_to_csv(rows):
    fields = [
        "id", "transaction_date", "transaction_type", "category",
        "item_description", "quantity", "unit", "unit_cost", "amount",
        "currency", "payment_method", "supplier", "department", "project",
        "full_name", "receipt_reference", "notes", "created_at",
    ]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(fields)
    for row in rows:
        writer.writerow([row[f] if f in row.keys() else "" for f in fields])
    return output.getvalue().encode("utf-8")


def show_finance_dashboard(admin_id):
    """Full automatic management dashboard for daily/monthly/yearly expenditure."""
    if not has_finance_permission(admin_id, "can_view_reports"):
        st.error("🔒 Finance report permission required.")
        return

    ensure_ledger_from_approved_expenses()
    init_database()

    today = date.today()
    year = st.selectbox(
        "Reporting Year",
        list(range(today.year - 5, today.year + 2)),
        index=5,
        key="finance_report_year",
    )

    st.subheader("📊 Financial Overview")
    year_rows = ledger_rows(
        start_date=date(year, 1, 1),
        end_date=date(year, 12, 31),
    )
    year_totals = ledger_totals(year_rows)

    metric_cols = st.columns(max(1, min(4, len(year_totals) or 1)))
    if year_totals:
        for col, (currency, total) in zip(metric_cols, sorted(year_totals.items())):
            with col:
                st.metric(f"💰 {currency} — Year Total", f"{total:,.0f}")
    else:
        metric_cols[0].metric("💰 Year Total", "0")

    st.caption(
        f"Automatic ledger: {len(year_rows):,} recorded expenditure transaction(s) in {year}."
    )

    tabs = st.tabs([
        "📅 Daily / Ledger",
        "📆 Monthly",
        "📈 Categories",
        "🏗️ Projects",
        "🎯 Budget vs Actual",
    ])

    with tabs[0]:
        st.markdown("### Daily Expenditure Ledger")
        c1, c2, c3 = st.columns(3)
        start = c1.date_input("From", value=date(year, 1, 1), key="ledger_from")
        end = c2.date_input("To", value=min(today, date(year, 12, 31)), key="ledger_to")
        types = c3.selectbox(
            "Type", ["All", "Expense", "Procurement"], key="ledger_type"
        )

        search = st.text_input(
            "🔎 Search item, supplier, receipt or notes",
            key="ledger_search",
        )
        currency = st.selectbox(
            "Currency",
            ["All"] + CURRENCIES,
            key="ledger_currency",
        )
        project_options = ["All", "General Operations"]
        con = db()
        project_rows = con.execute("SELECT DISTINCT COALESCE(project, 'General Operations') FROM finance_ledger ORDER BY 1").fetchall()
        con.close()
        project_options += [r[0] for r in project_rows if r[0] and r[0] not in project_options]
        selected_project = st.selectbox("Project / Cost Centre", project_options, key="ledger_project")

        rows = ledger_rows(
            start_date=start,
            end_date=end,
            currency=currency,
            transaction_type=types,
            search=search,
            project=selected_project,
        )

        totals = ledger_totals(rows)
        if totals:
            cols = st.columns(min(4, len(totals)))
            for col, (cur, total) in zip(cols, sorted(totals.items())):
                col.metric(f"Period total ({cur})", f"{total:,.0f}")
        else:
            st.info("No expenditure recorded for this period.")

        if rows:
            data = [{
                "Date": r["transaction_date"],
                "Type": r["transaction_type"],
                "Category": r["category"],
                "Project / Cost Centre": r["project"] or "General Operations",
                "Item / Purpose": r["item_description"],
                "Qty": r["quantity"],
                "Unit": r["unit"],
                "Unit Cost": r["unit_cost"],
                "Total": r["amount"],
                "Currency": r["currency"],
                "Payment": r["payment_method"],
                "Supplier": r["supplier"] or "",
                "Staff": r["full_name"] or "",
                "Receipt": r["receipt_reference"] or "",
            } for r in rows]
            st.dataframe(data, use_container_width=True, hide_index=True)

            if has_finance_permission(admin_id, "can_export_reports"):
                st.download_button(
                    "⬇️ Export Finance Ledger CSV",
                    data=ledger_to_csv(rows),
                    file_name=f"pan_ideate_finance_ledger_{year}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

    with tabs[1]:
        st.markdown("### Monthly Expenditure")
        available_currencies = sorted({r["currency"] for r in year_rows})
        selected_currency = st.selectbox(
            "Currency", available_currencies or CURRENCIES,
            key="monthly_currency",
        )
        monthly = monthly_totals(year, selected_currency)
        if monthly:
            st.dataframe(
                [{
                    "Month": r["month"],
                    "Transactions": r["count"],
                    "Total Expenditure": r["total"],
                    "Currency": selected_currency,
                } for r in monthly],
                use_container_width=True,
                hide_index=True,
            )
            st.bar_chart(
                {r["month"]: r["total"] for r in monthly},
                x_label="Month",
                y_label=f"Expenditure ({selected_currency})",
            )
        else:
            st.info(f"No {selected_currency} expenditure recorded in {year}.")

    with tabs[2]:
        st.markdown("### Expenditure by Category")
        cat = category_totals(year_rows)
        if cat:
            category_data = [
                {
                    "Category": category,
                    "Currency": currency,
                    "Total": total,
                }
                for (category, currency), total in sorted(cat.items())
            ]
            st.dataframe(
                category_data,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No category expenditure data available.")

    with tabs[3]:
        st.markdown("### 🏗️ Project & Cost Centre Expenditure")
        st.caption("See how much has actually been spent on each project and on general company operations.")
        project_rows = ledger_rows(start_date=date(year, 1, 1), end_date=date(year, 12, 31))
        totals = {}
        for r in project_rows:
            key = (r["project"] or "General Operations", r["currency"])
            totals[key] = totals.get(key, 0.0) + float(r["amount"] or 0)
        if totals:
            st.dataframe([
                {"Project / Cost Centre": k[0], "Currency": k[1], "Actual Expenditure": v}
                for k, v in sorted(totals.items())
            ], use_container_width=True, hide_index=True)
        else:
            st.info("No project expenditure has been recorded yet.")

    with tabs[4]:
        st.markdown("### 🎯 Budget vs Actual")
        st.caption(
            "Set annual budgets by category. Actuals are calculated automatically from the finance ledger."
        )
        if has_finance_permission(admin_id, "can_review_expenses"):
            with st.form("finance_budget_form"):
                c1, c2, c3 = st.columns(3)
                budget_category = c1.selectbox(
                    "Category",
                    sorted(set(EXPENSE_CATEGORIES + PROCUREMENT_CATEGORIES)),
                    key="budget_category",
                )
                budget_currency = c2.selectbox(
                    "Currency", CURRENCIES, key="budget_currency",
                )
                budget_amount = c3.number_input(
                    "Annual Budget",
                    min_value=0.0,
                    step=100000.0,
                    format="%.2f",
                    key="budget_amount",
                )
                budget_notes = st.text_input("Budget Notes", key="budget_notes")
                save = st.form_submit_button(
                    "💾 Save / Update Budget",
                    use_container_width=True,
                )
            if save:
                ok, msg = save_budget(
                    year, budget_category, budget_amount,
                    budget_currency, budget_notes, admin_id
                )
                (st.success if ok else st.error)(msg)
                if ok:
                    st.rerun()

        budget_data = budget_vs_actual(year)
        if budget_data:
            st.dataframe(
                budget_data,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No annual budgets have been configured yet.")


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
    st.info("💡 Use **General Operations** for ordinary daily running costs. Use a specific project name for project-related expenses and material requests so Finance can automatically report spending by project.")

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

            project = st.text_input(
                "Project / Cost Centre",
                value="General Operations",
                help="Use General Operations for ordinary company running costs, or enter the project this expense supports.",
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
                    project,
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

            project = st.text_input(
                "Project / Cost Centre",
                value="General Operations",
                help="For example: Project A, Iron Oxide Pigments, Biochar, or General Operations.",
                key="procurement_project",
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
                    project,
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
        st.error("🔒 Authorized Administrator / Finance access required.")
        return

    st.title("💰 Finance, Expenditure & Procurement Centre")
    st.caption("Pan Ideate Africa — Automatic Financial Control & Management")
    st.success(f"Signed in as: {admin['full_name']} • {admin['role']}")

    # Automatically synchronize approved expense claims into the expenditure ledger.
    ensure_ledger_from_approved_expenses()
    metrics = finance_metrics()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🟡 Pending Expenses", metrics["pending_expenses"])
    c2.metric("🟡 Pending Purchases", metrics["pending_procurement"])
    c3.metric("🟢 Approved Expenses", f"{metrics['approved_expenses']:,.0f}")
    c4.metric("🟢 Approved Purchases", f"{metrics['approved_procurement']:,.0f}")

    st.divider()

    tab_labels = [
        "📊 Finance Dashboard",
        "💰 Expense Claims",
        "🛒 Procurement",
        "📋 Reports / Export",
    ]
    if admin["role"] == "Super Admin":
        tab_labels.extend(["🏢 Suppliers", "🔐 Access Control"])

    tabs = st.tabs(tab_labels)

    # --------------------------------------------------------
    # AUTOMATIC FINANCE DASHBOARD
    # --------------------------------------------------------
    with tabs[0]:
        show_finance_dashboard(admin_id)

    # --------------------------------------------------------
    # EXPENSE REVIEW
    # --------------------------------------------------------
    with tabs[1]:
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
                    f"{icon} #{row['id']} — {row['full_name']} — "
                    f"{row['amount']:,.2f} {row['currency']}"
                ):
                    st.write(f"**Staff:** {row['full_name']} (@{row['username']})")
                    st.write(f"**Category:** {row['category']}")
                    st.write(f"**Amount:** {row['amount']:,.2f} {row['currency']}")
                    st.write(f"**Expense Date:** {row['expense_date']}")
                    st.write(f"**Description:** {row['description']}")
                    if row["receipt_reference"]:
                        st.write(f"**Receipt/Reference:** {row['receipt_reference']}")
                    st.write(f"**Status:** {row['status']}")

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
                                    row["id"], admin_id, "Approved", note
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
                                    row["id"], admin_id, "Rejected", note
                                )
                                (st.success if ok else st.error)(msg)
                                if ok:
                                    st.rerun()

    # --------------------------------------------------------
    # PROCUREMENT REVIEW + ACTUAL PURCHASE
    # --------------------------------------------------------
    with tabs[2]:
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
                estimated_total = row["quantity"] * row["estimated_unit_cost"]
                actual_exists = bool(
                    row["actual_quantity"] is not None
                    if "actual_quantity" in row.keys() else False
                )
                icon = {
                    "Pending": "🟡",
                    "Approved": "🟢",
                    "Rejected": "🔴",
                }.get(row["status"], "⚪")

                with st.expander(
                    f"{icon} #{row['id']} — {row['full_name']} — {row['item_name']}"
                ):
                    st.write(f"**Staff:** {row['full_name']} (@{row['username']})")
                    st.write(f"**Category:** {row['category']}")
                    st.write(f"**Item:** {row['item_name']}")
                    st.write(f"**Quantity:** {row['quantity']:g} {row['unit']}")
                    st.write(
                        f"**Estimated Unit Cost:** "
                        f"{row['estimated_unit_cost']:,.2f} {row['currency']}"
                    )
                    st.write(
                        f"**Estimated Total:** "
                        f"**{estimated_total:,.2f} {row['currency']}**"
                    )
                    if row["supplier"]:
                        st.write(f"**Preferred Supplier:** {row['supplier']}")
                    if row["required_by"]:
                        st.write(f"**Required By:** {row['required_by']}")
                    st.write(f"**Justification:** {row['justification']}")
                    st.write(f"**Status:** {row['status']}")

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
                                    row["id"], admin_id, "Approved", note
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
                                    row["id"], admin_id, "Rejected", note
                                )
                                (st.success if ok else st.error)(msg)
                                if ok:
                                    st.rerun()

                    elif row["status"] == "Approved":
                        st.divider()
                        st.subheader("🧾 Record Actual Purchase")

                        if actual_exists:
                            actual_total = (
                                (row["actual_quantity"] or 0)
                                * (row["actual_unit_cost"] or 0)
                            )
                            st.success(
                                f"Recorded in Finance Ledger: "
                                f"{actual_total:,.2f} {row['currency']} "
                                f"on {row['actual_purchase_date']}"
                            )
                            if row["actual_receipt_reference"]:
                                st.caption(
                                    f"Receipt: {row['actual_receipt_reference']}"
                                )
                        else:
                            with st.form(f"actual_purchase_{row['id']}"):
                                a, b, c = st.columns(3)
                                actual_qty = a.number_input(
                                    "Actual Quantity",
                                    min_value=0.001,
                                    value=float(row["quantity"]),
                                    step=1.0,
                                )
                                actual_unit = b.number_input(
                                    "Actual Unit Cost",
                                    min_value=0.0,
                                    value=float(row["estimated_unit_cost"]),
                                    step=1000.0,
                                    format="%.2f",
                                )
                                purchase_date = c.date_input(
                                    "Purchase Date",
                                    value=date.today(),
                                    max_value=date.today(),
                                )
                                payment_method = st.selectbox(
                                    "Payment Method",
                                    [
                                        "Cash",
                                        "Bank Transfer",
                                        "Mobile Money",
                                        "Card",
                                        "Cheque",
                                        "Other",
                                    ],
                                    key=f"payment_method_{row['id']}",
                                )
                                receipt = st.text_input(
                                    "Receipt / Invoice Number",
                                    key=f"actual_receipt_{row['id']}",
                                )
                                notes = st.text_area(
                                    "Purchase Notes",
                                    key=f"actual_notes_{row['id']}",
                                )
                                save_actual = st.form_submit_button(
                                    "💾 Record Actual Purchase & Post to Ledger",
                                    use_container_width=True,
                                    type="primary",
                                )

                            if save_actual:
                                ok, msg = record_actual_purchase(
                                    row["id"],
                                    admin_id,
                                    actual_qty,
                                    actual_unit,
                                    purchase_date,
                                    payment_method,
                                    receipt,
                                    notes,
                                )
                                (st.success if ok else st.error)(msg)
                                if ok:
                                    st.rerun()

    # --------------------------------------------------------
    # REPORTS / EXPORT
    # --------------------------------------------------------
    with tabs[3]:
        st.subheader("📋 Finance Reports & Export")
        ensure_ledger_from_approved_expenses()

        report_year = st.selectbox(
            "Year", list(range(date.today().year - 5, date.today().year + 1)),
            index=5, key="export_report_year"
        )
        rows = ledger_rows(
            start_date=date(report_year, 1, 1),
            end_date=date(report_year, 12, 31),
        )
        totals = ledger_totals(rows)

        if totals:
            st.write("### Automatic Year Totals")
            for cur, total in sorted(totals.items()):
                st.metric(cur, f"{total:,.0f}")

        if rows:
            st.dataframe(
                [{
                    "Date": r["transaction_date"],
                    "Type": r["transaction_type"],
                    "Category": r["category"],
                    "Item / Purpose": r["item_description"],
                    "Amount": r["amount"],
                    "Currency": r["currency"],
                    "Payment": r["payment_method"],
                    "Supplier": r["supplier"] or "",
                    "Receipt": r["receipt_reference"] or "",
                    "Staff": r["full_name"] or "",
                } for r in rows],
                use_container_width=True,
                hide_index=True,
            )

            if has_finance_permission(admin_id, "can_export_reports"):
                st.download_button(
                    "⬇️ Download Complete Finance Ledger",
                    data=ledger_to_csv(rows),
                    file_name=f"pan_ideate_finance_{report_year}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

                st.download_button(
                    "⬇️ Download Expense Claims",
                    data=rows_to_csv(
                        expense_claims(),
                        [
                            "id", "full_name", "category", "amount", "currency",
                            "expense_date", "status", "description",
                            "receipt_reference", "submitted_at",
                            "reviewed_by", "reviewed_at", "review_note",
                        ],
                    ),
                    file_name="pan_ideate_expense_claims.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        else:
            st.info("No finance ledger records available for this year.")

    # --------------------------------------------------------
    # SUPER ADMIN TOOLS
    # --------------------------------------------------------
    if admin["role"] == "Super Admin":
        with tabs[4]:
            show_suppliers(admin_id)
        with tabs[5]:
            show_finance_access_control(admin_id)


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
