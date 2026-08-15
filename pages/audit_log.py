import csv
import hashlib
import io
import json
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "pan_ideate.db"

AUDIT_TABLE = "audit_log"


def _db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def _table_columns(con, table_name):
    try:
        return {row[1] for row in con.execute(f"PRAGMA table_info({table_name})").fetchall()}
    except sqlite3.OperationalError:
        return set()


def ensure_audit_table():
    """Create the append-only audit table without touching existing modules."""
    con = _db()
    con.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {AUDIT_TABLE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_time TEXT NOT NULL,
            actor_id TEXT,
            actor_name TEXT NOT NULL DEFAULT 'System',
            actor_role TEXT,
            department TEXT,
            module TEXT NOT NULL,
            action TEXT NOT NULL,
            target_type TEXT,
            target_id TEXT,
            summary TEXT NOT NULL,
            details TEXT,
            severity TEXT NOT NULL DEFAULT 'INFO',
            outcome TEXT NOT NULL DEFAULT 'SUCCESS',
            previous_hash TEXT,
            event_hash TEXT NOT NULL
        )
        """
    )
    con.execute(
        f"CREATE INDEX IF NOT EXISTS idx_{AUDIT_TABLE}_time ON {AUDIT_TABLE}(event_time DESC)"
    )
    con.execute(
        f"CREATE INDEX IF NOT EXISTS idx_{AUDIT_TABLE}_module ON {AUDIT_TABLE}(module)"
    )
    con.execute(
        f"CREATE INDEX IF NOT EXISTS idx_{AUDIT_TABLE}_actor ON {AUDIT_TABLE}(actor_id)"
    )
    con.commit()
    con.close()


def _canonical_event(event):
    return json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def log_audit_event(
    module,
    action,
    summary,
    *,
    actor_id=None,
    actor_name="System",
    actor_role=None,
    department=None,
    target_type=None,
    target_id=None,
    details=None,
    severity="INFO",
    outcome="SUCCESS",
):
    """Append one tamper-evident audit event. Existing modules can call this helper."""
    ensure_audit_table()
    event_time = datetime.now(timezone.utc).isoformat(timespec="seconds")
    severity = str(severity or "INFO").upper()
    outcome = str(outcome or "SUCCESS").upper()
    details_text = (
        json.dumps(details, ensure_ascii=False, default=str)
        if isinstance(details, (dict, list, tuple))
        else (None if details is None else str(details))
    )

    con = _db()
    previous = con.execute(
        f"SELECT event_hash FROM {AUDIT_TABLE} ORDER BY id DESC LIMIT 1"
    ).fetchone()
    previous_hash = previous[0] if previous else "GENESIS"

    payload = {
        "event_time": event_time,
        "actor_id": actor_id,
        "actor_name": actor_name,
        "actor_role": actor_role,
        "department": department,
        "module": module,
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
        "summary": summary,
        "details": details_text,
        "severity": severity,
        "outcome": outcome,
        "previous_hash": previous_hash,
    }
    event_hash = hashlib.sha256(_canonical_event(payload).encode("utf-8")).hexdigest()

    con.execute(
        f"""
        INSERT INTO {AUDIT_TABLE}
        (event_time, actor_id, actor_name, actor_role, department, module, action,
         target_type, target_id, summary, details, severity, outcome, previous_hash, event_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_time, actor_id, actor_name, actor_role, department, module, action,
            target_type, target_id, summary, details_text, severity, outcome,
            previous_hash, event_hash,
        ),
    )
    con.commit()
    con.close()
    return event_hash


def _get_staff_context():
    """Best-effort lookup for the active administrator without assuming schema extras."""
    con = _db()
    cols = _table_columns(con, "staff_users")
    if not cols:
        con.close()
        return None

    wanted = [c for c in ["id", "full_name", "username", "role", "department"] if c in cols]
    if not wanted:
        con.close()
        return None

    row = con.execute(
        f"SELECT {', '.join(wanted)} FROM staff_users WHERE LOWER(username) = 'admin' AND status = 'Active' LIMIT 1"
    ).fetchone()
    con.close()
    return row


