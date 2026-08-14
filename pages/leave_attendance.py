import sqlite3
from pathlib import Path
from datetime import datetime, date, timedelta
import streamlit as st

try:
    from pages.notification_centre import create_notification
except Exception:
    create_notification = None


# ============================================================
# PAN IDEATE AFRICA — LEAVE & ATTENDANCE V1
# ============================================================
# Independent V1 module.
# Uses the existing data/pan_ideate.db and staff_users table.
# Creates only its own attendance/leave tables.
#
# Features:
# - Sign In / Clock In
# - Sign Out / Clock Out
# - Configurable work hours and grace period
# - Late-arrival recording
# - Early sign-out authorization
# - Emergency administrator override
# - Leave requests and approval/rejection
# - Attendance history
# - Admin dashboard
# - Current staff-at-work view
# - Attendance reports + CSV export
# - Attendance/leave audit trail
# - Existing Notification Centre integration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "pan_ideate.db"

DEFAULT_START = "08:00"
DEFAULT_END = "17:00"
DEFAULT_GRACE = 15

LEAVE_TYPES = [
    "Annual Leave", "Sick Leave", "Personal Leave",
    "Maternity Leave", "Paternity Leave", "Emergency Leave",
    "Study / Training Leave", "Other Leave"
]

APPROVER_ROLES = {"Super Admin", "Administrator", "Manager"}


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
        CREATE TABLE IF NOT EXISTS attendance_settings (
            id INTEGER PRIMARY KEY CHECK(id = 1),
            work_start TEXT NOT NULL DEFAULT '08:00',
            work_end TEXT NOT NULL DEFAULT '17:00',
            grace_minutes INTEGER NOT NULL DEFAULT 15,
            early_signout_requires_approval INTEGER NOT NULL DEFAULT 1,
            updated_by INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        INSERT OR IGNORE INTO attendance_settings
        (id, work_start, work_end, grace_minutes,
         early_signout_requires_approval)
        VALUES (1, ?, ?, ?, 1)
    """, (DEFAULT_START, DEFAULT_END, DEFAULT_GRACE))

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER NOT NULL,
            work_date TEXT NOT NULL,
            sign_in_at TEXT,
            sign_out_at TEXT,
            status TEXT NOT NULL DEFAULT 'Present',
            late_minutes INTEGER NOT NULL DEFAULT 0,
            early_signout_requested INTEGER NOT NULL DEFAULT 0,
            early_signout_reason TEXT,
            early_signout_requested_at TEXT,
            early_signout_approved INTEGER NOT NULL DEFAULT 0,
            early_signout_approved_by INTEGER,
            early_signout_approved_at TEXT,
            early_signout_approval_note TEXT,
            hours_worked REAL NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(staff_id, work_date)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER NOT NULL,
            leave_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_by INTEGER,
            reviewed_at TEXT,
            review_note TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER NOT NULL,
            actor_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_attendance_staff_date
        ON attendance_records(staff_id, work_date)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_attendance_date
        ON attendance_records(work_date)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_leave_status
        ON leave_requests(status)
    """)

    con.commit()
    con.close()


# ============================================================
# STAFF / PERMISSION HELPERS
# ============================================================

