
import sqlite3
from pathlib import Path
from datetime import date, datetime

import streamlit as st

from pages.notification_centre import create_notification


# ============================================================
# PAN IDEATE AFRICA — TASK & PROJECT MANAGER
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "pan_ideate.db"


# ------------------------------------------------------------
# DATABASE
# ------------------------------------------------------------

def get_connection():
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_task_database():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            manager_id INTEGER,
            priority TEXT NOT NULL DEFAULT 'normal',
            status TEXT NOT NULL DEFAULT 'not_started',
            progress INTEGER NOT NULL DEFAULT 0,
            start_date TEXT,
            due_date TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            project_id INTEGER,
            assigned_to INTEGER,
            created_by INTEGER,
            priority TEXT NOT NULL DEFAULT 'normal',
            status TEXT NOT NULL DEFAULT 'not_started',
            progress INTEGER NOT NULL DEFAULT 0,
            start_date TEXT,
            due_date TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        )
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to
        ON tasks(assigned_to)
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_project
        ON tasks(project_id)
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_due_date
        ON tasks(due_date)
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS task_notification_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            notification_key TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(task_id, user_id, notification_key)
        )
    """)

    conn.commit()
    conn.close()


# ------------------------------------------------------------
# STAFF HELPERS
# ------------------------------------------------------------

def get_staff_members():
    """Read active staff from the existing Staff Management database."""
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT id, full_name, username, role, status
            FROM staff_users
            WHERE status = 'Active'
            ORDER BY full_name
        """).fetchall()
    except sqlite3.OperationalError:
        rows = []

    conn.close()
    return rows


def get_user_role(user_id):
    if not user_id:
        return None

    conn = get_connection()

    try:
        row = conn.execute("""
            SELECT role
            FROM staff_users
            WHERE id = ? AND status = 'Active'
            LIMIT 1
        """, (user_id,)).fetchone()
    except sqlite3.OperationalError:
        row = None

    conn.close()
    return row["role"] if row else None


def staff_label(person):
    return f"{person['full_name']} (@{person['username']}) — {person['role']}"


# ------------------------------------------------------------
# TASK NOTIFICATIONS
# ------------------------------------------------------------

def _task_notification_once(task_id, user_id, notification_key,
                            title, message, priority="normal"):
    """Send a task notification once for a specific event."""
    if not task_id or not user_id:
        return False

    init_task_database()
    conn = get_connection()

    existing = conn.execute("""
        SELECT id
        FROM task_notification_log
        WHERE task_id = ?
          AND user_id = ?
          AND notification_key = ?
        LIMIT 1
    """, (
        task_id,
        user_id,
        notification_key,
    )).fetchone()

    if existing:
        conn.close()
        return False

    try:
        create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="task",
            priority=priority,
            related_id=task_id,
            related_type="task",
        )

        conn.execute("""
            INSERT INTO task_notification_log
            (task_id, user_id, notification_key)
            VALUES (?, ?, ?)
        """, (
            task_id,
            user_id,
            notification_key,
        ))

        conn.commit()
        conn.close()
        return True

    except Exception:
        conn.close()
        return False


def notify_task_assigned(task_id, assigned_to, title, priority):
    priority_map = {
        "low": "low",
        "normal": "normal",
        "high": "high",
        "urgent": "urgent",
    }

    return _task_notification_once(
        task_id,
        assigned_to,
        "assigned",
        "📋 New Task Assigned",
        f"You have been assigned the task: {title}",
        priority_map.get(priority, "normal"),
    )


def notify_task_completed(task_id, manager_id, title):
    return _task_notification_once(
        task_id,
        manager_id,
        "completed",
        "✅ Task Completed",
        f"The task '{title}' has been completed.",
        "normal",
    )


def notify_task_updated(task_id, manager_id, title):
    return _task_notification_once(
        task_id,
        manager_id,
        "updated",
        "🔄 Task Updated",
        f"The task '{title}' has been updated by the assigned employee.",
        "normal",
    )