def _fetch_events(module="All Modules", severity="All Severities", outcome="All Outcomes",
                  actor="All Actors", search="", start_date=None, end_date=None):
    ensure_audit_table()
    con = _db()
    clauses = []
    params = []

    if module != "All Modules":
        clauses.append("module = ?")
        params.append(module)
    if severity != "All Severities":
        clauses.append("severity = ?")
        params.append(severity)
    if outcome != "All Outcomes":
        clauses.append("outcome = ?")
        params.append(outcome)
    if actor != "All Actors":
        clauses.append("actor_name = ?")
        params.append(actor)
    if search.strip():
        q = f"%{search.strip()}%"
        clauses.append("(summary LIKE ? OR details LIKE ? OR target_type LIKE ? OR target_id LIKE ? OR action LIKE ?)")
        params.extend([q, q, q, q, q])
    if start_date:
        clauses.append("date(event_time) >= date(?)")
        params.append(start_date.isoformat())
    if end_date:
        clauses.append("date(event_time) <= date(?)")
        params.append(end_date.isoformat())

    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    rows = con.execute(
        f"SELECT * FROM {AUDIT_TABLE}{where} ORDER BY id DESC", params
    ).fetchall()
    con.close()
    return rows


def _all_values(column):
    ensure_audit_table()
    con = _db()
    rows = con.execute(
        f"SELECT DISTINCT {column} FROM {AUDIT_TABLE} WHERE {column} IS NOT NULL AND {column} != '' ORDER BY {column}"
    ).fetchall()
    con.close()
    return [row[0] for row in rows]


def _verify_chain(rows=None):
    ensure_audit_table()
    con = _db()
    all_rows = con.execute(f"SELECT * FROM {AUDIT_TABLE} ORDER BY id ASC").fetchall()
    con.close()

    previous = "GENESIS"
    checked = 0
    for row in all_rows:
        payload = {
            "event_time": row["event_time"],
            "actor_id": row["actor_id"],
            "actor_name": row["actor_name"],
            "actor_role": row["actor_role"],
            "department": row["department"],
            "module": row["module"],
            "action": row["action"],
            "target_type": row["target_type"],
            "target_id": row["target_id"],
            "summary": row["summary"],
            "details": row["details"],
            "severity": row["severity"],
            "outcome": row["outcome"],
            "previous_hash": row["previous_hash"],
        }
        expected = hashlib.sha256(_canonical_event(payload).encode("utf-8")).hexdigest()
        if row["previous_hash"] != previous or row["event_hash"] != expected:
            return False, checked, row["id"]
        previous = row["event_hash"]
        checked += 1
    return True, checked, None


def _export_csv(rows):
    output = io.StringIO()
    fields = [
        "id", "event_time", "actor_id", "actor_name", "actor_role", "department",
        "module", "action", "target_type", "target_id", "summary", "details",
        "severity", "outcome", "previous_hash", "event_hash",
    ]
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row[field] for field in fields})
    return output.getvalue().encode("utf-8")


def _severity_icon(value):
    return {
        "CRITICAL": "🔴",
        "HIGH": "🟠",
        "WARNING": "🟡",
        "INFO": "🔵",
    }.get(value, "⚪")