def get_staff(staff_id):
    if not staff_id:
        return None
    con = db()
    try:
        row = con.execute("""
            SELECT id, full_name, username, role, status
            FROM staff_users WHERE id = ? LIMIT 1
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
        person and person["status"] == "Active"
        and person["role"] in APPROVER_ROLES
    )


def label(person):
    return f"{person['full_name']} (@{person['username']}) — {person['role']}"


# ============================================================
# SETTINGS
# ============================================================

def parse_time(value):
    try:
        return datetime.strptime(str(value), "%H:%M").time()
    except (TypeError, ValueError):
        return datetime.strptime(DEFAULT_START, "%H:%M").time()


def get_settings():
    init_database()
    con = db()
    row = con.execute(
        "SELECT * FROM attendance_settings WHERE id = 1"
    ).fetchone()
    con.close()
    return row


def save_settings(admin_id, start, end, grace, require_approval):
    if not is_approver(admin_id):
        return False, "You are not authorized to change attendance settings."

    start_t, end_t = parse_time(start), parse_time(end)
    if start_t >= end_t:
        return False, "Work end time must be later than start time."

    try:
        grace = max(0, min(int(grace), 240))
    except (TypeError, ValueError):
        return False, "Grace period must be a whole number."

    con = db()
    con.execute("""
        UPDATE attendance_settings
        SET work_start=?, work_end=?, grace_minutes=?,
            early_signout_requires_approval=?,
            updated_by=?, updated_at=CURRENT_TIMESTAMP
        WHERE id=1
    """, (start_t.strftime("%H:%M"), end_t.strftime("%H:%M"),
          grace, int(bool(require_approval)), admin_id))
    con.commit()
    con.close()
    return True, "Attendance settings saved."


# ============================================================
# NOTIFICATIONS / AUDIT
# ============================================================

def notify(user_id, title, message, priority="normal",
           related_id=None, related_type="attendance"):
    try:
        if create_notification and user_id:
            create_notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type="approval",
                priority=priority,
                related_id=related_id,
                related_type=related_type
            )
    except Exception:
        pass


def audit(staff_id, actor_id, action, details=""):
    con = db()
    con.execute("""
        INSERT INTO attendance_audit
        (staff_id, actor_id, action, details)
        VALUES (?, ?, ?, ?)
    """, (staff_id, actor_id, action, details))
    con.commit()
    con.close()


# ============================================================
# ATTENDANCE CORE
# ============================================================

def get_record(staff_id, work_date=None):
    work_date = work_date or date.today().isoformat()
    con = db()
    row = con.execute("""
        SELECT a.*, s.full_name, s.username, s.role
        FROM attendance_records a
        JOIN staff_users s ON s.id = a.staff_id
        WHERE a.staff_id=? AND a.work_date=?
        LIMIT 1
    """, (staff_id, work_date)).fetchone()
    con.close()
    return row


def hours_between(start, end):
    if not start or not end:
        return 0.0
    try:
        a, b = datetime.fromisoformat(start), datetime.fromisoformat(end)
        return round(max(0, (b-a).total_seconds()) / 3600, 2)
    except (TypeError, ValueError):
        return 0.0


def sign_in(staff_id):
    person = get_staff(staff_id)
    if not person or person["status"] != "Active":
        return False, "Active staff account required."

    today = date.today().isoformat()
    leave = approved_leave(staff_id, today)
    if leave:
        return False, f"You are on approved {leave['leave_type']} today."

    existing = get_record(staff_id, today)
    if existing and existing["sign_in_at"]:
        return False, (
            "Today's attendance is already signed in."
            if not existing["sign_out_at"]
            else "Today's attendance has already been completed."
        )

    settings = get_settings()
    now = datetime.now()
    scheduled = datetime.combine(now.date(), parse_time(settings["work_start"]))
    grace_end = scheduled + timedelta(minutes=int(settings["grace_minutes"]))
    late = max(0, int((now - scheduled).total_seconds() // 60)) if now > grace_end else 0
    status = "Late" if late else "Present"

    con = db()
    if existing:
        con.execute("""
            UPDATE attendance_records
            SET sign_in_at=?, status=?, late_minutes=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (now.isoformat(timespec="seconds"), status, late, existing["id"]))
    else:
        con.execute("""
            INSERT INTO attendance_records
            (staff_id, work_date, sign_in_at, status, late_minutes)
            VALUES (?, ?, ?, ?, ?)
        """, (staff_id, today, now.isoformat(timespec="seconds"), status, late))
    con.commit()
    con.close()

    audit(staff_id, staff_id, "sign_in",
          f"Signed in at {now.strftime('%H:%M:%S')}; late minutes={late}.")
    notify(
        staff_id, "🟢 Attendance Recorded",
        f"Your sign-in at {now.strftime('%H:%M')} was recorded as {status}.",
        related_type="attendance"
    )
    return True, (
        f"Signed in at {now.strftime('%H:%M:%S')}."
        + (f" You are {late} minute(s) late." if late else "")
    )