def check_task_deadlines():
    """
    Generate one notification when a task is due today or tomorrow,
    and one notification when it becomes overdue.

    This is intentionally event-based and de-duplicated. It can be
    called whenever the Task Manager loads without repeatedly sending
    the same alert.
    """
    init_task_database()

    today = date.today()

    conn = get_connection()
    tasks = conn.execute("""
        SELECT
            t.id,
            t.title,
            t.assigned_to,
            t.created_by,
            t.due_date,
            t.status
        FROM tasks t
        WHERE t.due_date IS NOT NULL
          AND t.due_date != ''
          AND t.status != 'completed'
    """).fetchall()
    conn.close()

    sent = 0

    for task in tasks:
        try:
            due = date.fromisoformat(str(task["due_date"]))
        except ValueError:
            continue

        days_left = (due - today).days

        if days_left == 0:
            if _task_notification_once(
                task["id"],
                task["assigned_to"],
                "due_today",
                "⏰ Task Due Today",
                f"Your task '{task['title']}' is due today.",
                "high",
            ):
                sent += 1

        elif days_left == 1:
            if _task_notification_once(
                task["id"],
                task["assigned_to"],
                "due_tomorrow",
                "⏰ Task Due Tomorrow",
                f"Your task '{task['title']}' is due tomorrow.",
                "normal",
            ):
                sent += 1

        elif days_left < 0:
            if _task_notification_once(
                task["id"],
                task["assigned_to"],
                "overdue",
                "🔴 Task Overdue",
                f"Your task '{task['title']}' is overdue.",
                "urgent",
            ):
                sent += 1

            if task["created_by"] != task["assigned_to"]:
                if _task_notification_once(
                    task["id"],
                    task["created_by"],
                    "manager_overdue",
                    "🔴 Staff Task Overdue",
                    f"The task '{task['title']}' is overdue.",
                    "high",
                ):
                    sent += 1

    return sent


# ------------------------------------------------------------
# PROJECT HELPERS
# ------------------------------------------------------------

def get_projects():
    conn = get_connection()

    rows = conn.execute("""
        SELECT
            p.*,
            s.full_name AS manager_name,
            s.username AS manager_username
        FROM projects p
        LEFT JOIN staff_users s
            ON p.manager_id = s.id
        ORDER BY p.created_at DESC, p.id DESC
    """).fetchall()

    conn.close()
    return rows


def create_project(
    name,
    description,
    manager_id,
    priority,
    start_date,
    due_date,
    created_by,
):
    conn = get_connection()

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO projects
        (name, description, manager_id, priority, status,
         progress, start_date, due_date, created_by)
        VALUES (?, ?, ?, ?, 'not_started', 0, ?, ?, ?)
    """, (
        name.strip(),
        description.strip(),
        manager_id,
        priority,
        start_date,
        due_date,
        created_by,
    ))

    project_id = cur.lastrowid
    conn.commit()
    conn.close()

    return project_id


def update_project_progress(project_id, progress):
    progress = max(0, min(100, int(progress)))

    if progress == 100:
        status = "completed"
    elif progress > 0:
        status = "in_progress"
    else:
        status = "not_started"

    conn = get_connection()

    conn.execute("""
        UPDATE projects
        SET progress = ?,
            status = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (progress, status, project_id))

    conn.commit()
    conn.close()


# ------------------------------------------------------------
# TASK HELPERS
# ------------------------------------------------------------

def get_tasks(user_id=None, role=None):
    conn = get_connection()

    base_query = """
        SELECT
            t.*,
            p.name AS project_name,
            s.full_name AS assignee_name,
            s.username AS assignee_username
        FROM tasks t
        LEFT JOIN projects p
            ON t.project_id = p.id
        LEFT JOIN staff_users s
            ON t.assigned_to = s.id
    """

    params = []

    # Ordinary staff see their own tasks.
    # Managers/Super Admin can see the team.
    if user_id and role not in {"Super Admin", "Manager"}:
        base_query += " WHERE t.assigned_to = ? "
        params.append(user_id)

    base_query += """
        ORDER BY
            CASE t.status
                WHEN 'overdue' THEN 1
                WHEN 'in_progress' THEN 2
                WHEN 'under_review' THEN 3
                WHEN 'not_started' THEN 4
                WHEN 'completed' THEN 5
                WHEN 'on_hold' THEN 6
                ELSE 7
            END,
            CASE
                WHEN t.due_date IS NULL OR t.due_date = '' THEN 1
                ELSE 0
            END,
            t.due_date ASC,
            t.id DESC
    """

    rows = conn.execute(base_query, params).fetchall()
    conn.close()
    return rows


