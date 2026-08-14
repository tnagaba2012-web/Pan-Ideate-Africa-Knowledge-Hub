import sqlite3
import re
from pathlib import Path
from datetime import datetime, date, timedelta
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "pan_ideate.db"

APPROVER_ROLES = {"Super Admin", "Administrator", "Manager", "Finance"}

def db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

def init_database():
    con = db()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS staff_appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            appointment_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            expected_end_time TEXT,
            location TEXT,
            contact_person TEXT,
            notes TEXT,
            status TEXT NOT NULL DEFAULT 'Scheduled',
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ai_staff_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL DEFAULT 'Warning',
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            source_id INTEGER,
            source_type TEXT,
            alert_date TEXT NOT NULL,
            is_read INTEGER NOT NULL DEFAULT 0,
            is_resolved INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ai_staff_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER,
            actor_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_ai_alert
        ON ai_staff_alerts(
            staff_id, alert_type, source_id, source_type, alert_date
        )
    """)
    con.commit()
    con.close()

def get_staff(staff_id):
    if not staff_id:
        return None
    con = db()
    try:
        row = con.execute("""
            SELECT id, full_name, username, role, status
            FROM staff_users WHERE id=? LIMIT 1
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
            WHERE status='Active'
            ORDER BY full_name
        """).fetchall()
    except sqlite3.OperationalError:
        rows = []
    con.close()
    return rows

def is_admin(staff_id):
    p = get_staff(staff_id)
    return bool(p and p["status"] == "Active" and p["role"] in APPROVER_ROLES)

def notify(user_id, title, message, severity="Warning", alert_id=None):
    try:
        from pages.notification_centre import create_notification
        create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="alert",
            priority="high" if severity != "Info" else "normal",
            related_id=alert_id,
            related_type="ai_staff_alert",
        )
    except Exception:
        pass

def audit(staff_id, actor_id, action, details=""):
    con = db()
    con.execute("""
        INSERT INTO ai_staff_audit(staff_id, actor_id, action, details)
        VALUES (?, ?, ?, ?)
    """, (staff_id, actor_id, action, details))
    con.commit()
    con.close()

def create_alert(staff_id, alert_type, severity, title, message,
                 source_id=None, source_type=None, alert_date=None):
    alert_date = alert_date or date.today().isoformat()
    con = db()
    row = con.execute("""
        SELECT id FROM ai_staff_alerts
        WHERE staff_id IS ? AND alert_type=?
          AND source_id IS ? AND source_type IS ? AND alert_date=?
        LIMIT 1
    """, (staff_id, alert_type, source_id, source_type, alert_date)).fetchone()
    if row:
        con.close()
        return row["id"], False
    cur = con.cursor()
    cur.execute("""
        INSERT INTO ai_staff_alerts
        (staff_id, alert_type, severity, title, message,
         source_id, source_type, alert_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (staff_id, alert_type, severity, title, message,
          source_id, source_type, alert_date))
    alert_id = cur.lastrowid
    con.commit()
    con.close()
    notify(staff_id, title, message, severity, alert_id)
    audit(staff_id, staff_id, "alert_created",
          f"{alert_type}; {severity}; {message}")
    return alert_id, True

def get_alerts(staff_id=None, include_resolved=False, limit=100):
    con = db()
    q = """
        SELECT a.*, s.full_name, s.username
        FROM ai_staff_alerts a
        LEFT JOIN staff_users s ON s.id=a.staff_id
        WHERE 1=1
    """
    params = []
    if staff_id:
        q += " AND a.staff_id=?"
        params.append(staff_id)
    if not include_resolved:
        q += " AND a.is_resolved=0"
    q += """
        ORDER BY CASE a.severity
            WHEN 'Critical' THEN 0 WHEN 'Warning' THEN 1 ELSE 2 END,
            a.created_at DESC LIMIT ?
    """
    params.append(limit)
    rows = con.execute(q, params).fetchall()
    con.close()
    return rows

def attendance_settings():
    con = db()
    try:
        row = con.execute("""
            SELECT work_start, work_end, grace_minutes
            FROM attendance_settings WHERE id=1
        """).fetchone()
    except sqlite3.OperationalError:
        row = None
    con.close()
    return dict(row) if row else {
        "work_start": "08:00", "work_end": "17:00", "grace_minutes": 15
    }

def parse_dt(value):
    if not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M",
                "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    return None