def request_early_signout(staff_id, reason):
    if not reason.strip():
        return False, "Please provide a reason."

    today = date.today().isoformat()
    record = get_record(staff_id, today)
    if not record or not record["sign_in_at"]:
        return False, "You must sign in before requesting early sign-out."
    if record["sign_out_at"]:
        return False, "You have already signed out."

    settings = get_settings()
    now = datetime.now()
    closing = datetime.combine(now.date(), parse_time(settings["work_end"]))

    if now >= closing:
        return sign_out(staff_id, authorized=True)

    con = db()
    con.execute("""
        UPDATE attendance_records
        SET early_signout_requested=1,
            early_signout_reason=?,
            early_signout_requested_at=?,
            status='Pending Early Sign-Out',
            updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (reason.strip(), now.isoformat(timespec="seconds"), record["id"]))
    con.commit()
    con.close()

    person = get_staff(staff_id)
    audit(staff_id, staff_id, "early_signout_requested",
          f"Reason: {reason.strip()}")

    for approver in get_active_staff():
        if approver["role"] in APPROVER_ROLES:
            notify(
                approver["id"], "⏰ Early Sign-Out Authorization",
                f"{person['full_name']} requested to leave early. "
                f"Reason: {reason.strip()}",
                priority="high", related_id=record["id"],
                related_type="early_signout"
            )

    return True, "Early sign-out request sent for authorization."


def sign_out(staff_id, authorized=False, actor_id=None):
    today = date.today().isoformat()
    record = get_record(staff_id, today)
    if not record or not record["sign_in_at"]:
        return False, "You have not signed in today."
    if record["sign_out_at"]:
        return False, "You have already signed out."

    settings = get_settings()
    now = datetime.now()
    closing = datetime.combine(now.date(), parse_time(settings["work_end"]))
    early = now < closing

    if early and settings["early_signout_requires_approval"]:
        if not authorized:
            return False, (
                "Early sign-out requires authorization. "
                "Please submit an early sign-out request."
            )
        if not record["early_signout_approved"]:
            return False, "Your early sign-out has not been authorized."

    hrs = hours_between(record["sign_in_at"], now.isoformat(timespec="seconds"))
    status = "Early Sign-Out" if early else record["status"]

    con = db()
    con.execute("""
        UPDATE attendance_records
        SET sign_out_at=?, status=?, hours_worked=?,
            updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (now.isoformat(timespec="seconds"), status, hrs, record["id"]))
    con.commit()
    con.close()

    audit(staff_id, actor_id or staff_id, "sign_out",
          f"Signed out at {now.strftime('%H:%M:%S')}; hours={hrs:.2f}; early={early}.")
    notify(
        staff_id, "🔴 Attendance Completed",
        f"Signed out at {now.strftime('%H:%M')}. Hours worked: {hrs:.2f}.",
        related_id=record["id"], related_type="attendance"
    )
    return True, f"Signed out at {now.strftime('%H:%M:%S')}. Hours: {hrs:.2f}."