def create_task(
    title,
    description,
    project_id,
    assigned_to,
    created_by,
    priority,
    start_date,
    due_date,
):
    conn = get_connection()

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tasks
        (title, description, project_id, assigned_to, created_by,
         priority, status, progress, start_date, due_date)
        VALUES (?, ?, ?, ?, ?, ?, 'not_started', 0, ?, ?)
    """, (
        title.strip(),
        description.strip(),
        project_id,
        assigned_to,
        created_by,
        priority,
        start_date,
        due_date,
    ))

    task_id = cur.lastrowid
    conn.commit()
    conn.close()

    notify_task_assigned(
        task_id,
        assigned_to,
        title.strip(),
        priority,
    )

    return task_id


def update_task(task_id, status, progress, notes):
    progress = max(0, min(100, int(progress)))

    if status == "completed":
        progress = 100
    elif status == "not_started":
        progress = 0
    elif status == "in_progress" and progress == 0:
        progress = 1

    conn = get_connection()

    conn.execute("""
        UPDATE tasks
        SET status = ?,
            progress = ?,
            notes = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        status,
        progress,
        notes.strip(),
        task_id,
    ))

    conn.commit()
    conn.close()

    if status == "completed" and task_id:
        # The creator is notified once when the task reaches completion.
        conn2 = get_connection()
        row = conn2.execute("""
            SELECT created_by, title, assigned_to
            FROM tasks
            WHERE id = ?
            LIMIT 1
        """, (task_id,)).fetchone()
        conn2.close()

        if row:
            notify_task_completed(
                task_id,
                row["created_by"],
                row["title"],
            )

    return True


def refresh_overdue_tasks():
    """Mark unfinished tasks past their due date as overdue."""
    today = date.today().isoformat()

    conn = get_connection()

    conn.execute("""
        UPDATE tasks
        SET status = 'overdue',
            updated_at = CURRENT_TIMESTAMP
        WHERE due_date IS NOT NULL
          AND due_date != ''
          AND due_date < ?
          AND status NOT IN ('completed', 'on_hold')
    """, (today,))

    conn.commit()
    conn.close()


# ------------------------------------------------------------
# DASHBOARD
# ------------------------------------------------------------

def show_dashboard(tasks, projects):
    total_projects = len(projects)
    active_projects = sum(
        p["status"] in {"in_progress", "under_review"}
        for p in projects
    )
    completed_projects = sum(
        p["status"] == "completed"
        for p in projects
    )

    total_tasks = len(tasks)
    pending_tasks = sum(
        t["status"] not in {"completed", "on_hold"}
        for t in tasks
    )
    overdue_tasks = sum(
        t["status"] == "overdue"
        for t in tasks
    )
    completed_tasks = sum(
        t["status"] == "completed"
        for t in tasks
    )

    st.markdown("## 📊 Task & Project Dashboard")

    cols = st.columns(6)

    metrics = [
        ("📁 Projects", total_projects),
        ("🚀 Active Projects", active_projects),
        ("✅ Completed Projects", completed_projects),
        ("📋 Tasks", total_tasks),
        ("⏳ Pending Tasks", pending_tasks),
        ("🔴 Overdue", overdue_tasks),
    ]

    for col, (label, value) in zip(cols, metrics):
        with col:
            st.metric(label, value)

    st.divider()

    if total_tasks:
        completion = round(
            (completed_tasks / total_tasks) * 100
        )
        st.progress(
            completion / 100,
            text=f"Overall task completion: {completion}%",
        )
    else:
        st.info("No tasks have been created yet.")


# ------------------------------------------------------------
# PROJECT CREATION
# ------------------------------------------------------------

def show_create_project(user_id, staff):
    st.markdown("## ➕ Create Project")

    if not staff:
        st.warning(
            "No active staff accounts were found. "
            "Create staff accounts first."
        )
        return

    staff_labels = [staff_label(p) for p in staff]

    with st.form("create_project_form"):
        name = st.text_input(
            "Project Name",
            placeholder="e.g. Iron Oxide Pigments Business Project",
        )

        description = st.text_area(
            "Project Description",
            placeholder="Describe the purpose and expected outcome...",
            height=120,
        )

        manager_label = st.selectbox(
            "Project Manager",
            staff_labels,
        )

        priority = st.selectbox(
            "Priority",
            [
                ("low", "🟢 Low"),
                ("normal", "🔵 Normal"),
                ("high", "🟠 High"),
                ("urgent", "🔴 Urgent"),
            ],
            format_func=lambda x: x[1],
        )

        start_date = st.date_input(
            "Start Date",
            value=date.today(),
        )

        due_date = st.date_input(
            "Target Completion Date",
            value=date.today(),
        )

        submit = st.form_submit_button(
            "📁 Create Project",
            use_container_width=True,
            type="primary",
        )

    if submit:
        if not name.strip():
            st.error("Please enter a project name.")
            return

        if due_date < start_date:
            st.error(
                "Target completion date cannot be before the start date."
            )
            return

        manager = staff[
            staff_labels.index(manager_label)
        ]

        project_id = create_project(
            name,
            description,
            manager["id"],
            priority[0],
            start_date.isoformat(),
            due_date.isoformat(),
            user_id,
        )

        st.success(
            f"✅ Project created successfully. Project #{project_id}"
        )
        st.rerun()