def show_audit_log():
    ensure_audit_table()

    st.title("🔐 Audit & Activity Log")
    st.caption("Pan Ideate Africa — accountable, searchable and tamper-evident organizational activity history")

    staff_context = _get_staff_context()
    if staff_context:
        name = staff_context["full_name"] if "full_name" in staff_context.keys() else "Administrator"
        role = staff_context["role"] if "role" in staff_context.keys() else "Administrator"
        st.success(f"🔒 Audit access: {name} • {role}")
    else:
        st.info("Audit records are available to authorized administrators. The system is using its central audit database.")

    con = _db()
    total = con.execute(f"SELECT COUNT(*) FROM {AUDIT_TABLE}").fetchone()[0]
    today = con.execute(f"SELECT COUNT(*) FROM {AUDIT_TABLE} WHERE date(event_time) = date('now')").fetchone()[0]
    high = con.execute(f"SELECT COUNT(*) FROM {AUDIT_TABLE} WHERE severity IN ('HIGH','CRITICAL')").fetchone()[0]
    failed = con.execute(f"SELECT COUNT(*) FROM {AUDIT_TABLE} WHERE outcome NOT IN ('SUCCESS','COMPLETED')").fetchone()[0]
    con.close()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📚 Total Events", total)
    c2.metric("🕘 Today", today)
    c3.metric("🚨 High Priority", high)
    c4.metric("⚠️ Non-success", failed)

    st.divider()
    st.markdown("### 🧭 Activity Intelligence")

    f1, f2, f3 = st.columns(3)
    with f1:
        modules = ["All Modules"] + _all_values("module")
        module = st.selectbox("Module", modules, key="audit_filter_module")
    with f2:
        severities = ["All Severities", "CRITICAL", "HIGH", "WARNING", "INFO"]
        severity = st.selectbox("Severity", severities, key="audit_filter_severity")
    with f3:
        outcomes = ["All Outcomes"] + _all_values("outcome")
        outcome = st.selectbox("Outcome", outcomes, key="audit_filter_outcome")

    f4, f5, f6 = st.columns(3)
    with f4:
        actors = ["All Actors"] + _all_values("actor_name")
        actor = st.selectbox("Actor", actors, key="audit_filter_actor")
    with f5:
        search = st.text_input("🔎 Search activity", placeholder="approval, expense, Sandra, procurement…", key="audit_search")
    with f6:
        date_mode = st.selectbox("Date range", ["All time", "Today", "Last 7 days", "Last 30 days", "Custom"], key="audit_date_mode")

    now = datetime.now().astimezone()
    start_date = None
    end_date = None
    if date_mode == "Today":
        start_date = end_date = now.date()
    elif date_mode == "Last 7 days":
        start_date = (now - timedelta(days=6)).date()
        end_date = now.date()
    elif date_mode == "Last 30 days":
        start_date = (now - timedelta(days=29)).date()
        end_date = now.date()
    elif date_mode == "Custom":
        d1, d2 = st.columns(2)
        with d1:
            start_date = st.date_input("From", value=(now - timedelta(days=30)).date(), key="audit_start_date")
        with d2:
            end_date = st.date_input("To", value=now.date(), key="audit_end_date")
        if start_date > end_date:
            st.error("The start date cannot be after the end date.")
            return

    rows = _fetch_events(module, severity, outcome, actor, search, start_date, end_date)

    a1, a2, a3 = st.columns(3)
    a1.metric("🔎 Matching Events", len(rows))
    ok, checked, broken_id = _verify_chain()
    if ok:
        a2.metric("🛡️ Integrity", "Verified")
    else:
        a2.metric("🛡️ Integrity", "ALERT")
    a3.metric("⛓️ Chain Checked", checked)

    if not ok:
        st.error(f"🚨 Audit chain verification failed at event #{broken_id}. Do not delete or edit audit records. Investigate the database immediately.")
    else:
        st.success("🛡️ Audit integrity verified — the append-only event chain is consistent.")

    b1, b2 = st.columns([1, 1])
    with b1:
        st.download_button(
            "⬇️ Export Filtered Audit CSV",
            data=_export_csv(rows),
            file_name=f"pan_ideate_audit_{now.strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with b2:
        if st.button("🔄 Refresh Audit View", use_container_width=True):
            st.rerun()

    st.divider()
    st.markdown("### 🧾 Activity Timeline")

    if not rows:
        st.info("No audit events match the current filters. New important administrative activity will appear here automatically when modules record it.")
    else:
        for row in rows[:250]:
            icon = _severity_icon(row["severity"])
            when = row["event_time"].replace("T", " ").replace("+00:00", " UTC")
            title = f"{icon} {row['summary']}"
            with st.expander(f"{when}  •  {row['module']}  •  {title}"):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Actor:** {row['actor_name']}")
                c2.write(f"**Role:** {row['actor_role'] or '—'}")
                c3.write(f"**Department:** {row['department'] or '—'}")
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Action:** {row['action']}")
                c2.write(f"**Outcome:** {row['outcome']}")
                c3.write(f"**Severity:** {row['severity']}")
                if row["target_type"] or row["target_id"]:
                    st.write(f"**Target:** {row['target_type'] or '—'} {row['target_id'] or ''}")
                if row["details"]:
                    st.write("**Details:**")
                    st.code(row["details"], language="text")
                st.caption(f"Event #{row['id']} • Hash: {row['event_hash'][:20]}…")

        if len(rows) > 250:
            st.caption(f"Showing the newest 250 of {len(rows)} matching events. Export the filtered CSV for the complete result set.")

    st.divider()
    st.markdown("### 🛡️ Governance & Security")
    st.info(
        "The Audit & Activity Log is designed as an accountability layer. "
        "It does not replace the business rules of Leave & Attendance, Expenses & Procurement, "
        "Approval Centre, Meeting Centre or other modules. Those modules can record their important "
        "actions here through the shared log_audit_event() function. Audit records should be treated "
        "as append-only and should not be edited or deleted through the application."
    )


if __name__ == "__main__":
    show_audit_log()