def scan_attendance_alerts(now=None):
    init_database()
    now = now or datetime.now()
    today = now.date().isoformat()
    settings = attendance_settings()
    try:
        start = datetime.strptime(
            f"{today} {settings['work_start']}", "%Y-%m-%d %H:%M")
        end = datetime.strptime(
            f"{today} {settings['work_end']}", "%Y-%m-%d %H:%M")
    except ValueError:
        start = datetime.strptime(f"{today} 08:00", "%Y-%m-%d %H:%M")
        end = datetime.strptime(f"{today} 17:00", "%Y-%m-%d %H:%M")
    grace = int(settings["grace_minutes"])
    con = db()
    rows = con.execute("""
        SELECT a.id, a.staff_id, a.sign_in_at, a.sign_out_at,
               a.early_signout_requested, s.full_name
        FROM attendance_records a
        JOIN staff_users s ON s.id=a.staff_id
        WHERE a.work_date=? AND s.status='Active'
    """, (today,)).fetchall()
    active = con.execute("""
        SELECT id, full_name FROM staff_users WHERE status='Active'
    """).fetchall()
    con.close()

    made = []
    seen = {r["staff_id"] for r in rows if r["sign_in_at"]}

    for r in rows:
        sign_in = parse_dt(r["sign_in_at"])
        if sign_in:
            late = max(0, int((sign_in - start).total_seconds()/60))
            if late > grace:
                aid, created = create_alert(
                    r["staff_id"], "late_arrival",
                    "Critical" if late >= 60 else "Warning",
                    "⚠️ Late Arrival Detected",
                    f"{r['full_name']}, your sign-in was {late} minute(s) "
                    f"after the configured grace period.",
                    r["id"], "attendance", today)
                if created: made.append(aid)

        if r["early_signout_requested"] and not r["sign_out_at"]:
            aid, created = create_alert(
                r["staff_id"], "early_leave_request", "Warning",
                "🕘 Early Leave Request Pending",
                "Your early sign-out request is awaiting approval.",
                r["id"], "attendance", today)
            if created: made.append(aid)

        if r["sign_in_at"] and not r["sign_out_at"] and now >= end + timedelta(minutes=30):
            aid, created = create_alert(
                r["staff_id"], "missing_sign_out", "Warning",
                "🔔 Sign-Out Reminder",
                "Your attendance record still has no sign-out. "
                "Please complete the required attendance process.",
                r["id"], "attendance", today)
            if created: made.append(aid)

    if now >= start + timedelta(minutes=grace):
        for p in active:
            if p["id"] not in seen:
                aid, created = create_alert(
                    p["id"], "missing_sign_in", "Warning",
                    "⚠️ Attendance Check",
                    f"No sign-in has been recorded for you today after "
                    f"the {grace}-minute grace period. Please sign in "
                    f"or contact your supervisor if appropriate.",
                    None, "attendance_missing", today)
                if created: made.append(aid)
    return made

def scan_appointment_alerts(now=None):
    init_database()
    now = now or datetime.now()
    today = now.date().isoformat()
    con = db()
    rows = con.execute("""
        SELECT * FROM staff_appointments
        WHERE appointment_date=? AND status='Scheduled'
    """, (today,)).fetchall()
    con.close()
    made = []
    for a in rows:
        try:
            start = datetime.strptime(
                f"{a['appointment_date']} {a['start_time']}",
                "%Y-%m-%d %H:%M")
        except ValueError:
            continue
        minutes = (start-now).total_seconds()/60
        if 0 <= minutes <= 15:
            aid, created = create_alert(
                a["staff_id"], "appointment_reminder", "Info",
                "📅 Appointment Reminder",
                f"Your appointment '{a['title']}' starts at "
                f"{a['start_time']}."
                + (f" Location: {a['location']}." if a["location"] else ""),
                a["id"], "appointment", today)
            if created: made.append(aid)
        if minutes < -10:
            delay = int(-minutes)
            aid, created = create_alert(
                a["staff_id"], "appointment_delay",
                "Critical" if delay >= 30 else "Warning",
                "⏰ Appointment Delay Warning",
                f"Your appointment '{a['title']}' started at "
                f"{a['start_time']} and is now {delay} minute(s) overdue. "
                "Please attend, reschedule, or notify the relevant person.",
                a["id"], "appointment", today)
            if created: made.append(aid)
    return made

def run_alert_engine(now=None):
    init_database()
    return scan_attendance_alerts(now) + scan_appointment_alerts(now)