# ------------------------------------------------------------
# TASK CREATION
# ------------------------------------------------------------

def show_create_task(user_id, staff, projects):
    st.markdown("## ➕ Create Task")

    if not staff:
        st.warning("No active staff accounts are available.")
        return

    staff_labels = [staff_label(p) for p in staff]

    project_options = [
        ("0", "No Project / General Task")
    ] + [
        (str(p["id"]), p["name"])
        for p in projects
    ]

    with st.form("create_task_form"):
        title = st.text_input(
            "Task Title",
            placeholder="e.g. Prepare pigment market analysis",
        )

        description = st.text_area(
            "Task Description",
            placeholder="Explain exactly what needs to be done...",
            height=120,
        )

        project_label = st.selectbox(
            "Project",
            project_options,
            format_func=lambda x: x[1],
        )

        assignee_label = st.selectbox(
            "Assign To",
            staff_labels,
        )

        priority = st.selectbox(
            "Priority",
            [
                ("low", "🟢 Low"),
                ("normal", "🔵 Normal"),
                ("high", "🟠 High"),
                ("urgent", "🔴 Urgent"),
            ],
            format_func=lambda x: x[1],
        )

        start_date = st.date_input(
            "Start Date",
            value=date.today(),
        )

        due_date = st.date_input(
            "Due Date",
            value=date.today(),
        )

        submit = st.form_submit_button(
            "📋 Create & Assign Task",
            use_container_width=True,
            type="primary",
        )

    if submit:
        if not title.strip():
            st.error("Please enter a task title.")
            return

        if due_date < start_date:
            st.error("Due date cannot be before the start date.")
            return

        assignee = staff[
            staff_labels.index(assignee_label)
        ]

        project_id = (
            int(project_label[0])
            if project_label[0] != "0"
            else None
        )

        task_id = create_task(
            title,
            description,
            project_id,
            assignee["id"],
            user_id,
            priority[0],
            start_date.isoformat(),
            due_date.isoformat(),
        )

        st.success(
            f"✅ Task #{task_id} created and assigned to "
            f"{assignee['full_name']}."
        )

        # Notification integration is intentionally prepared for
        # the next connection step. This module remains standalone
        # until the Task Manager is tested.
        st.rerun()


# ------------------------------------------------------------
# PROJECTS VIEW
# ------------------------------------------------------------

def show_projects(projects, staff):
    st.markdown("## 📁 Projects")

    if not projects:
        st.info(
            "No projects yet. Use 'Create Project' to add the first one."
        )
        return

    staff_lookup = {
        p["id"]: p
        for p in staff
    }

    for project in projects:
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 2, 2])

            with c1:
                st.markdown(
                    f"### 📁 {project['name']}"
                )
                st.write(
                    project["description"]
                    or "No project description provided."
                )

            with c2:
                st.caption("Status")
                st.write(
                    project["status"].replace("_", " ").title()
                )
                st.caption("Priority")
                st.write(
                    project["priority"].title()
                )

            with c3:
                st.caption("Project Manager")
                st.write(
                    project["manager_name"]
                    or "Not assigned"
                )
                st.caption("Due")
                st.write(
                    project["due_date"]
                    or "No deadline"
                )

            st.progress(
                project["progress"] / 100,
                text=f"Progress: {project['progress']}%",
            )

            new_progress = st.slider(
                "Update Project Progress",
                0,
                100,
                int(project["progress"]),
                key=f"project_progress_{project['id']}",
            )

            if new_progress != project["progress"]:
                if st.button(
                    "💾 Save Progress",
                    key=f"save_project_{project['id']}",
                ):
                    update_project_progress(
                        project["id"],
                        new_progress,
                    )
                    st.success("Project progress updated.")
                    st.rerun()


# ------------------------------------------------------------
# TASKS VIEW
# ------------------------------------------------------------

