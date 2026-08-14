import sqlite3
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "pan_ideate.db"

AUTHORITY_LEVELS = {
    1: "Level 1 — Supervisor / Team Approver",
    2: "Level 2 — Manager / Department Head",
    3: "Level 3 — Administrator",
    4: "Level 4 — Super Admin",
}

REQUEST_LABELS = {
    "leave": "🏖️ Leave",
    "early_signout": "🚪 Early Sign-Out",
    "expense": "💰 Expense",
    "procurement": "🛒 Procurement",
}


def db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def ensure_staff_department():
    con = db()
    try:
        columns = {
            row["name"]
            for row in con.execute("PRAGMA table_info(staff_users)").fetchall()
        }
        if "department" not in columns:
            con.execute(
                "ALTER TABLE staff_users ADD COLUMN department TEXT"
            )
            con.commit()
    except sqlite3.OperationalError:
        pass
    con.close()


def init_approval_engine():
    ensure_staff_department()
    con = db()

    con.execute("""
        CREATE TABLE IF NOT EXISTS approval_authorities (
            staff_id INTEGER PRIMARY KEY,
            authority_level INTEGER NOT NULL DEFAULT 1,
            department TEXT,
            can_access INTEGER NOT NULL DEFAULT 0,
            all_departments INTEGER NOT NULL DEFAULT 0,
            max_leave_days INTEGER NOT NULL DEFAULT 0,
            can_approve_early_exit INTEGER NOT NULL DEFAULT 0,
            expense_limit REAL NOT NULL DEFAULT 0,
            expense_currency TEXT NOT NULL DEFAULT 'UGX',
            procurement_limit REAL NOT NULL DEFAULT 0,
            procurement_currency TEXT NOT NULL DEFAULT 'UGX',
            updated_by INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS approval_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT NOT NULL,
            source_id INTEGER NOT NULL,
            requester_id INTEGER,
            department TEXT,
            approver_id INTEGER NOT NULL,
            authority_level INTEGER NOT NULL,
            decision TEXT NOT NULL,
            note TEXT,
            acted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS approval_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT NOT NULL,
            source_id INTEGER NOT NULL,
            staff_id INTEGER NOT NULL,
            authority_level INTEGER NOT NULL,
            notified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(source_type, source_id, staff_id, authority_level)
        )
    """)

    con.execute("""
        CREATE INDEX IF NOT EXISTS idx_approval_actions_source
        ON approval_actions(source_type, source_id, acted_at)
    """)

    con.execute("""
        CREATE INDEX IF NOT EXISTS idx_approval_authority_level
        ON approval_authorities(authority_level, can_access)
    """)

    # Super Admin always has full approval visibility and authority.
    super_admins = con.execute("""
        SELECT id
        FROM staff_users
        WHERE status = 'Active' AND role = 'Super Admin'
    """).fetchall()

    for person in super_admins:
        con.execute("""
            INSERT OR IGNORE INTO approval_authorities (
                staff_id, authority_level, department, can_access,
                all_departments, max_leave_days,
                can_approve_early_exit, expense_limit, expense_currency,
                procurement_limit, procurement_currency, updated_by
            )
            VALUES (?, 4, '', 1, 1, -1, 1, -1, 'UGX', -1, 'UGX', ?)
        """, (person["id"], person["id"]))

    con.commit()
    con.close()


def get_staff(staff_id):
    init_approval_engine()
    con = db()
    try:
        row = con.execute("""
            SELECT id, full_name, username, role, status, department
            FROM staff_users
            WHERE id = ?
            LIMIT 1
        """, (staff_id,)).fetchone()
    except sqlite3.OperationalError:
        row = None
    con.close()
    return row


def get_active_staff():
    init_approval_engine()
    con = db()
    rows = con.execute("""
        SELECT id, full_name, username, role, status, department
        FROM staff_users
        WHERE status = 'Active'
        ORDER BY full_name COLLATE NOCASE
    """).fetchall()
    con.close()
    return rows


def get_staff_department(staff_id):
    person = get_staff(staff_id)
    if not person:
        return ""
    return (person["department"] or "").strip()


def is_super_admin(staff_id):
    person = get_staff(staff_id)
    return bool(
        person
        and person["status"] == "Active"
        and person["role"] == "Super Admin"
    )


def get_authority_profile(staff_id):
    init_approval_engine()
    con = db()
    row = con.execute("""
        SELECT
            a.*,
            s.full_name,
            s.username,
            s.role,
            s.status
        FROM approval_authorities a
        JOIN staff_users s ON s.id = a.staff_id
        WHERE a.staff_id = ?
        LIMIT 1
    """, (staff_id,)).fetchone()
    con.close()
    return row