def resolve_alert(alert_id, actor_id):
    con = db()
    row = con.execute(
        "SELECT staff_id FROM ai_staff_alerts WHERE id=?",
        (alert_id,)).fetchone()
    if not row:
        con.close()
        return False, "Alert not found."
    if row["staff_id"] != actor_id and not is_admin(actor_id):
        con.close()
        return False, "You are not authorized to resolve this alert."
    con.execute("UPDATE ai_staff_alerts SET is_resolved=1 WHERE id=?",
                (alert_id,))
    con.commit()
    con.close()
    audit(row["staff_id"], actor_id, "alert_resolved", f"Alert {alert_id}")
    return True, "Alert resolved."

def add_appointment(staff_id, title, appointment_date, start_time,
                    expected_end_time="", location="",
                    contact_person="", notes="", created_by=None):
    if not get_staff(staff_id):
        return False, "Staff member not found."
    if not title.strip():
        return False, "Appointment title is required."
    con = db()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO staff_appointments
        (staff_id, title, appointment_date, start_time,
         expected_end_time, location, contact_person, notes, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (staff_id, title.strip(), appointment_date, start_time,
          expected_end_time, location.strip(), contact_person.strip(),
          notes.strip(), created_by or staff_id))
    rid = cur.lastrowid
    con.commit()
    con.close()
    return True, rid


def directory_rows():
    """Return Staff Directory records for the Assistant's authorized lookups."""
    try:
        from pages.staff_directory import get_directory_staff
        return get_directory_staff(status="Active")
    except Exception:
        return []


def _normalize(value):
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def find_directory_staff(question):
    """Find the most likely active staff member mentioned in a question."""
    rows = directory_rows()
    if not rows:
        return None

    q = _normalize(question)

    # Prefer exact full-name / username / staff-ID matches.
    exact = []
    for row in rows:
        candidates = [
            row["full_name"],
            row["username"],
            row["staff_id"],
        ]
        for candidate in candidates:
            n = _normalize(candidate)
            if n and n in q:
                exact.append(row)
                break

    if len(exact) == 1:
        return exact[0]

    # Fall back to matching the meaningful name tokens.
    best = None
    best_score = 0
    for row in rows:
        name = _normalize(row["full_name"])
        tokens = [t for t in name.split() if len(t) >= 3]
        score = sum(1 for token in tokens if token in q)
        if score > best_score:
            best_score = score
            best = row

    return best if best_score else None


def _directory_answer(question):
    """Answer basic people/company questions from the Staff Directory."""
    q = _normalize(question)
    person = find_directory_staff(question)

    # Department-wide queries.
    if person is None:
        rows = directory_rows()

        dept = None
        for row in rows:
            d = _normalize(row["department"])
            if d and d in q:
                dept = row["department"]
                break

        if dept and any(word in q for word in (
            "who", "staff", "people", "employee", "employees", "work",
            "works", "department", "team"
        )):
            members = [r for r in rows if r["department"] == dept]
            if members:
                names = []
                for r in members:
                    title = r["job_title"] or r["role"] or "Staff"
                    names.append(f"• {r['full_name']} — {title}")
                return (
                    f"**{dept}** currently has {len(members)} active "
                    "staff member(s):\n\n" + "\n".join(names)
                )

        if any(word in q for word in (
            "who is active", "active staff", "all staff", "list staff"
        )):
            return "\n".join(
                f"• {r['full_name']} — "
                f"{r['job_title'] or r['role'] or 'Staff'}"
                for r in rows
            )

        return None

    name = person["full_name"]
    title = person["job_title"] or person["role"] or "Staff"
    department = person["department"] or "Department not yet assigned"

    if any(word in q for word in (
        "role", "position", "job", "title", "what does", "responsible"
    )):
        return (
            f"**{name}** is **{title}** in the **{department}** "
            "department."
        )

    if any(word in q for word in ("department", "where does", "which department")):
        return f"**{name}** works in the **{department}** department."

    if any(word in q for word in ("phone", "telephone", "contact number", "mobile")):
        phone = person["phone"] or "No phone number has been entered in the Staff Directory."
        return f"**{name}'s phone:** {phone}"

    if any(word in q for word in ("email", "e-mail", "mail address")):
        email = person["email"] or "No email address has been entered in the Staff Directory."
        return f"**{name}'s email:** {email}"

    if any(word in q for word in ("location", "office", "work place", "workplace")):
        location = person["work_location"] or "No work location has been entered in the Staff Directory."
        return f"**{name}'s work location:** {location}"

    if any(word in q for word in ("joined", "date joined", "started", "start date")):
        joined = person["date_joined"] or "No joining date has been entered in the Staff Directory."
        return f"**{name}'s date joined:** {joined}"

    if any(word in q for word in ("status", "active", "inactive", "suspended")):
        return f"**{name}'s account status:** {person['status']}."

    if any(word in q for word in ("about", "profile", "bio", "who is")):
        bio = person["bio"] or "No additional profile biography has been entered."
        return (
            f"**{name}**\n\n"
            f"**Job title:** {title}\n\n"
            f"**Department:** {department}\n\n"
            f"**Status:** {person['status']}\n\n"
            f"**Profile:** {bio}"
        )

    return (
        f"**{name}** is **{title}** in **{department}**. "
        "You can ask me for the person's job title, department, "
        "phone, email, work location, joining date, status or profile."
    )

