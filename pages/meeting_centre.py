import sqlite3
from pathlib import Path
from datetime import datetime, date

import streamlit as st

# ============================================================
# PAN IDEATE AFRICA
# MEETING CENTRE V1
# ============================================================
# Purpose:
# Central meeting management for Pan Ideate Africa.
#
# Designed to work with the existing AI Staff Assistant:
# - Meetings are stored here.
# - Each participant receives an appointment record in
#   staff_appointments so the AI Assistant can issue reminders
#   and delay warnings.
#
# V1 capabilities:
# - Meeting dashboard
# - Create meetings
# - Staff participants
# - RSVP
# - Attendance status
# - Agenda
# - Meeting minutes
# - Decisions
# - Action points
# - Responsible staff
# - Deadlines
# - Follow-up status
# - Overdue action visibility
# - Admin oversight
# - Staff personal meeting view
#
# Future:
# - Calendar month/week view
# - External guests
# - File attachments via Document Centre
# - Automatic AI follow-up warnings
# - Email/SMS/WhatsApp notifications
# - Recurring meetings
# - Video-conference links
# - Permission Centre integration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "pan_ideate.db"

ADMIN_ROLES = {"Super Admin", "Administrator", "Manager"}
DEPARTMENT_MEETING_ADMIN_ROLES = {"Super Admin", "Administrator"}


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
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            meeting_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            location TEXT,
            meeting_link TEXT,
            organizer_id INTEGER NOT NULL,
            purpose TEXT,
            agenda TEXT,
            status TEXT NOT NULL DEFAULT 'Scheduled',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS meeting_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER NOT NULL UNIQUE,
            department TEXT NOT NULL,
            can_organize INTEGER NOT NULL DEFAULT 0,
            updated_by INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # V1 databases may not yet have department/audit fields.
    for column, definition in [
        ("department", "TEXT"),
        ("created_by", "INTEGER"),
        ("meeting_scope", "TEXT NOT NULL DEFAULT 'Department'"),
    ]:
        try:
            cur.execute(f"ALTER TABLE meetings ADD COLUMN {column} {definition}")
        except sqlite3.OperationalError:
            pass

    cur.execute("""
        CREATE TABLE IF NOT EXISTS meeting_participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER NOT NULL,
            staff_id INTEGER NOT NULL,
            invitation_status TEXT NOT NULL DEFAULT 'Pending',
            attendance_status TEXT NOT NULL DEFAULT 'Not Recorded',
            response_note TEXT,
            responded_at TIMESTAMP,
            UNIQUE(meeting_id, staff_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS meeting_minutes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER NOT NULL UNIQUE,
            minutes_text TEXT,
            prepared_by INTEGER,
            approved_by INTEGER,
            approval_status TEXT NOT NULL DEFAULT 'Draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS meeting_decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER NOT NULL,
            decision_text TEXT NOT NULL,
            responsible_staff_id INTEGER,
            due_date TEXT,
            status TEXT NOT NULL DEFAULT 'Open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS meeting_action_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER NOT NULL,
            action_text TEXT NOT NULL,
            responsible_staff_id INTEGER,
            due_date TEXT,
            priority TEXT NOT NULL DEFAULT 'Normal',
            status TEXT NOT NULL DEFAULT 'Open',
            completion_note TEXT,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_meeting_date
        ON meetings(meeting_date, start_time)
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_meeting_participant
        ON meeting_participants(staff_id, meeting_id)
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_meeting_actions
        ON meeting_action_items(responsible_staff_id, due_date, status)
    """)

    con.commit()
    con.close()


# ============================================================
# STAFF HELPERS
# ============================================================

def get_staff(staff_id):
    con = db()
    row = con.execute("""
        SELECT id, full_name, username, role, status
        FROM staff_users
        WHERE id = ?
        LIMIT 1
    """, (staff_id,)).fetchone()
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


def is_admin(staff_id):
    person = get_staff(staff_id)
    return bool(
        person
        and person["status"] == "Active"
        and person["role"] in ADMIN_ROLES
    )


def staff_label(person):
    return f"{person['full_name']} — {person['role']}"


def get_meeting_permission(staff_id):
    con = db()
    row = con.execute("""
        SELECT staff_id, department, can_organize
        FROM meeting_permissions
        WHERE staff_id=?
        LIMIT 1
    """, (staff_id,)).fetchone()
    con.close()
    return row


def can_organize_department_meeting(staff_id, department):
    person = get_staff(staff_id)
    if not person or person["status"] != "Active":
        return False, "Active staff account required."

    if person["role"] in DEPARTMENT_MEETING_ADMIN_ROLES:
        return True, "Administrator permission granted."

    permission = get_meeting_permission(staff_id)
    if not permission or not permission["can_organize"]:
        return False, "You have not been authorized to organize department meetings."

    assigned = (permission["department"] or "").strip()
    requested = (department or "").strip()
    if not assigned or assigned.casefold() != requested.casefold():
        return False, "You may only organize meetings for your authorized department."

    return True, "Department meeting permission granted."