def has_approval_access(staff_id):
    if is_super_admin(staff_id):
        return True
    profile = get_authority_profile(staff_id)
    return bool(
        profile
        and profile["can_access"]
        and profile["status"] == "Active"
    )


def save_authority_profile(
    staff_id,
    authority_level,
    department,
    can_access,
    all_departments,
    max_leave_days,
    can_approve_early_exit,
    expense_limit,
    expense_currency,
    procurement_limit,
    procurement_currency,
    updated_by,
):
    if not is_super_admin(updated_by):
        return False, "Only the Super Admin can change approval authority."

    if authority_level not in AUTHORITY_LEVELS:
        return False, "Invalid authority level."

    staff = get_staff(staff_id)
    if not staff or staff["status"] != "Active":
        return False, "The selected staff account is not active."

    if authority_level == 4:
        can_access = True
        all_departments = True
        max_leave_days = -1
        can_approve_early_exit = True
        expense_limit = -1
        procurement_limit = -1

    con = db()
    con.execute("""
        INSERT INTO approval_authorities (
            staff_id, authority_level, department, can_access,
            all_departments, max_leave_days,
            can_approve_early_exit, expense_limit, expense_currency,
            procurement_limit, procurement_currency, updated_by,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(staff_id) DO UPDATE SET
            authority_level = excluded.authority_level,
            department = excluded.department,
            can_access = excluded.can_access,
            all_departments = excluded.all_departments,
            max_leave_days = excluded.max_leave_days,
            can_approve_early_exit = excluded.can_approve_early_exit,
            expense_limit = excluded.expense_limit,
            expense_currency = excluded.expense_currency,
            procurement_limit = excluded.procurement_limit,
            procurement_currency = excluded.procurement_currency,
            updated_by = excluded.updated_by,
            updated_at = CURRENT_TIMESTAMP
    """, (
        staff_id,
        authority_level,
        (department or "").strip(),
        int(bool(can_access)),
        int(bool(all_departments)),
        int(max_leave_days),
        int(bool(can_approve_early_exit)),
        float(expense_limit),
        expense_currency,
        float(procurement_limit),
        procurement_currency,
        updated_by,
    ))
    con.commit()
    con.close()
    return True, "Approval authority saved successfully."


def get_authority_profiles():
    init_approval_engine()
    con = db()
    rows = con.execute("""
        SELECT
            a.*,
            s.full_name,
            s.username,
            s.role,
            s.status
        FROM approval_authorities a
        JOIN staff_users s ON s.id = a.staff_id
        ORDER BY a.authority_level, s.full_name COLLATE NOCASE
    """).fetchall()
    con.close()
    return rows


def _days_between(start_date, end_date):
    try:
        return (date.fromisoformat(end_date) - date.fromisoformat(start_date)).days + 1
    except Exception:
        return None