def assistant_response(question, staff_id):
    p = get_staff(staff_id)
    if not p:
        return "I could not identify your staff account."

    # First try the internal Staff Directory so people/company
    # questions are answered from Pan Ideate Africa's actual records.
    directory_answer = _directory_answer(question)
    if directory_answer:
        return directory_answer

    q = (question or "").lower()
    if any(x in q for x in ("late", "attendance", "arrive", "sign in")):
        s = attendance_settings()
        return (f"Your configured start time is {s['work_start']} with a "
                f"{s['grace_minutes']}-minute grace period. I monitor the "
                "attendance record and can issue a warning when a late "
                "arrival or missing sign-in is detected.")
    if any(x in q for x in ("leave", "early", "sign out")):
        return ("Use Leave & Attendance for early sign-out requests. "
                "I can warn you when an early-leave request is still "
                "awaiting approval.")
    if any(x in q for x in ("meeting", "appointment", "schedule")):
        return ("I can issue appointment reminders and delay warnings. "
                "The appointment table is designed to connect directly "
                "to the future Meeting Centre.")
    if any(x in q for x in ("expense", "procurement", "purchase")):
        return ("Expenses & Procurement handles expense claims and "
                "purchase requests. I can guide you through the workflow; "
                "approval remains with authorized management.")
    alerts = get_alerts(staff_id)
    if any(x in q for x in ("warning", "alert", "notification")):
        return (f"You currently have {len(alerts)} unresolved assistant "
                "alert(s)." if alerts else
                "You currently have no unresolved assistant alerts.")
    return (f"Hello {p['full_name']}. I am your Pan Ideate Africa Staff "
            "Assistant. I can currently help with attendance, leave, "
            "appointments, expenses, procurement and alerts. The "
            "generative-AI connector can be added later.")

def show_staff_ai_assistant(staff_id):
    init_database()
    p = get_staff(staff_id)
    if not p or p["status"] != "Active":
        st.error("Active staff account required.")
        return
    run_alert_engine()
    st.title("🤖 AI Staff Assistant")
    st.caption("Pan Ideate Africa — Intelligent Staff Support & Alerts")
    st.success(f"Assistant active for {p['full_name']} • {p['role']}")

    t1, t2, t3 = st.tabs(["🤖 Assistant", "🚨 My Alerts", "📅 Appointments"])
    with t1:
        q = st.text_area(
            "What do you need help with?",
            placeholder="Ask about staff, roles, departments, attendance, leave, "
                        "appointments, expenses, procurement or alerts...")
        if st.button("🤖 Ask Assistant", type="primary",
                     use_container_width=True):
            st.info(assistant_response(q, staff_id))
        st.divider()
        st.subheader("⚡ Intelligent Monitoring")
        a, b, c = st.columns(3)
        a.write("🕘 **Attendance**")
        a.caption("Late-arrival and missing sign-in warnings.")
        b.write("🚪 **Early Leave**")
        b.caption("Pending early sign-out warnings.")
        c.write("📅 **Appointments**")
        c.caption("Reminders and delay warnings.")
    with t2:
        alerts = get_alerts(staff_id)
        if not alerts:
            st.success("✅ No unresolved assistant alerts.")
        for alert in alerts:
            icon = {"Critical":"🔴","Warning":"🟠","Info":"🔵"}.get(
                alert["severity"], "⚪")
            with st.container(border=True):
                st.write(f"{icon} **{alert['title']}**")
                st.write(alert["message"])
                if st.button("✓ Resolve", key=f"staff_ai_res_{alert['id']}"):
                    ok, msg = resolve_alert(alert["id"], staff_id)
                    (st.success if ok else st.error)(msg)
                    if ok: st.rerun()
    with t3:
        con = db()
        rows = con.execute("""
            SELECT * FROM staff_appointments
            WHERE staff_id=?
            ORDER BY appointment_date DESC, start_time DESC
            LIMIT 100
        """, (staff_id,)).fetchall()
        con.close()
        if not rows:
            st.info("No appointments recorded yet.")
        for a in rows:
            with st.container(border=True):
                st.write(f"**{a['title']}**")
                st.write(f"{a['appointment_date']} • {a['start_time']}")
                if a["location"]: st.caption(f"Location: {a['location']}")