def get_authorized_participants(staff_id, department):
    person = get_staff(staff_id)
    people = get_active_staff()
    if not person:
        return []
    if person["role"] in DEPARTMENT_MEETING_ADMIN_ROLES:
        return people

    permission = get_meeting_permission(staff_id)
    if not permission or not permission["can_organize"]:
        return []

    # Current staff_users V1 has no department column. Until the Staff
    # Directory gets the department field, an authorized department
    # organizer can invite staff explicitly selected by the administrator.
    # This keeps authorization enforced without inventing department data.
    return people


def staff_map():
    return {staff_label(p): p["id"] for p in get_active_staff()}


# ============================================================
# NOTIFICATIONS
# ============================================================

def notify(user_id, title, message, priority="normal"):
    try:
        from pages.notification_centre import create_notification

        create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="meeting",
            priority=priority,
            related_type="meeting",
        )
        return True
    except Exception:
        return False


# ============================================================
# AI APPOINTMENT INTEGRATION
# ============================================================

def sync_ai_appointment(
    staff_id,
    meeting_id,
    title,
    meeting_date,
    start_time,
    end_time,
    location,
    purpose,
    created_by,
):
    """
    Create an appointment record for the AI Staff Assistant.

    We use the existing staff_appointments table created by the
    AI Staff Assistant. If the table does not exist yet, create
    the compatible foundation here too.
    """
    con = db()

    con.execute("""
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

    # Older AI Assistant versions created staff_appointments without
    # source_meeting_id. Add the bridge column before querying it.
    try:
        con.execute("""
            ALTER TABLE staff_appointments
            ADD COLUMN source_meeting_id INTEGER
        """)
    except sqlite3.OperationalError:
        # Column already exists.
        pass

    existing = con.execute("""
        SELECT id
        FROM staff_appointments
        WHERE staff_id = ?
          AND source_meeting_id = ?
        LIMIT 1
    """, (staff_id, meeting_id)).fetchone()

    if existing:
        con.execute("""
            UPDATE staff_appointments
            SET title = ?,
                appointment_date = ?,
                start_time = ?,
                expected_end_time = ?,
                location = ?,
                notes = ?,
                status = 'Scheduled'
            WHERE id = ?
        """, (
            f"Meeting: {title}",
            meeting_date,
            start_time,
            end_time or "",
            location or "",
            purpose or "",
            existing["id"],
        ))
        appointment_id = existing["id"]
    else:
        cur = con.cursor()
        cur.execute("""
            INSERT INTO staff_appointments
            (
                staff_id,
                title,
                appointment_date,
                start_time,
                expected_end_time,
                location,
                contact_person,
                notes,
                status,
                created_by,
                source_meeting_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Scheduled', ?, ?)
        """, (
            staff_id,
            f"Meeting: {title}",
            meeting_date,
            start_time,
            end_time or "",
            location or "",
            "",
            purpose or "",
            created_by,
            meeting_id,
        ))
        appointment_id = cur.lastrowid

    con.commit()
    con.close()
    return appointment_id


def cancel_ai_appointments(meeting_id):
    con = db()

    try:
        con.execute("""
            UPDATE staff_appointments
            SET status = 'Cancelled'
            WHERE source_meeting_id = ?
        """, (meeting_id,))
    except sqlite3.OperationalError:
        # Older AI table may not yet have the bridge column.
        pass

    con.commit()
    con.close()


# ============================================================
# MEETING CREATION
# ============================================================

def create_meeting(
    title, meeting_date, start_time, end_time, location, meeting_link,
    organizer_id, purpose, agenda, participant_ids,
    department="", meeting_scope="Department", created_by=None,
):
    if not title.strip():
        return False, "Meeting title is required."

    creator_id = created_by or organizer_id
    if meeting_scope == "Department":
        allowed, message = can_organize_department_meeting(
            creator_id, department
        )
        if not allowed:
            return False, message
    elif get_staff(creator_id)["role"] not in DEPARTMENT_MEETING_ADMIN_ROLES:
        return False, "Only authorized administrators can create organization-wide meetings."

    if not participant_ids:
        participant_ids = [organizer_id]
    if organizer_id not in participant_ids:
        participant_ids = [organizer_id] + participant_ids

    con = db()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO meetings
        (title, meeting_date, start_time, end_time, location, meeting_link,
         organizer_id, purpose, agenda, department, created_by, meeting_scope)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title.strip(), meeting_date, start_time, end_time, location.strip(),
        meeting_link.strip(), organizer_id, purpose.strip(), agenda.strip(),
        department.strip(), creator_id, meeting_scope,
    ))
    meeting_id = cur.lastrowid

    for staff_id in sorted(set(participant_ids)):
        cur.execute("""
            INSERT OR IGNORE INTO meeting_participants (meeting_id, staff_id)
            VALUES (?, ?)
        """, (meeting_id, staff_id))
    con.commit()
    con.close()

    for staff_id in sorted(set(participant_ids)):
        sync_ai_appointment(
            staff_id, meeting_id, title, meeting_date, start_time,
            end_time, location, purpose, organizer_id,
        )
        if staff_id != organizer_id:
            notify(
                staff_id, "📅 New Meeting Invitation",
                f"You have been added to '{title}' on {meeting_date} at {start_time}.",
            )

    notify(organizer_id, "📅 Meeting Created",
           f"Meeting '{title}' has been created successfully.")
    return True, meeting_id


# ============================================================
# QUERIES
# ============================================================

def get_meeting(meeting_id):
    con = db()
    row = con.execute("""
        SELECT
            m.*,
            s.full_name AS organizer_name,
            s.role AS organizer_role
        FROM meetings m
        LEFT JOIN staff_users s
            ON s.id = m.organizer_id
        WHERE m.id = ?
        LIMIT 1
    """, (meeting_id,)).fetchone()
    con.close()
    return row


def get_meetings_for_staff(staff_id, include_past=True):
    con = db()

    query = """
        SELECT
            m.*,
            s.full_name AS organizer_name,
            p.invitation_status,
            p.attendance_status
        FROM meetings m
        JOIN meeting_participants p
            ON p.meeting_id = m.id
        LEFT JOIN staff_users s
            ON s.id = m.organizer_id
        WHERE p.staff_id = ?
    """

    params = [staff_id]

    if not include_past:
        query += " AND m.meeting_date >= ?"
        params.append(date.today().isoformat())

    query += " ORDER BY m.meeting_date DESC, m.start_time DESC"

    rows = con.execute(query, params).fetchall()
    con.close()
    return rows


def get_all_meetings():
    con = db()
    rows = con.execute("""
        SELECT
            m.*,
            s.full_name AS organizer_name,
            COUNT(p.id) AS participant_count
        FROM meetings m
        LEFT JOIN staff_users s
            ON s.id = m.organizer_id
        LEFT JOIN meeting_participants p
            ON p.meeting_id = m.id
        GROUP BY m.id
        ORDER BY m.meeting_date DESC, m.start_time DESC
    """).fetchall()
    con.close()
    return rows


def get_participants(meeting_id):
    con = db()
    rows = con.execute("""
        SELECT
            p.*,
            s.full_name,
            s.username,
            s.role
        FROM meeting_participants p
        JOIN staff_users s
            ON s.id = p.staff_id
        WHERE p.meeting_id = ?
        ORDER BY s.full_name
    """, (meeting_id,)).fetchall()
    con.close()
    return rows


# ============================================================
# RSVP / ATTENDANCE
# ============================================================

def update_rsvp(meeting_id, staff_id, response, note=""):
    allowed = {"Accepted", "Declined", "Tentative"}
    if response not in allowed:
        return False, "Invalid meeting response."

    con = db()

    row = con.execute("""
        SELECT id
        FROM meeting_participants
        WHERE meeting_id = ? AND staff_id = ?
        LIMIT 1
    """, (meeting_id, staff_id)).fetchone()

    if not row:
        con.close()
        return False, "You are not listed as a participant."

    con.execute("""
        UPDATE meeting_participants
        SET invitation_status = ?,
            response_note = ?,
            responded_at = CURRENT_TIMESTAMP
        WHERE meeting_id = ? AND staff_id = ?
    """, (
        response,
        note.strip(),
        meeting_id,
        staff_id,
    ))

    con.commit()
    con.close()

    meeting = get_meeting(meeting_id)

    if meeting:
        notify(
            meeting["organizer_id"],
            "📩 Meeting Response",
            f"{get_staff(staff_id)['full_name']} marked "
            f"'{meeting['title']}' as {response}.",
        )

    return True, "Meeting response saved."


def update_attendance(meeting_id, staff_id, attendance_status):
    allowed = {
        "Present",
        "Late",
        "Absent",
        "Excused",
        "Not Recorded",
    }

    if attendance_status not in allowed:
        return False, "Invalid attendance status."

    con = db()
    row = con.execute("""
        SELECT id
        FROM meeting_participants
        WHERE meeting_id = ? AND staff_id = ?
        LIMIT 1
    """, (meeting_id, staff_id)).fetchone()

    if not row:
        con.close()
        return False, "Participant not found."

    con.execute("""
        UPDATE meeting_participants
        SET attendance_status = ?
        WHERE meeting_id = ? AND staff_id = ?
    """, (
        attendance_status,
        meeting_id,
        staff_id,
    ))

    con.commit()
    con.close()

    return True, "Meeting attendance updated."


# ============================================================
# MINUTES / DECISIONS / ACTION ITEMS
# ============================================================

def save_minutes(meeting_id, minutes_text, prepared_by):
    con = db()

    existing = con.execute("""
        SELECT id
        FROM meeting_minutes
        WHERE meeting_id = ?
        LIMIT 1
    """, (meeting_id,)).fetchone()

    if existing:
        con.execute("""
            UPDATE meeting_minutes
            SET minutes_text = ?,
                prepared_by = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE meeting_id = ?
        """, (
            minutes_text,
            prepared_by,
            meeting_id,
        ))
    else:
        con.execute("""
            INSERT INTO meeting_minutes
            (
                meeting_id,
                minutes_text,
                prepared_by
            )
            VALUES (?, ?, ?)
        """, (
            meeting_id,
            minutes_text,
            prepared_by,
        ))

    con.commit()
    con.close()


def get_minutes(meeting_id):
    con = db()
    row = con.execute("""
        SELECT
            mm.*,
            s.full_name AS prepared_by_name
        FROM meeting_minutes mm
        LEFT JOIN staff_users s
            ON s.id = mm.prepared_by
        WHERE mm.meeting_id = ?
        LIMIT 1
    """, (meeting_id,)).fetchone()
    con.close()
    return row


def add_decision(
    meeting_id,
    decision_text,
    responsible_staff_id=None,
    due_date="",
):
    if not decision_text.strip():
        return False, "Decision text is required."

    con = db()
    cur = con.cursor()

    cur.execute("""
        INSERT INTO meeting_decisions
        (
            meeting_id,
            decision_text,
            responsible_staff_id,
            due_date
        )
        VALUES (?, ?, ?, ?)
    """, (
        meeting_id,
        decision_text.strip(),
        responsible_staff_id,
        due_date,
    ))

    rid = cur.lastrowid
    con.commit()
    con.close()

    if responsible_staff_id:
        meeting = get_meeting(meeting_id)
        if meeting:
            notify(
                responsible_staff_id,
                "📌 New Meeting Decision",
                f"You are responsible for a decision from "
                f"'{meeting['title']}'.",
            )

    return True, rid


def add_action_item(
    meeting_id,
    action_text,
    responsible_staff_id=None,
    due_date="",
    priority="Normal",
):
    if not action_text.strip():
        return False, "Action item is required."

    con = db()
    cur = con.cursor()

    cur.execute("""
        INSERT INTO meeting_action_items
        (
            meeting_id,
            action_text,
            responsible_staff_id,
            due_date,
            priority
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        meeting_id,
        action_text.strip(),
        responsible_staff_id,
        due_date,
        priority,
    ))

    rid = cur.lastrowid
    con.commit()
    con.close()

    if responsible_staff_id:
        meeting = get_meeting(meeting_id)
        if meeting:
            notify(
                responsible_staff_id,
                "📌 New Meeting Action",
                f"You have a new action from '{meeting['title']}'."
                + (
                    f" Deadline: {due_date}."
                    if due_date else ""
                ),
            )

    return True, rid


def get_decisions(meeting_id):
    con = db()
    rows = con.execute("""
        SELECT
            d.*,
            s.full_name AS responsible_name
        FROM meeting_decisions d
        LEFT JOIN staff_users s
            ON s.id = d.responsible_staff_id
        WHERE d.meeting_id = ?
        ORDER BY d.id DESC
    """, (meeting_id,)).fetchall()
    con.close()
    return rows


def get_actions(meeting_id=None, staff_id=None):
    con = db()

    query = """
        SELECT
            a.*,
            s.full_name AS responsible_name,
            m.title AS meeting_title,
            m.meeting_date
        FROM meeting_action_items a
        LEFT JOIN staff_users s
            ON s.id = a.responsible_staff_id
        JOIN meetings m
            ON m.id = a.meeting_id
        WHERE 1=1
    """

    params = []

    if meeting_id:
        query += " AND a.meeting_id = ?"
        params.append(meeting_id)

    if staff_id:
        query += " AND a.responsible_staff_id = ?"
        params.append(staff_id)

    query += """
        ORDER BY
            CASE a.priority
                WHEN 'High' THEN 0
                WHEN 'Normal' THEN 1
                ELSE 2
            END,
            a.due_date ASC,
            a.id DESC
    """

    rows = con.execute(query, params).fetchall()
    con.close()
    return rows


def update_action_status(action_id, status, completion_note=""):
    allowed = {"Open", "In Progress", "Completed", "Cancelled"}

    if status not in allowed:
        return False, "Invalid action status."

    con = db()

    if status == "Completed":
        con.execute("""
            UPDATE meeting_action_items
            SET status = ?,
                completion_note = ?,
                completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            status,
            completion_note.strip(),
            action_id,
        ))
    else:
        con.execute("""
            UPDATE meeting_action_items
            SET status = ?,
                completion_note = ?
            WHERE id = ?
        """, (
            status,
            completion_note.strip(),
            action_id,
        ))

    con.commit()
    con.close()

    return True, "Action item updated."


def save_meeting_permission(staff_id, department, can_organize, updated_by):
    if not department.strip():
        return False, "Department name is required."
    con = db()
    con.execute("""
        INSERT INTO meeting_permissions
        (staff_id, department, can_organize, updated_by)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(staff_id) DO UPDATE SET
            department=excluded.department,
            can_organize=excluded.can_organize,
            updated_by=excluded.updated_by,
            updated_at=CURRENT_TIMESTAMP
    """, (staff_id, department.strip(), int(can_organize), updated_by))
    con.commit()
    con.close()
    return True, "Meeting permission saved."


def get_meeting_permissions():
    con = db()
    rows = con.execute("""
        SELECT mp.*, s.full_name, s.username, s.role
        FROM meeting_permissions mp
        JOIN staff_users s ON s.id=mp.staff_id
        ORDER BY s.full_name
    """).fetchall()
    con.close()
    return rows


# ============================================================
# DASHBOARD METRICS
# ============================================================

def dashboard_metrics(staff_id=None):
    con = db()
    today = date.today().isoformat()

    if staff_id:
        upcoming = con.execute("""
            SELECT COUNT(*)
            FROM meetings m
            JOIN meeting_participants p
                ON p.meeting_id = m.id
            WHERE p.staff_id = ?
              AND m.meeting_date >= ?
              AND m.status = 'Scheduled'
        """, (staff_id, today)).fetchone()[0]

        actions = con.execute("""
            SELECT COUNT(*)
            FROM meeting_action_items
            WHERE responsible_staff_id = ?
              AND status != 'Completed'
              AND status != 'Cancelled'
        """, (staff_id,)).fetchone()[0]

        overdue = con.execute("""
            SELECT COUNT(*)
            FROM meeting_action_items
            WHERE responsible_staff_id = ?
              AND due_date != ''
              AND due_date < ?
              AND status != 'Completed'
              AND status != 'Cancelled'
        """, (staff_id, today)).fetchone()[0]

        con.close()

        return {
            "upcoming": upcoming,
            "actions": actions,
            "overdue": overdue,
        }

    meetings = con.execute("""
        SELECT COUNT(*)
        FROM meetings
        WHERE meeting_date >= ?
          AND status = 'Scheduled'
    """, (today,)).fetchone()[0]

    open_actions = con.execute("""
        SELECT COUNT(*)
        FROM meeting_action_items
        WHERE status NOT IN ('Completed', 'Cancelled')
    """).fetchone()[0]

    overdue = con.execute("""
        SELECT COUNT(*)
        FROM meeting_action_items
        WHERE due_date != ?
          AND due_date < ?
          AND status NOT IN ('Completed', 'Cancelled')
    """, ("", today)).fetchone()[0]

    pending_rsvp = con.execute("""
        SELECT COUNT(*)
        FROM meeting_participants p
        JOIN meetings m ON m.id = p.meeting_id
        WHERE p.invitation_status = 'Pending'
          AND m.meeting_date >= ?
          AND m.status = 'Scheduled'
    """, (today,)).fetchone()[0]

    con.close()

    return {
        "upcoming": meetings,
        "actions": open_actions,
        "overdue": overdue,
        "pending_rsvp": pending_rsvp,
    }


# ============================================================
# STAFF INTERFACE
# ============================================================

def show_staff_meeting_centre(staff_id):
    init_database()

    person = get_staff(staff_id)

    if not person or person["status"] != "Active":
        st.error("Active staff account required.")
        return

    metrics = dashboard_metrics(staff_id)

    st.title("📅 Meeting Centre")
    st.caption(
        "Pan Ideate Africa — Meetings, Minutes, Decisions & Follow-up"
    )

    st.success(
        f"Signed in as: {person['full_name']} • {person['role']}"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("📅 Upcoming Meetings", metrics["upcoming"])
    c2.metric("📌 My Open Actions", metrics["actions"])
    c3.metric("⚠️ My Overdue Actions", metrics["overdue"])

    tabs = st.tabs([
        "📅 My Meetings",
        "📌 My Actions",
        "📝 Meeting Details",
    ])

    with tabs[0]:
        meetings = get_meetings_for_staff(
            staff_id,
            include_past=True,
        )

        if not meetings:
            st.info("You have no meetings recorded yet.")

        for meeting in meetings:
            with st.container(border=True):
                st.subheader(meeting["title"])

                st.write(
                    f"📅 **{meeting['meeting_date']}** • "
                    f"🕘 **{meeting['start_time']}**"
                )

                if meeting["end_time"]:
                    st.write(
                        f"Expected end: {meeting['end_time']}"
                    )

                if meeting["location"]:
                    st.write(
                        f"📍 {meeting['location']}"
                    )

                st.caption(
                    f"Organizer: {meeting['organizer_name']} • "
                    f"Invitation: {meeting['invitation_status']} • "
                    f"Attendance: {meeting['attendance_status']}"
                )

                if meeting["meeting_link"]:
                    st.write(
                        f"🔗 Meeting link: {meeting['meeting_link']}"
                    )

                b1, b2, b3 = st.columns(3)

                with b1:
                    if st.button(
                        "✅ Accept",
                        key=f"accept_{meeting['id']}",
                    ):
                        ok, msg = update_rsvp(
                            meeting["id"],
                            staff_id,
                            "Accepted",
                        )
                        (st.success if ok else st.error)(msg)
                        if ok:
                            st.rerun()

                with b2:
                    if st.button(
                        "❔ Tentative",
                        key=f"tentative_{meeting['id']}",
                    ):
                        ok, msg = update_rsvp(
                            meeting["id"],
                            staff_id,
                            "Tentative",
                        )
                        (st.success if ok else st.error)(msg)
                        if ok:
                            st.rerun()

                with b3:
                    if st.button(
                        "❌ Decline",
                        key=f"decline_{meeting['id']}",
                    ):
                        ok, msg = update_rsvp(
                            meeting["id"],
                            staff_id,
                            "Declined",
                        )
                        (st.success if ok else st.error)(msg)
                        if ok:
                            st.rerun()

    with tabs[1]:
        actions = get_actions(staff_id=staff_id)

        if not actions:
            st.success("✅ You have no open meeting action items.")

        for action in actions:
            overdue = (
                action["due_date"]
                and action["due_date"] < date.today().isoformat()
                and action["status"] not in ("Completed", "Cancelled")
            )

            title = (
                "🔴 OVERDUE — "
                if overdue else ""
            ) + action["action_text"]

            with st.container(border=True):
                st.write(f"**{title}**")
                st.caption(
                    f"Meeting: {action['meeting_title']} • "
                    f"Priority: {action['priority']}"
                )

                if action["due_date"]:
                    st.write(
                        f"Deadline: **{action['due_date']}**"
                    )

                status = st.selectbox(
                    "Status",
                    [
                        "Open",
                        "In Progress",
                        "Completed",
                        "Cancelled",
                    ],
                    index=[
                        "Open",
                        "In Progress",
                        "Completed",
                        "Cancelled",
                    ].index(action["status"]),
                    key=f"action_status_{action['id']}",
                )

                note = st.text_area(
                    "Completion / progress note",
                    value=action["completion_note"] or "",
                    key=f"action_note_{action['id']}",
                    height=80,
                )

                if st.button(
                    "💾 Update Action",
                    key=f"update_action_{action['id']}",
                ):
                    ok, msg = update_action_status(
                        action["id"],
                        status,
                        note,
                    )
                    (st.success if ok else st.error)(msg)
                    if ok:
                        st.rerun()

    with tabs[2]:
        meetings = get_meetings_for_staff(
            staff_id,
            include_past=True,
        )

        if not meetings:
            st.info("No meetings available.")
        else:
            labels = {
                f"#{m['id']} — {m['title']} — "
                f"{m['meeting_date']}": m["id"]
                for m in meetings
            }

            selected_label = st.selectbox(
                "Select meeting",
                list(labels.keys()),
            )

            meeting_id = labels[selected_label]
            meeting = get_meeting(meeting_id)

            if meeting:
                st.subheader(meeting["title"])

                st.write(
                    f"**Purpose:** "
                    f"{meeting['purpose'] or 'Not specified'}"
                )

                st.write(
                    f"**Agenda:** "
                    f"{meeting['agenda'] or 'No agenda recorded'}"
                )

                if meeting["location"]:
                    st.write(
                        f"📍 **Location:** {meeting['location']}"
                    )

                minutes = get_minutes(meeting_id)

                st.divider()
                st.subheader("📝 Minutes")

                if minutes and minutes["minutes_text"]:
                    st.write(minutes["minutes_text"])
                else:
                    st.info("Minutes have not been recorded yet.")

                st.subheader("📌 Decisions")

                decisions = get_decisions(meeting_id)

                if not decisions:
                    st.info("No decisions recorded.")
                else:
                    for decision in decisions:
                        st.write(
                            f"• {decision['decision_text']}"
                        )
                        st.caption(
                            f"Responsible: "
                            f"{decision['responsible_name'] or 'Unassigned'} "
                            f"• Status: {decision['status']}"
                        )

                st.subheader("📋 Action Points")

                actions = get_actions(meeting_id=meeting_id)

                if not actions:
                    st.info("No action points recorded.")
                else:
                    for action in actions:
                        st.write(
                            f"• **{action['action_text']}**"
                        )
                        st.caption(
                            f"Responsible: "
                            f"{action['responsible_name'] or 'Unassigned'} "
                            f"• Deadline: "
                            f"{action['due_date'] or 'Not set'} "
                            f"• Status: {action['status']}"
                        )


# ============================================================
# ADMIN INTERFACE
# ============================================================

def show_admin_meeting_centre(admin_id):
    init_database()

    if not is_admin(admin_id):
        st.error(
            "🔒 Authorized Administrator or Manager access required."
        )
        return

    person = get_staff(admin_id)
    metrics = dashboard_metrics()

    st.title("📅 Meeting Centre")
    st.caption(
        "Pan Ideate Africa — Organization-wide Meeting Management"
    )

    st.success(
        f"Meeting Centre active • "
        f"{person['full_name']} • {person['role']}"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("📅 Upcoming", metrics["upcoming"])
    c2.metric("📌 Open Actions", metrics["actions"])
    c3.metric("⚠️ Overdue", metrics["overdue"])
    c4.metric("📩 Pending RSVPs", metrics["pending_rsvp"])

    tabs = st.tabs([
        "📅 Meetings",
        "➕ Create Meeting",
        "📝 Minutes & Actions",
        "👥 Attendance",
        "🔐 Meeting Permissions",
    ])

    # --------------------------------------------------------
    # MEETINGS
    # --------------------------------------------------------
    with tabs[0]:
        meetings = get_all_meetings()

        if not meetings:
            st.info(
                "No meetings have been created yet. "
                "Use Create Meeting to add the first one."
            )

        for meeting in meetings:
            with st.expander(
                f"📅 {meeting['meeting_date']} "
                f"{meeting['start_time']} — "
                f"{meeting['title']}"
            ):
                st.write(
                    f"Organizer: **{meeting['organizer_name']}**"
                )
                st.write(
                    f"Participants: **{meeting['participant_count']}**"
                )
                if meeting["meeting_scope"]:
                    st.write(f"Scope: **{meeting['meeting_scope']}**")
                if meeting["department"]:
                    st.write(f"Department: **{meeting['department']}**")

                if meeting["location"]:
                    st.write(
                        f"📍 {meeting['location']}"
                    )

                st.write(
                    f"Status: **{meeting['status']}**"
                )

                if meeting["purpose"]:
                    st.write(
                        f"Purpose: {meeting['purpose']}"
                    )

                if meeting["meeting_link"]:
                    st.write(
                        f"🔗 {meeting['meeting_link']}"
                    )

    # --------------------------------------------------------
    # CREATE MEETING
    # --------------------------------------------------------
    with tabs[1]:
        admin_person = get_staff(admin_id)
        people = get_active_staff()
        permission = get_meeting_permission(admin_id)

        if admin_person["role"] in DEPARTMENT_MEETING_ADMIN_ROLES:
            scope = st.selectbox("Meeting Scope", ["Department", "Organization-wide"], key="meeting_scope")
            if scope == "Department":
                department = st.text_input("Department", placeholder="e.g. Agriculture").strip()
            else:
                department = "Organization-wide"
            organizer_id = admin_id
            organizer_display = admin_person["full_name"]
            participant_people = people
        else:
            scope = "Department"
            department = permission["department"] if permission else ""
            organizer_id = admin_id
            organizer_display = admin_person["full_name"]
            participant_people = get_authorized_participants(admin_id, department)
            if not department or not permission or not permission["can_organize"]:
                st.warning("You are not authorized to organize department meetings. An Administrator must grant this permission.")
            else:
                st.info(f"Authorized department: **{department}**")

        if people and (admin_person["role"] in DEPARTMENT_MEETING_ADMIN_ROLES or (permission and permission["can_organize"])):
            people_map = {staff_label(p): p["id"] for p in participant_people if p["id"] != organizer_id}
            with st.form("create_meeting_form"):
                st.write(f"**Organizer:** {organizer_display}")
                st.write(f"**Scope:** {scope} • **Department:** {department}")
                selected_participants = st.multiselect("Participants", list(people_map.keys()))
                title = st.text_input("Meeting Title", placeholder="e.g. Weekly Department Meeting")
                c1, c2 = st.columns(2)
                with c1:
                    meeting_date = st.date_input("Meeting Date", value=date.today())
                with c2:
                    start_time = st.time_input("Start Time")
                end_time = st.text_input("Expected End Time", placeholder="e.g. 11:30")
                location = st.text_input("Location")
                meeting_link = st.text_input("Meeting / Video Link (optional)")
                purpose = st.text_area("Purpose", height=80)
                agenda = st.text_area("Agenda", height=140, placeholder="1. Opening\n2. Previous action points\n3. New matters\n4. Decisions\n5. Closing")
                create = st.form_submit_button("📅 Create Meeting", type="primary", use_container_width=True)
                if create:
                    participant_ids = [people_map[label] for label in selected_participants]
                    ok, result = create_meeting(
                        title, meeting_date.isoformat(), start_time.strftime("%H:%M"),
                        end_time.strip(), location, meeting_link, organizer_id,
                        purpose, agenda, participant_ids, department, scope, admin_id,
                    )
                    if ok:
                        st.success(f"Meeting #{result} created successfully.")
                        st.rerun()
                    else:
                        st.error(result)

    # --------------------------------------------------------
    # MINUTES / ACTIONS
    # --------------------------------------------------------
    with tabs[2]:
        meetings = get_all_meetings()

        if not meetings:
            st.info("Create a meeting first.")
        else:
            labels = {
                f"#{m['id']} — {m['title']} — "
                f"{m['meeting_date']}": m["id"]
                for m in meetings
            }

            selected_label = st.selectbox(
                "Select Meeting",
                list(labels.keys()),
                key="admin_minutes_meeting",
            )

            meeting_id = labels[selected_label]
            meeting = get_meeting(meeting_id)

            if meeting:
                st.subheader(
                    f"📝 {meeting['title']}"
                )

                current_minutes = get_minutes(meeting_id)

                minutes_text = st.text_area(
                    "Meeting Minutes",
                    value=(
                        current_minutes["minutes_text"]
                        if current_minutes
                        else ""
                    ),
                    height=220,
                    key=f"minutes_{meeting_id}",
                )

                if st.button(
                    "💾 Save Minutes",
                    key=f"save_minutes_{meeting_id}",
                    type="primary",
                ):
                    save_minutes(
                        meeting_id,
                        minutes_text,
                        admin_id,
                    )
                    st.success("Meeting minutes saved.")
                    st.rerun()

                st.divider()

                st.subheader("📌 Add Decision")

                people_map = staff_map()

                with st.form(
                    f"decision_form_{meeting_id}"
                ):
                    decision_text = st.text_area(
                        "Decision",
                    )

                    responsible = st.selectbox(
                        "Responsible Person",
                        ["Unassigned"] + list(people_map.keys()),
                    )

                    due_date = st.date_input(
                        "Decision Due Date",
                        value=date.today(),
                        key=f"decision_due_{meeting_id}",
                    )

                    save_decision = st.form_submit_button(
                        "📌 Save Decision",
                        use_container_width=True,
                    )

                    if save_decision:
                        responsible_id = (
                            None
                            if responsible == "Unassigned"
                            else people_map[responsible]
                        )

                        ok, result = add_decision(
                            meeting_id,
                            decision_text,
                            responsible_id,
                            due_date.isoformat(),
                        )

                        if ok:
                            st.success(
                                f"Decision #{result} saved."
                            )
                            st.rerun()
                        else:
                            st.error(result)

                st.divider()

                st.subheader("📋 Add Action Point")

                with st.form(
                    f"action_form_{meeting_id}"
                ):
                    action_text = st.text_area(
                        "Action Point",
                    )

                    responsible = st.selectbox(
                        "Responsible Person",
                        ["Unassigned"] + list(people_map.keys()),
                        key=f"action_person_{meeting_id}",
                    )

                    c1, c2 = st.columns(2)

                    with c1:
                        action_due = st.date_input(
                            "Deadline",
                            value=date.today(),
                            key=f"action_due_{meeting_id}",
                        )

                    with c2:
                        priority = st.selectbox(
                            "Priority",
                            ["Low", "Normal", "High"],
                            index=1,
                            key=f"action_priority_{meeting_id}",
                        )

                    save_action = st.form_submit_button(
                        "📋 Save Action Point",
                        use_container_width=True,
                    )

                    if save_action:
                        responsible_id = (
                            None
                            if responsible == "Unassigned"
                            else people_map[responsible]
                        )

                        ok, result = add_action_item(
                            meeting_id,
                            action_text,
                            responsible_id,
                            action_due.isoformat(),
                            priority,
                        )

                        if ok:
                            st.success(
                                f"Action #{result} saved."
                            )
                            st.rerun()
                        else:
                            st.error(result)

                st.divider()

                st.subheader("Current Action Points")

                for action in get_actions(meeting_id):
                    st.write(
                        f"**{action['action_text']}**"
                    )
                    st.caption(
                        f"{action['responsible_name'] or 'Unassigned'} • "
                        f"Due: {action['due_date'] or 'Not set'} • "
                        f"{action['priority']} • "
                        f"{action['status']}"
                    )

    # --------------------------------------------------------
    # ATTENDANCE
    # --------------------------------------------------------
    with tabs[3]:
        meetings = get_all_meetings()

        if not meetings:
            st.info("No meetings available.")
        else:
            labels = {
                f"#{m['id']} — {m['title']} — "
                f"{m['meeting_date']}": m["id"]
                for m in meetings
            }

            selected_label = st.selectbox(
                "Select Meeting",
                list(labels.keys()),
                key="admin_attendance_meeting",
            )

            meeting_id = labels[selected_label]
            participants = get_participants(meeting_id)

            if not participants:
                st.info(
                    "No participants have been added."
                )

            for participant in participants:
                with st.container(border=True):
                    c1, c2 = st.columns([2, 1])

                    with c1:
                        st.write(
                            f"**{participant['full_name']}**"
                        )
                        st.caption(
                            f"{participant['role']} • "
                            f"Invitation: "
                            f"{participant['invitation_status']}"
                        )

                    with c2:
                        statuses = [
                            "Not Recorded",
                            "Present",
                            "Late",
                            "Absent",
                            "Excused",
                        ]

                        current = participant[
                            "attendance_status"
                        ]

                        index = (
                            statuses.index(current)
                            if current in statuses
                            else 0
                        )

                        status = st.selectbox(
                            "Attendance",
                            statuses,
                            index=index,
                            key=(
                                f"meeting_att_{meeting_id}_"
                                f"{participant['staff_id']}"
                            ),
                        )

                        if st.button(
                            "Save",
                            key=(
                                f"meeting_att_save_{meeting_id}_"
                                f"{participant['staff_id']}"
                            ),
                        ):
                            ok, msg = update_attendance(
                                meeting_id,
                                participant["staff_id"],
                                status,
                            )
                            (st.success if ok else st.error)(msg)
                            if ok:
                                st.rerun()


    # --------------------------------------------------------
    # MEETING PERMISSIONS
    # --------------------------------------------------------
    with tabs[4]:
        st.subheader("🔐 Department Meeting Permissions")
        st.caption("Only authorized administrators can grant or remove department meeting-organizer access.")
        people = get_active_staff()
        if people:
            people_map = {staff_label(p): p["id"] for p in people}
            with st.form("meeting_permission_form"):
                selected = st.selectbox("Staff Member", list(people_map.keys()))
                department = st.text_input("Authorized Department", placeholder="e.g. Agriculture")
                can_organize = st.checkbox("Allow this staff member to organize department meetings")
                save = st.form_submit_button("💾 Save Meeting Permission", type="primary", use_container_width=True)
                if save:
                    ok, msg = save_meeting_permission(
                        people_map[selected], department, can_organize, admin_id
                    )
                    (st.success if ok else st.error)(msg)
                    if ok:
                        st.rerun()

        rows = get_meeting_permissions()
        if rows:
            st.divider()
            st.subheader("Current Department Meeting Permissions")
            for row in rows:
                status = "✅ Authorized" if row["can_organize"] else "🚫 Not Authorized"
                st.write(f"**{row['full_name']}** — {row['department']} — {status}")
        else:
            st.info("No department meeting permissions have been configured yet.")


# ============================================================
# GENERIC ENTRY POINTS
# ============================================================

def show_staff(staff_id):
    show_staff_meeting_centre(staff_id)


def show_admin(admin_id):
    show_admin_meeting_centre(admin_id)


def show(user_id=None, admin=False):
    if admin:
        show_admin_meeting_centre(user_id)
    else:
        show_staff_meeting_centre(user_id)


init_database()