def get_request_context(source_type, source_id):
    init_approval_engine()
    con = db()

    if source_type == "leave":
        row = con.execute("""
            SELECT l.*, s.full_name, s.department
            FROM leave_requests l
            JOIN staff_users s ON s.id = l.staff_id
            WHERE l.id = ?
            LIMIT 1
        """, (source_id,)).fetchone()

        if not row:
            con.close()
            return None

        ctx = {
            "source_type": "leave",
            "source_id": row["id"],
            "requester_id": row["staff_id"],
            "requester_name": row["full_name"],
            "department": (row["department"] or "").strip(),
            "title": f"Leave request — {row['leave_type']}",
            "details": (
                f"{row['start_date']} → {row['end_date']} • "
                f"{row['reason']}"
            ),
            "submitted_at": row["requested_at"],
            "status": row["status"],
            "leave_days": _days_between(
                row["start_date"], row["end_date"]
            ),
            "amount": None,
            "currency": "",
        }

    elif source_type == "early_signout":
        row = con.execute("""
            SELECT a.*, s.full_name, s.department
            FROM attendance_records a
            JOIN staff_users s ON s.id = a.staff_id
            WHERE a.id = ?
            LIMIT 1
        """, (source_id,)).fetchone()

        if not row:
            con.close()
            return None

        pending = (
            bool(row["early_signout_requested"])
            and not bool(row["early_signout_approved"])
            and not row["sign_out_at"]
        )

        ctx = {
            "source_type": "early_signout",
            "source_id": row["id"],
            "requester_id": row["staff_id"],
            "requester_name": row["full_name"],
            "department": (row["department"] or "").strip(),
            "title": "Early sign-out request",
            "details": (
                f"{row['work_date']} • "
                f"{row['early_signout_reason'] or 'No reason provided'}"
            ),
            "submitted_at": row["early_signout_requested_at"],
            "status": "Pending" if pending else "Closed",
            "leave_days": None,
            "amount": None,
            "currency": "",
        }

    elif source_type == "expense":
        row = con.execute("""
            SELECT e.*, s.full_name, s.department
            FROM expense_claims e
            JOIN staff_users s ON s.id = e.staff_id
            WHERE e.id = ?
            LIMIT 1
        """, (source_id,)).fetchone()

        if not row:
            con.close()
            return None

        ctx = {
            "source_type": "expense",
            "source_id": row["id"],
            "requester_id": row["staff_id"],
            "requester_name": row["full_name"],
            "department": (row["department"] or "").strip(),
            "title": f"Expense claim — {row['category']}",
            "details": f"{row['expense_date']} • {row['description']}",
            "submitted_at": row["submitted_at"],
            "status": row["status"],
            "leave_days": None,
            "amount": float(row["amount"]),
            "currency": row["currency"] or "UGX",
        }

    elif source_type == "procurement":
        row = con.execute("""
            SELECT p.*, s.full_name, s.department
            FROM purchase_requests p
            JOIN staff_users s ON s.id = p.staff_id
            WHERE p.id = ?
            LIMIT 1
        """, (source_id,)).fetchone()

        if not row:
            con.close()
            return None

        total = float(row["quantity"]) * float(row["estimated_unit_cost"])

        ctx = {
            "source_type": "procurement",
            "source_id": row["id"],
            "requester_id": row["staff_id"],
            "requester_name": row["full_name"],
            "department": (row["department"] or "").strip(),
            "title": f"Purchase request — {row['item_name']}",
            "details": (
                f"{row['quantity']:g} {row['unit']} • "
                f"{row['justification']}"
            ),
            "submitted_at": row["submitted_at"],
            "status": row["status"],
            "leave_days": None,
            "amount": total,
            "currency": row["currency"] or "UGX",
        }

    else:
        con.close()
        return None

    con.close()
    return ctx


def get_pending_requests():
    queries = [
        ("leave", "SELECT id FROM leave_requests WHERE status='Pending'"),
        (
            "early_signout",
            """
            SELECT id
            FROM attendance_records
            WHERE early_signout_requested = 1
              AND early_signout_approved = 0
              AND sign_out_at IS NULL
            """,
        ),
        ("expense", "SELECT id FROM expense_claims WHERE status='Pending'"),
        ("procurement", "SELECT id FROM purchase_requests WHERE status='Pending'"),
    ]

    pending = []
    con = db()

    for source_type, query in queries:
        try:
            rows = con.execute(query).fetchall()
        except sqlite3.OperationalError:
            rows = []

        for row in rows:
            ctx = get_request_context(source_type, row["id"])
            if ctx and ctx["status"] == "Pending":
                pending.append(ctx)

    con.close()
    return pending


def _profile_eligible(profile, ctx):
    if not profile["can_access"]:
        return False

    if int(profile["staff_id"]) == int(ctx["requester_id"]):
        return False

    if not profile["all_departments"]:
        profile_dept = (profile["department"] or "").strip().casefold()
        request_dept = (ctx["department"] or "").strip().casefold()
        if not profile_dept or not request_dept or profile_dept != request_dept:
            return False

    source_type = ctx["source_type"]

    if source_type == "leave":
        limit = int(profile["max_leave_days"])
        days = int(ctx["leave_days"] or 0)
        return limit == -1 or (limit > 0 and days <= limit)

    if source_type == "early_signout":
        return bool(profile["can_approve_early_exit"])

    if source_type == "expense":
        limit = float(profile["expense_limit"])
        return (
            limit == -1
            or (
                limit > 0
                and profile["expense_currency"] == ctx["currency"]
                and float(ctx["amount"] or 0) <= limit
            )
        )

    if source_type == "procurement":
        limit = float(profile["procurement_limit"])
        return (
            limit == -1
            or (
                limit > 0
                and profile["procurement_currency"] == ctx["currency"]
                and float(ctx["amount"] or 0) <= limit
            )
        )

    return False