def show_admin_ai_staff_assistant(admin_id):
    init_database()
    if not is_admin(admin_id):
        st.error("🔒 Authorized Administrator access required.")
        return
    run_alert_engine()
    p = get_staff(admin_id)
    st.title("🤖 AI Staff Assistant")
    st.caption("Pan Ideate Africa — Intelligent Workforce Monitoring")
    st.success(f"Monitoring active • {p['full_name']} • {p['role']}")
    alerts = get_alerts()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🚨 Open Alerts", len(alerts))
    c2.metric("🔴 Critical", sum(a["severity"]=="Critical" for a in alerts))
    c3.metric("🟠 Warnings", sum(a["severity"]=="Warning" for a in alerts))
    c4.metric("🔵 Info", sum(a["severity"]=="Info" for a in alerts))

    t1, t2, t3 = st.tabs(["🚨 Alerts", "📅 Appointments", "🤖 Assistant Test"])
    with t1:
        if not alerts:
            st.success("✅ No unresolved staff alerts.")
        for alert in alerts:
            icon = {"Critical":"🔴","Warning":"🟠","Info":"🔵"}.get(
                alert["severity"], "⚪")
            with st.expander(
                f"{icon} {alert['title']} — "
                f"{alert['full_name'] or 'System'}"):
                st.write(alert["message"])
                st.caption(f"{alert['created_at']} • {alert['severity']}")
                if st.button("✓ Resolve", key=f"admin_ai_res_{alert['id']}"):
                    ok, msg = resolve_alert(alert["id"], admin_id)
                    (st.success if ok else st.error)(msg)
                    if ok: st.rerun()
    with t2:
        st.info("This appointment foundation is ready for the future "
                "Meeting Centre. It can already generate reminders and "
                "delay warnings.")
        people = get_active_staff()
        if people:
            labels = {f"{x['full_name']} (@{x['username']})": x["id"]
                      for x in people}
            selected = st.selectbox("Staff Member", list(labels))
            with st.form("ai_admin_appointment"):
                title = st.text_input("Appointment / Meeting Title")
                d = st.date_input("Date", value=date.today())
                tm = st.time_input("Start Time")
                location = st.text_input("Location")
                contact = st.text_input("Contact Person")
                notes = st.text_area("Notes")
                save = st.form_submit_button(
                    "📅 Add Appointment", type="primary",
                    use_container_width=True)
                if save:
                    ok, result = add_appointment(
                        labels[selected], title, d.isoformat(),
                        tm.strftime("%H:%M"), location=location,
                        contact_person=contact, notes=notes,
                        created_by=admin_id)
                    if ok:
                        st.success(f"Appointment #{result} created.")
                        st.rerun()
                    else:
                        st.error(result)
    with t3:
        people = get_active_staff()
        if people:
            # Use simple strings as widget options.
            # sqlite3.Row objects cannot be pickled by Streamlit.
            staff_options = {
                f"{x['full_name']} — {x['role']}": x["id"]
                for x in people
            }
            selected_label = st.selectbox(
                "Test as staff member", list(staff_options.keys()))
            q = st.text_area("Ask the assistant")
            if st.button("Run Assistant", type="primary"):
                st.info(
                    assistant_response(
                        q, staff_options[selected_label]
                    )
                )

def show_staff(staff_id):
    show_staff_ai_assistant(staff_id)

def show_admin(admin_id):
    show_admin_ai_staff_assistant(admin_id)

def show(user_id=None, admin=False):
    if admin:
        show_admin_ai_staff_assistant(user_id)
    else:
        show_staff_ai_assistant(user_id)

init_database()