def review_early_signout(attendance_id, admin_id, decision, note=""):
    if not is_approver(admin_id):
        return False, "You are not authorized to review early sign-outs."
    if decision not in {"Approved", "Rejected"}:
        return False, "Invalid decision."

    con = db()
    record = con.execute(
        "SELECT * FROM attendance_records WHERE id=? LIMIT 1",
        (attendance_id,)
    ).fetchone()

    if not record:
        con.close()
        return False, "Attendance request not found."
    if not record["early_signout_requested"] or record["sign_out_at"]:
        con.close()
        return False, "This early sign-out request is no longer pending."

    approved = 1 if decision == "Approved" else 0
    now = datetime.now().isoformat(timespec="seconds")
    con.execute("""
        UPDATE attendance_records
        SET early_signout_approved=?,
            early_signout_approved_by=?,
            early_signout_approved_at=?,
            early_signout_approval_note=?,
            status='Present',
            updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (approved, admin_id, now, note.strip(), attendance_id))
    con.commit()
    con.close()

    audit(record["staff_id"], admin_id,
          f"early_signout_{decision.lower()}",
          f"Note: {note.strip()}")
    notify(
        record["staff_id"],
        "✅ Early Sign-Out Authorized" if decision == "Approved"
        else "❌ Early Sign-Out Rejected",
        (
            "Your early sign-out request was approved. You may now sign out."
            if decision == "Approved"
            else "Your early sign-out request was rejected."
        ) + (f" Note: {note.strip()}" if note.strip() else ""),
        priority="normal" if decision == "Approved" else "high",
        related_id=attendance_id, related_type="early_signout"
    )
    return True, f"Early sign-out {decision.lower()}."


# ============================================================
# LEAVE CORE
# ============================================================

def approved_leave(staff_id, work_date):
    con = db()
    row = con.execute("""
        SELECT * FROM leave_requests
        WHERE staff_id=? AND status='Approved'
          AND start_date<=? AND end_date>=?
        ORDER BY id DESC LIMIT 1
    """, (staff_id, work_date, work_date)).fetchone()
    con.close()
    return row


def overlapping_leave(staff_id, start_date, end_date):
    con = db()
    row = con.execute("""
        SELECT id FROM leave_requests
        WHERE staff_id=?
          AND status IN ('Pending','Approved')
          AND start_date<=? AND end_date>=?
        LIMIT 1
    """, (staff_id, end_date, start_date)).fetchone()
    con.close()
    return row is not None


def submit_leave(staff_id, leave_type, start_date, end_date, reason):
    if start_date > end_date:
        return False, "End date cannot be before start date."
    if not reason.strip():
        return False, "Please provide a reason."
    if overlapping_leave(staff_id, start_date.isoformat(), end_date.isoformat()):
        return False, "This period overlaps another pending or approved leave."

    con = db()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO leave_requests
        (staff_id, leave_type, start_date, end_date, reason)
        VALUES (?, ?, ?, ?, ?)
    """, (staff_id, leave_type, start_date.isoformat(),
          end_date.isoformat(), reason.strip()))
    request_id = cur.lastrowid
    con.commit()
    con.close()

    person = get_staff(staff_id)
    audit(staff_id, staff_id, "leave_request_submitted",
          f"{leave_type}: {start_date} to {end_date}")

    for approver in get_active_staff():
        if approver["role"] in APPROVER_ROLES:
            notify(
                approver["id"], "🏖️ New Leave Request",
                f"{person['full_name']} requested {leave_type} "
                f"from {start_date} to {end_date}.",
                related_id=request_id, related_type="leave_request"
            )

    return True, "Leave request submitted for approval."


def leave_requests(staff_id=None, status=None):
    con = db()
    q = """
        SELECT l.*, s.full_name, s.username, s.role
        FROM leave_requests l
        JOIN staff_users s ON s.id=l.staff_id
        WHERE 1=1
    """
    params = []
    if staff_id:
        q += " AND l.staff_id=?"
        params.append(staff_id)
    if status:
        q += " AND l.status=?"
        params.append(status)
    q += """
        ORDER BY CASE WHEN l.status='Pending' THEN 0 ELSE 1 END,
                 l.requested_at DESC, l.id DESC
        LIMIT 500
    """
    rows = con.execute(q, params).fetchall()
    con.close()
    return rows


def review_leave(request_id, admin_id, decision, note=""):
    if not is_approver(admin_id):
        return False, "You are not authorized to review leave."
    if decision not in {"Approved", "Rejected"}:
        return False, "Invalid decision."

    con = db()
    request = con.execute(
        "SELECT * FROM leave_requests WHERE id=? LIMIT 1",
        (request_id,)
    ).fetchone()
    if not request:
        con.close()
        return False, "Leave request not found."
    if request["status"] != "Pending":
        con.close()
        return False, "This request has already been reviewed."

    if decision == "Approved":
        overlap = con.execute("""
            SELECT id FROM leave_requests
            WHERE staff_id=? AND status='Approved'
              AND start_date<=? AND end_date>=? AND id!=?
            LIMIT 1
        """, (request["staff_id"], request["end_date"],
              request["start_date"], request["id"])).fetchone()
        if overlap:
            con.close()
            return False, "This request overlaps approved leave."

    now = datetime.now().isoformat(timespec="seconds")
    con.execute("""
        UPDATE leave_requests
        SET status=?, reviewed_by=?, reviewed_at=?, review_note=?
        WHERE id=?
    """, (decision, admin_id, now, note.strip(), request_id))
    con.commit()
    con.close()

    audit(request["staff_id"], admin_id,
          f"leave_{decision.lower()}",
          f"Note: {note.strip()}")
    notify(
        request["staff_id"],
        "✅ Leave Approved" if decision == "Approved" else "❌ Leave Rejected",
        f"Your {request['leave_type']} request "
        f"({request['start_date']} to {request['end_date']}) "
        f"was {decision.lower()}."
        + (f" Note: {note.strip()}" if note.strip() else ""),
        priority="normal" if decision == "Approved" else "high",
        related_id=request_id, related_type="leave_request"
    )
    return True, f"Leave request {decision.lower()}."