def show_tasks(tasks):
    st.markdown("## 📋 Tasks")

    if not tasks:
        st.info("No tasks found.")
        return

    for task in tasks:
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 2, 2])

            with c1:
                st.markdown(
                    f"### 📋 {task['title']}"
                )

                if task["description"]:
                    st.write(task["description"])

                if task["project_name"]:
                    st.caption(
                        f"📁 Project: {task['project_name']}"
                    )

            with c2:
                st.caption("Assigned To")
                st.write(
                    task["assignee_name"]
                    or "Unassigned"
                )

                st.caption("Priority")
                st.write(
                    task["priority"].title()
                )

            with c3:
                st.caption("Status")
                st.write(
                    task["status"].replace("_", " ").title()
                )

                st.caption("Due")
                st.write(
                    task["due_date"]
                    or "No deadline"
                )

            st.progress(
                task["progress"] / 100,
                text=f"Progress: {task['progress']}%",
            )

            with st.expander("✏️ Update Task"):
                status_options = [
                    "not_started",
                    "in_progress",
                    "under_review",
                    "completed",
                    "on_hold",
                    "overdue",
                ]

                current_status = (
                    task["status"]
                    if task["status"] in status_options
                    else "not_started"
                )

                status = st.selectbox(
                    "Status",
                    status_options,
                    index=status_options.index(
                        current_status
                    ),
                    format_func=lambda x:
                        x.replace("_", " ").title(),
                    key=f"task_status_{task['id']}",
                )

                progress = st.slider(
                    "Progress",
                    0,
                    100,
                    int(task["progress"]),
                    key=f"task_progress_{task['id']}",
                )

                notes = st.text_area(
                    "Notes / Progress Update",
                    value=task["notes"] or "",
                    key=f"task_notes_{task['id']}",
                )

                if st.button(
                    "💾 Save Task Update",
                    key=f"save_task_{task['id']}",
                    use_container_width=True,
                ):
                    update_task(
                        task["id"],
                        status,
                        progress,
                        notes,
                    )
                    st.success("Task updated successfully.")
                    st.rerun()


# ------------------------------------------------------------
# MAIN PAGE
# ------------------------------------------------------------

def show_task_project_manager(user_id):
    init_task_database()
    refresh_overdue_tasks()
    check_task_deadlines()

    role = get_user_role(user_id)
    staff = get_staff_members()
    projects = get_projects()
    tasks = get_tasks(user_id, role)

    st.title("📋 Task & Project Manager")

    st.caption(
        "Pan Ideate Africa — Internal Digital Operations"
    )

    if not role:
        st.error(
            "Your active staff account could not be identified."
        )
        return

    st.info(
        f"Signed in as: **{role}**"
    )

    dashboard_tab, projects_tab, tasks_tab, create_project_tab, create_task_tab = st.tabs([
        "📊 Dashboard",
        "📁 Projects",
        "📋 Tasks",
        "➕ Create Project",
        "➕ Create Task",
    ])

    with dashboard_tab:
        show_dashboard(tasks, projects)

    with projects_tab:
        show_projects(projects, staff)

    with tasks_tab:
        show_tasks(tasks)

    with create_project_tab:
        if role in {"Super Admin", "Manager"}:
            show_create_project(user_id, staff)
        else:
            st.warning(
                "Project creation is available to Super Admin "
                "and Manager accounts."
            )

    with create_task_tab:
        if role in {"Super Admin", "Manager"}:
            show_create_task(user_id, staff, projects)
        else:
            st.warning(
                "Task assignment is available to Super Admin "
                "and Manager accounts."
            )


# ------------------------------------------------------------
# ADMIN CENTRE CONNECTION
# ------------------------------------------------------------

def show_admin_task_manager(user_id):
    """
    Entry point used by the Pan Ideate Africa Administration Centre.

    The Admin Centre expects this function name, while the main
    Task & Project Manager uses show_task_project_manager().
    This wrapper keeps both entry points connected to the same
    Task Manager without creating a second Task Manager.
    """
    return show_task_project_manager(user_id)



# Safe direct execution for testing this module alone.
if __name__ == "__main__":
    st.set_page_config(
        page_title="Task & Project Manager",
        page_icon="📋",
        layout="wide",
    )

    st.warning(
        "This is the standalone Task & Project Manager test page. "
        "The main Pan Ideate Africa app will supply the authenticated "
        "user ID when this module is connected."
    )

    test_user_id = st.number_input(
        "Test User ID",
        min_value=1,
        value=1,
        step=1,
    )

    show_task_project_manager(int(test_user_id))