def routing_for_request(ctx):
    init_approval_engine()
    con = db()

    profiles = con.execute("""
        SELECT
            a.*,
            s.full_name,
            s.username,
            s.role,
            s.status
        FROM approval_authorities a
        JOIN staff_users s ON s.id = a.staff_id
        WHERE s.status = 'Active'
          AND a.can_access = 1
        ORDER BY a.authority_level, s.full_name COLLATE NOCASE
    """).fetchall()

    con.close()

    eligible = [
        profile
        for profile in profiles
        if _profile_eligible(profile, ctx)
    ]

    if eligible:
        lowest = min(int(p["authority_level"]) for p in eligible)
        candidates = [
            p for p in eligible
            if int(p["authority_level"]) == lowest
        ]
        return {
            "level": lowest,
            "label": AUTHORITY_LEVELS[lowest],
            "candidates": candidates,
            "fallback": False,
        }

    con = db()
    fallback = con.execute("""
        SELECT id, full_name, username, role
        FROM staff_users
        WHERE status = 'Active'
          AND role = 'Super Admin'
          AND id != ?
        ORDER BY full_name COLLATE NOCASE
    """, (ctx["requester_id"],)).fetchall()
    con.close()

    return {
        "level": 4,
        "label": AUTHORITY_LEVELS[4],
        "candidates": fallback,
        "fallback": True,
    }


def can_review_request(staff_id, source_type, source_id):
    person = get_staff(staff_id)
    if not person or person["status"] != "Active":
        return False, "Active staff account required."

    ctx = get_request_context(source_type, source_id)
    if not ctx:
        return False, "Approval request not found."

    if ctx["status"] != "Pending":
        return False, "This approval request is no longer pending."

    if person["role"] == "Super Admin":
        return True, "Super Admin has full approval visibility and authority."

    routing = routing_for_request(ctx)

    candidate_ids = set()
    for candidate in routing["candidates"]:
        candidate_id = candidate["staff_id"] if "staff_id" in candidate.keys() else candidate["id"]
        candidate_ids.add(int(candidate_id))

    if int(staff_id) in candidate_ids:
        return True, f"Authorized at {routing['label']}."

    return False, (
        f"This request is currently routed to {routing['label']}. "
        "You do not have the authority to act on it."
    )


def record_approval_decision(
    source_type,
    source_id,
    requester_id,
    approver_id,
    decision,
    note="",
):
    ctx = get_request_context(source_type, source_id)
    person = get_staff(approver_id)

    if not ctx or not person:
        return

    if person["role"] == "Super Admin":
        level = 4
    else:
        profile = get_authority_profile(approver_id)
        level = int(profile["authority_level"]) if profile else 0

    con = db()
    con.execute("""
        INSERT INTO approval_actions (
            source_type, source_id, requester_id, department,
            approver_id, authority_level, decision, note
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        source_type,
        source_id,
        requester_id,
        ctx["department"],
        approver_id,
        level,
        decision,
        (note or "").strip(),
    ))
    con.commit()
    con.close()


def has_any_configured_approval_authority(staff_id):
    profile = get_authority_profile(staff_id)
    return bool(
        profile
        and profile["status"] == "Active"
        and profile["can_access"]
    )

def visible_requests_for_user(staff_id):
    """
    Return the pending requests this user is authorized to see.

    Super Admin sees every pending request.
    Other approvers see only requests routed to the lowest eligible
    authority level for their department and thresholds.
    """
    person = get_staff(staff_id)
    if not person or person["status"] != "Active":
        return []

    requests = get_pending_requests()

    if person["role"] == "Super Admin":
        for request in requests:
            request["routing"] = routing_for_request(request)
        return requests

    visible = []

    for request in requests:
        routing = routing_for_request(request)

        candidate_ids = set()
        for candidate in routing["candidates"]:
            candidate_id = (
                candidate["staff_id"]
                if "staff_id" in candidate.keys()
                else candidate["id"]
            )
            candidate_ids.add(int(candidate_id))

        if int(staff_id) in candidate_ids:
            request["routing"] = routing
            visible.append(request)

    return visible


def decision_history(staff_id, all_history=False):
    """
    Return approval decisions.

    Super Admin can request organization-wide history.
    Other users see only decisions they personally made.
    """
    if all_history and not is_super_admin(staff_id):
        all_history = False

    con = db()

    query = """
        SELECT
            a.*,
            requester.full_name AS requester_name,
            approver.full_name AS approver_name,
            approver.role AS approver_role
        FROM approval_actions a
        LEFT JOIN staff_users requester
            ON requester.id = a.requester_id
        LEFT JOIN staff_users approver
            ON approver.id = a.approver_id
    """

    params = []

    if not all_history:
        query += " WHERE a.approver_id = ?"
        params.append(staff_id)

    query += """
        ORDER BY a.acted_at DESC, a.id DESC
        LIMIT 500
    """

    rows = con.execute(query, params).fetchall()
    con.close()
    return rows