# ============================================================
# REPORTING
# ============================================================

def attendance_rows(staff_id=None, start=None, end=None, status=None):
    con = db()
    q = """
        SELECT a.*, s.full_name, s.username, s.role
        FROM attendance_records a
        JOIN staff_users s ON s.id=a.staff_id
        WHERE 1=1
    """
    params = []
    if staff_id:
        q += " AND a.staff_id=?"
        params.append(staff_id)
    if start:
        q += " AND a.work_date>=?"
        params.append(start)
    if end:
        q += " AND a.work_date<=?"
        params.append(end)
    if status:
        q += " AND a.status=?"
        params.append(status)
    q += " ORDER BY a.work_date DESC, s.full_name LIMIT 1000"
    rows = con.execute(q, params).fetchall()
    con.close()
    return rows


def today_metrics():
    today = date.today().isoformat()
    con = db()
    total = con.execute(
        "SELECT COUNT(*) FROM staff_users WHERE status='Active'"
    ).fetchone()[0]
    signed_in = con.execute("""
        SELECT COUNT(*) FROM attendance_records
        WHERE work_date=? AND sign_in_at IS NOT NULL
    """, (today,)).fetchone()[0]
    signed_out = con.execute("""
        SELECT COUNT(*) FROM attendance_records
        WHERE work_date=? AND sign_out_at IS NOT NULL
    """, (today,)).fetchone()[0]
    late = con.execute("""
        SELECT COUNT(*) FROM attendance_records
        WHERE work_date=? AND late_minutes>0
    """, (today,)).fetchone()[0]
    pending = con.execute("""
        SELECT COUNT(*) FROM attendance_records
        WHERE work_date=? AND early_signout_requested=1
          AND early_signout_approved=0 AND sign_out_at IS NULL
    """, (today,)).fetchone()[0]
    on_leave = con.execute("""
        SELECT COUNT(*) FROM leave_requests
        WHERE status='Approved' AND start_date<=? AND end_date>=?
    """, (today, today)).fetchone()[0]
    con.close()

    return {
        "total": total,
        "signed_in": signed_in,
        "signed_out": signed_out,
        "late": late,
        "pending": pending,
        "on_leave": on_leave,
        "absent": max(0, total - signed_in - on_leave),
    }


# ============================================================
# STAFF INTERFACE
# ============================================================

def show_staff_attendance(staff_id):
    init_database()
    person = get_staff(staff_id)
    if not person or person["status"] != "Active":
        st.error("Active staff account required.")
        return

    settings = get_settings()
    today = date.today()
    today_text = today.isoformat()
    record = get_record(staff_id, today_text)
    leave = approved_leave(staff_id, today_text)

    st.title("🕘 Leave & Attendance")
    st.caption("Pan Ideate Africa — Staff Attendance & Leave Management")
    st.success(f"Signed in as: {person['full_name']} • {person['role']}")

    a, b, c, d = st.columns(4)
    a.metric("Start", settings["work_start"])
    b.metric("End", settings["work_end"])
    c.metric("Grace", f"{settings['grace_minutes']} min")
    d.metric(
        "Status",
        "On Leave" if leave else
        "Completed" if record and record["sign_out_at"] else
        "At Work" if record and record["sign_in_at"] else
        "Not Signed In"
    )

    st.divider()

    if leave:
        st.info(f"🏖️ Approved {leave['leave_type']} today.")
    elif not record or not record["sign_in_at"]:
        if st.button("🟢 Sign In", use_container_width=True, type="primary"):
            ok, msg = sign_in(staff_id)
            (st.success if ok else st.error)(msg)
            if ok:
                st.rerun()
    else:
        st.write(f"**Sign In:** {record['sign_in_at'].replace('T', ' ')}")
        if record["late_minutes"]:
            st.warning(f"⏰ Late by {record['late_minutes']} minute(s).")

        if record["sign_out_at"]:
            st.success(
                f"🔴 Signed out: {record['sign_out_at'].replace('T', ' ')}"
            )
            st.info(f"Hours worked: **{record['hours_worked']:.2f}**")
        else:
            now = datetime.now()
            closing = datetime.combine(today, parse_time(settings["work_end"]))

            if now >= closing:
                if st.button("🔴 Sign Out", use_container_width=True, type="primary"):
                    ok, msg = sign_out(staff_id)
                    (st.success if ok else st.error)(msg)
                    if ok:
                        st.rerun()
            elif record["early_signout_requested"] and record["early_signout_approved"]:
                st.success("✅ Early sign-out authorized.")
                if st.button("🔴 Sign Out — Authorized",
                             use_container_width=True, type="primary"):
                    ok, msg = sign_out(staff_id, authorized=True)
                    (st.success if ok else st.error)(msg)
                    if ok:
                        st.rerun()
            elif record["early_signout_requested"]:
                st.warning("⏳ Early sign-out request is awaiting authorization.")
            else:
                st.warning(f"Normal sign-out begins at {settings['work_end']}.")
                with st.form("early_signout_form"):
                    reason = st.text_area(
                        "Reason for leaving early",
                        placeholder="Explain the reason..."
                    )
                    send = st.form_submit_button(
                        "📨 Request Early Sign-Out",
                        use_container_width=True
                    )
                    if send:
                        ok, msg = request_early_signout(staff_id, reason)
                        (st.success if ok else st.error)(msg)
                        if ok:
                            st.rerun()

    st.divider()

    tab1, tab2 = st.tabs(["🏖️ My Leave", "📊 My Attendance History"])

    with tab1:
        with st.form("leave_request_form", clear_on_submit=True):
            leave_type = st.selectbox("Leave Type", LEAVE_TYPES)
            x, y = st.columns(2)
            with x:
                start = st.date_input("Start Date", value=date.today())
            with y:
                end = st.date_input("End Date", value=date.today())
            reason = st.text_area("Reason")
            submit = st.form_submit_button(
                "📨 Submit Leave Request",
                use_container_width=True
            )
            if submit:
                ok, msg = submit_leave(
                    staff_id, leave_type, start, end, reason
                )
                (st.success if ok else st.error)(msg)
                if ok:
                    st.rerun()

        st.subheader("My Leave History")
        rows = leave_requests(staff_id=staff_id)
        if not rows:
            st.info("No leave requests yet.")
        for row in rows:
            with st.container(border=True):
                st.write(f"**{row['leave_type']}**")
                st.write(
                    f"{row['start_date']} → {row['end_date']} • "
                    f"**{row['status']}**"
                )
                st.write(row["reason"])
                if row["review_note"]:
                    st.caption(f"Review note: {row['review_note']}")

    with tab2:
        rows = attendance_rows(staff_id=staff_id)
        if not rows:
            st.info("No attendance records yet.")
        else:
            data = [{
                "Date": r["work_date"],
                "Sign In": r["sign_in_at"] or "—",
                "Sign Out": r["sign_out_at"] or "—",
                "Status": r["status"],
                "Late Min": r["late_minutes"],
                "Hours": r["hours_worked"]
            } for r in rows]
            st.dataframe(data, use_container_width=True, hide_index=True)


# ============================================================
# ADMIN INTERFACE
# ============================================================

def show_admin_leave_attendance(admin_id):
    init_database()
    admin = get_staff(admin_id)
    if not admin or not is_approver(admin_id):
        st.error("🔒 Authorized Administrator access required.")
        return

    st.title("🕘 Leave & Attendance")
    st.caption("Pan Ideate Africa — Workforce Attendance & Leave Control")
    st.success(f"Signed in as: {admin['full_name']} • {admin['role']}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard",
        "⏰ Early Sign-Out",
        "🏖️ Leave Approvals",
        "📑 Reports",
        "⚙️ Settings"
    ])

    with tab1:
        m = today_metrics()
        cols = st.columns(4)
        cols[0].metric("👥 Active Staff", m["total"])
        cols[1].metric("🟢 Signed In", m["signed_in"])
        cols[2].metric("⏰ Late Today", m["late"])
        cols[3].metric("🏖️ On Leave", m["on_leave"])
        cols = st.columns(3)
        cols[0].metric("🔴 Signed Out", m["signed_out"])
        cols[1].metric("⚠️ Absent", m["absent"])
        cols[2].metric("⏳ Early Sign-Out Pending", m["pending"])

        st.divider()
        st.subheader("🟢 Currently At Work")
        con = db()
        current = con.execute("""
            SELECT a.*, s.full_name, s.username, s.role
            FROM attendance_records a
            JOIN staff_users s ON s.id=a.staff_id
            WHERE a.work_date=? AND a.sign_in_at IS NOT NULL
              AND a.sign_out_at IS NULL
            ORDER BY a.sign_in_at
        """, (date.today().isoformat(),)).fetchall()
        con.close()

        if not current:
            st.info("No staff are currently signed in.")
        for r in current:
            with st.container(border=True):
                c1, c2, c3 = st.columns([4, 2, 2])
                c1.write(f"**{r['full_name']}**")
                c1.caption(f"@{r['username']} • {r['role']}")
                c2.write(f"🟢 Since {r['sign_in_at'].replace('T',' ')}")
                c3.warning(f"Late {r['late_minutes']} min"
                            if r["late_minutes"] else "On time")

    with tab2:
        st.subheader("⏰ Early Sign-Out Authorization")
        con = db()
        rows = con.execute("""
            SELECT a.*, s.full_name, s.username, s.role
            FROM attendance_records a
            JOIN staff_users s ON s.id=a.staff_id
            WHERE a.early_signout_requested=1
              AND a.early_signout_approved=0
              AND a.sign_out_at IS NULL
            ORDER BY a.early_signout_requested_at
        """).fetchall()
        con.close()

        if not rows:
            st.success("No pending early sign-out requests.")

        for r in rows:
            with st.container(border=True):
                st.markdown(f"### ⏰ {r['full_name']}")
                st.write(
                    f"**Date:** {r['work_date']}  \n"
                    f"**Requested:** {r['early_signout_requested_at']}  \n"
                    f"**Reason:** {r['early_signout_reason']}"
                )
                with st.form(f"early_review_{r['id']}"):
                    note = st.text_area(
                        "Authorization note",
                        key=f"early_note_{r['id']}"
                    )
                    c1, c2, c3 = st.columns(3)
                    approve = c1.form_submit_button(
                        "✅ Approve", use_container_width=True
                    )
                    reject = c2.form_submit_button(
                        "❌ Reject", use_container_width=True
                    )
                    emergency = c3.form_submit_button(
                        "🚨 Emergency Override + Authorize",
                        use_container_width=True
                    )
                    if approve or reject or emergency:
                        decision = "Approved" if (approve or emergency) else "Rejected"
                        ok, msg = review_early_signout(
                            r["id"], admin_id, decision, note
                        )
                        (st.success if ok else st.error)(msg)
                        if ok and emergency:
                            st.info(
                                "Authorization recorded. The employee can now sign out."
                            )
                        if ok:
                            st.rerun()

    with tab3:
        st.subheader("🏖️ Leave Approval")
        rows = leave_requests(status="Pending")
        if not rows:
            st.success("No pending leave requests.")

        for r in rows:
            with st.container(border=True):
                st.markdown(f"### 🏖️ {r['full_name']}")
                st.write(
                    f"**{r['leave_type']}** • "
                    f"{r['start_date']} → {r['end_date']}"
                )
                st.write(f"**Reason:** {r['reason']}")
                with st.form(f"leave_review_{r['id']}"):
                    note = st.text_area(
                        "Review note",
                        key=f"leave_note_{r['id']}"
                    )
                    c1, c2 = st.columns(2)
                    approve = c1.form_submit_button(
                        "✅ Approve Leave", use_container_width=True
                    )
                    reject = c2.form_submit_button(
                        "❌ Reject Leave", use_container_width=True
                    )
                    if approve or reject:
                        decision = "Approved" if approve else "Rejected"
                        ok, msg = review_leave(
                            r["id"], admin_id, decision, note
                        )
                        (st.success if ok else st.error)(msg)
                        if ok:
                            st.rerun()

    with tab4:
        st.subheader("📑 Attendance Reports")
        people = get_active_staff()
        options = ["All Staff"] + [label(p) for p in people]
        selected = st.selectbox("Employee", options)
        selected_id = None
        if selected != "All Staff":
            selected_id = next(
                (p["id"] for p in people if label(p) == selected),
                None
            )

        c1, c2, c3 = st.columns(3)
        start = c1.date_input(
            "From", value=date.today() - timedelta(days=30)
        )
        end = c2.date_input("To", value=date.today())
        status = c3.selectbox(
            "Status",
            ["All", "Present", "Late", "Early Sign-Out",
             "Pending Early Sign-Out"]
        )

        rows = attendance_rows(
            staff_id=selected_id,
            start=start.isoformat(),
            end=end.isoformat(),
            status=None if status == "All" else status
        )

        if not rows:
            st.info("No records found.")
        else:
            table = [{
                "Employee": r["full_name"],
                "Date": r["work_date"],
                "Sign In": r["sign_in_at"] or "—",
                "Sign Out": r["sign_out_at"] or "—",
                "Status": r["status"],
                "Late Min": r["late_minutes"],
                "Hours": r["hours_worked"]
            } for r in rows]
            st.dataframe(table, use_container_width=True, hide_index=True)

            lines = ["Employee,Date,Sign In,Sign Out,Status,Late Min,Hours"]
            for r in rows:
                vals = [
                    r["full_name"], r["work_date"],
                    r["sign_in_at"] or "", r["sign_out_at"] or "",
                    r["status"], r["late_minutes"],
                    f"{r['hours_worked']:.2f}"
                ]
                lines.append(",".join(
                    '"' + str(v).replace('"', '""') + '"' for v in vals
                ))
            st.download_button(
                "⬇️ Download Attendance CSV",
                "\n".join(lines).encode("utf-8"),
                file_name=f"attendance_{start}_{end}.csv",
                mime="text/csv",
                use_container_width=True
            )

    with tab5:
        st.subheader("⚙️ Attendance Settings")
        settings = get_settings()
        with st.form("attendance_settings"):
            start = st.text_input(
                "Normal start time (HH:MM)",
                settings["work_start"]
            )
            end = st.text_input(
                "Normal end time (HH:MM)",
                settings["work_end"]
            )
            grace = st.number_input(
                "Grace period (minutes)", 0, 240,
                int(settings["grace_minutes"])
            )
            require = st.checkbox(
                "Require authorization for early sign-out",
                bool(settings["early_signout_requires_approval"])
            )
            save = st.form_submit_button(
                "💾 Save Settings",
                use_container_width=True
            )
            if save:
                ok, msg = save_settings(
                    admin_id, start, end, grace, require
                )
                (st.success if ok else st.error)(msg)
                if ok:
                    st.rerun()

        st.info(
            "Example: with a 17:00 closing time, an employee who "
            "tries to leave at 14:30 must request authorization. "
            "An authorized administrator can approve or reject the request."
        )


# ============================================================
# GENERIC ENTRY POINTS
# ============================================================

def show_staff(staff_id):
    show_staff_attendance(staff_id)


def show_admin(admin_id):
    show_admin_leave_attendance(admin_id)


def show(user_id=None, admin=False):
    if admin:
        show_admin_leave_attendance(user_id)
    else:
        show_staff_attendance(user_id)
