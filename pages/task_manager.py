import streamlit as st
from datetime import date, datetime

from utils.database import get_connection, get_all_staff
from pages.notification_centre import create_notification


PROJECT_STATUSES = [
    "Planning",
    "Active",
    "On Hold",
    "Completed",
    "Archived",
]

TASK_STATUSES = [
    "Not Started",
    "In Progress",
    "Blocked",
    "Completed",
]

PRIORITIES = [
    "Low",
    "Medium",
    "High",
    "Urgent",
]


def ensure_task_tables():
    """Create the project/task tables without changing existing tables."""
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'Planning',
            priority TEXT NOT NULL DEFAULT 'Medium',
            start_date DATE,
            due_date DATE,
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(created_by) REFERENCES staff_users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            assigned_to INTEGER NOT NULL,
            created_by INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Not Started',
            priority TEXT NOT NULL DEFAULT 'Medium',
            progress INTEGER NOT NULL DEFAULT 0,
            due_date DATE,
            staff_note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY(project_id) REFERENCES projects(id),
            FOREIGN KEY(assigned_to) REFERENCES staff_users(id),
            FOREIGN KEY(created_by) REFERENCES staff_users(id)
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to
        ON tasks(assigned_to)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_project
        ON tasks(project_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_due_date
        ON tasks(due_date)
    """)

    connection.commit()
    connection.close()


def _safe_date(value):
    if not value:
        return None
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _notify(user_id, title, message, priority="normal", related_id=None):
    try:
        create_notification(
            user_id,
            title,
            message,
            "task",
            priority,
            related_id,
            "task",
        )
    except Exception:
        # Task creation/update must not fail because notifications are unavailable.
        pass


def get_task_counts(user_id=None):
    ensure_task_tables()
    connection = get_connection()

    if user_id:
        rows = connection.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'Not Started' THEN 1 ELSE 0 END) AS not_started,
                SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) AS in_progress,
                SUM(CASE WHEN status = 'Blocked' THEN 1 ELSE 0 END) AS blocked,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) AS completed
            FROM tasks
            WHERE assigned_to = ?
        """, (user_id,)).fetchone()
    else:
        rows = connection.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'Not Started' THEN 1 ELSE 0 END) AS not_started,
                SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) AS in_progress,
                SUM(CASE WHEN status = 'Blocked' THEN 1 ELSE 0 END) AS blocked,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) AS completed
            FROM tasks
        """).fetchone()

    project_total = connection.execute(
        "SELECT COUNT(*) FROM projects"
    ).fetchone()[0]

    connection.close()

    return {
        "total": rows["total"] or 0,
        "not_started": rows["not_started"] or 0,
        "in_progress": rows["in_progress"] or 0,
        "blocked": rows["blocked"] or 0,
        "completed": rows["completed"] or 0,
        "projects": project_total,
    }


def get_projects(include_archived=False):
    ensure_task_tables()
    connection = get_connection()

    if include_archived:
        rows = connection.execute("""
            SELECT
                p.*,
                s.full_name AS creator_name,
                COUNT(t.id) AS task_count,
                SUM(CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END) AS completed_tasks
            FROM projects p
            LEFT JOIN staff_users s ON p.created_by = s.id
            LEFT JOIN tasks t ON p.id = t.project_id
            GROUP BY p.id
            ORDER BY p.created_at DESC, p.id DESC
        """).fetchall()
    else:
        rows = connection.execute("""
            SELECT
                p.*,
                s.full_name AS creator_name,
                COUNT(t.id) AS task_count,
                SUM(CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END) AS completed_tasks
            FROM projects p
            LEFT JOIN staff_users s ON p.created_by = s.id
            LEFT JOIN tasks t ON p.id = t.project_id
            WHERE p.status != 'Archived'
            GROUP BY p.id
            ORDER BY p.created_at DESC, p.id DESC
        """).fetchall()

    connection.close()
    return rows


def get_tasks(assigned_to=None, project_id=None, status=None):
    ensure_task_tables()
    connection = get_connection()

    conditions = []
    params = []

    if assigned_to is not None:
        conditions.append("t.assigned_to = ?")
        params.append(assigned_to)

    if project_id is not None:
        conditions.append("t.project_id = ?")
        params.append(project_id)

    if status and status != "All":
        conditions.append("t.status = ?")
        params.append(status)

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    rows = connection.execute(
        f"""
        SELECT
            t.*,
            p.name AS project_name,
            assignee.full_name AS assignee_name,
            creator.full_name AS creator_name
        FROM tasks t
        LEFT JOIN projects p ON t.project_id = p.id
        JOIN staff_users assignee ON t.assigned_to = assignee.id
        JOIN staff_users creator ON t.created_by = creator.id
        {where_clause}
        ORDER BY
            CASE t.priority
                WHEN 'Urgent' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                ELSE 4
            END,
            CASE WHEN t.status = 'Completed' THEN 2 ELSE 1 END,
            t.due_date IS NULL,
            t.due_date ASC,
            t.id DESC
        """,
        tuple(params),
    ).fetchall()

    connection.close()
    return rows


def create_project(
    name,
    description,
    status,
    priority,
    start_date,
    due_date,
    created_by,
):
    ensure_task_tables()

    if not name.strip():
        raise ValueError("Project name is required.")

    if due_date and start_date and due_date < start_date:
        raise ValueError("Project due date cannot be before its start date.")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO projects
        (name, description, status, priority, start_date, due_date, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        name.strip(),
        description.strip(),
        status,
        priority,
        _safe_date(start_date),
        _safe_date(due_date),
        created_by,
    ))

    project_id = cursor.lastrowid
    connection.commit()
    connection.close()

    return project_id


def create_task(
    project_id,
    title,
    description,
    assigned_to,
    created_by,
    status,
    priority,
    progress,
    due_date,
):
    ensure_task_tables()

    if not title.strip():
        raise ValueError("Task title is required.")

    if not assigned_to:
        raise ValueError("Please select an employee.")

    if progress < 0 or progress > 100:
        raise ValueError("Progress must be between 0 and 100.")

    if status == "Completed":
        progress = 100

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO tasks
        (
            project_id,
            title,
            description,
            assigned_to,
            created_by,
            status,
            priority,
            progress,
            due_date,
            completed_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        project_id,
        title.strip(),
        description.strip(),
        assigned_to,
        created_by,
        status,
        priority,
        progress,
        _safe_date(due_date),
        datetime.now().isoformat(timespec="seconds")
        if status == "Completed"
        else None,
    ))

    task_id = cursor.lastrowid
    connection.commit()

    assignee = connection.execute(
        "SELECT full_name FROM staff_users WHERE id = ?",
        (assigned_to,),
    ).fetchone()

    connection.close()

    if assignee:
        priority_map = {
            "Low": "low",
            "Medium": "normal",
            "High": "high",
            "Urgent": "urgent",
        }
        _notify(
            assigned_to,
            "New Task Assigned",
            f"You have been assigned: {title.strip()}",
            priority_map.get(priority, "normal"),
            task_id,
        )

    return task_id


def update_task(
    task_id,
    status=None,
    progress=None,
    due_date=None,
    staff_note=None,
    updated_by=None,
):
    ensure_task_tables()
    connection = get_connection()

    current = connection.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,),
    ).fetchone()

    if not current:
        connection.close()
        raise ValueError("Task not found.")

    new_status = status if status else current["status"]
    new_progress = (
        int(progress) if progress is not None else current["progress"]
    )

    if new_status == "Completed":
        new_progress = 100

    if new_progress < 0 or new_progress > 100:
        connection.close()
        raise ValueError("Progress must be between 0 and 100.")

    completed_at = current["completed_at"]
    if new_status == "Completed" and not completed_at:
        completed_at = datetime.now().isoformat(timespec="seconds")
    elif new_status != "Completed":
        completed_at = None

    connection.execute("""
        UPDATE tasks
        SET
            status = ?,
            progress = ?,
            due_date = ?,
            staff_note = ?,
            updated_at = CURRENT_TIMESTAMP,
            completed_at = ?
        WHERE id = ?
    """, (
        new_status,
        new_progress,
        _safe_date(due_date) if due_date is not None else current["due_date"],
        staff_note if staff_note is not None else current["staff_note"],
        completed_at,
        task_id,
    ))

    connection.commit()

    creator_id = current["created_by"]
    assignee_id = current["assigned_to"]

    connection.close()

    if updated_by and updated_by != creator_id:
        _notify(
            creator_id,
            "Task Updated",
            f"Task '{current['title']}' was updated.",
            "normal",
            task_id,
        )

    return True


def update_project_status(project_id, status):
    ensure_task_tables()
    connection = get_connection()

    connection.execute("""
        UPDATE projects
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (status, project_id))

    connection.commit()
    connection.close()


def delete_task(task_id):
    ensure_task_tables()
    connection = get_connection()
    connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    connection.commit()
    connection.close()


def delete_project(project_id):
    ensure_task_tables()
    connection = get_connection()

    task_count = connection.execute(
        "SELECT COUNT(*) FROM tasks WHERE project_id = ?",
        (project_id,),
    ).fetchone()[0]

    if task_count:
        connection.close()
        raise ValueError(
            "This project still has tasks. Archive the project instead, "
            "or remove its tasks first."
        )

    connection.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    connection.commit()
    connection.close()


def _date_text(value):
    if not value:
        return "No deadline"
    return str(value)


def _priority_badge(priority):
    return {
        "Low": "🟢",
        "Medium": "🔵",
        "High": "🟠",
        "Urgent": "🔴",
    }.get(priority, "⚪")


def _status_badge(status):
    return {
        "Not Started": "⚪",
        "In Progress": "🔵",
        "Blocked": "🟠",
        "Completed": "🟢",
    }.get(status, "⚪")


def _is_overdue(task):
    if not task["due_date"] or task["status"] == "Completed":
        return False
    try:
        return date.fromisoformat(str(task["due_date"])) < date.today()
    except ValueError:
        return False


def show_admin_task_manager(admin_id):
    """Super Admin project and task control centre."""
    ensure_task_tables()

    st.title("📋 Task & Project Manager")
    st.caption(
        "Plan projects, assign work, monitor progress and manage deadlines "
        "from the Pan Ideate Africa Administration Centre."
    )

    counts = get_task_counts()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📁 Projects", counts["projects"])
    c2.metric("📋 Tasks", counts["total"])
    c3.metric("🔵 In Progress", counts["in_progress"])
    c4.metric("🟠 Blocked", counts["blocked"])
    c5.metric("🟢 Completed", counts["completed"])

    st.divider()

    project_tab, create_project_tab, create_task_tab, task_tab = st.tabs([
        "📁 Projects",
        "➕ New Project",
        "📝 New Task",
        "📋 All Tasks",
    ])

    with project_tab:
        projects = get_projects(include_archived=True)

        if not projects:
            st.info("No projects have been created yet.")
        else:
            for project in projects:
                completion = (
                    round(
                        (project["completed_tasks"] or 0)
                        / project["task_count"]
                        * 100
                    )
                    if project["task_count"]
                    else 0
                )

                with st.container(border=True):
                    left, right = st.columns([5, 2])

                    with left:
                        st.subheader(f"📁 {project['name']}")
                        if project["description"]:
                            st.write(project["description"])
                        st.caption(
                            f"Priority: {_priority_badge(project['priority'])} "
                            f"{project['priority']} • "
                            f"Created by: {project['creator_name'] or 'Unknown'}"
                        )
                        st.progress(completion / 100)
                        st.caption(
                            f"{project['completed_tasks'] or 0}/"
                            f"{project['task_count'] or 0} tasks completed "
                            f"({completion}%)"
                        )

                    with right:
                        new_status = st.selectbox(
                            "Project status",
                            PROJECT_STATUSES,
                            index=PROJECT_STATUSES.index(project["status"])
                            if project["status"] in PROJECT_STATUSES
                            else 0,
                            key=f"project_status_{project['id']}",
                        )

                        if st.button(
                            "💾 Update Status",
                            key=f"project_update_{project['id']}",
                            use_container_width=True,
                        ):
                            update_project_status(project["id"], new_status)
                            st.success("Project status updated.")
                            st.rerun()

                        st.caption(
                            f"Start: {_date_text(project['start_date'])}"
                        )
                        st.caption(
                            f"Due: {_date_text(project['due_date'])}"
                        )

    with create_project_tab:
        st.subheader("➕ Create a New Project")

        with st.form("task_manager_create_project", clear_on_submit=True):
            name = st.text_input(
                "Project Name",
                placeholder="e.g. Iron Oxide Pigments Production Project",
            )
            description = st.text_area(
                "Project Description",
                placeholder="Describe the project objectives and expected result.",
            )

            c1, c2 = st.columns(2)
            with c1:
                status = st.selectbox("Status", PROJECT_STATUSES)
                priority = st.selectbox("Priority", PRIORITIES)

            with c2:
                start_date = st.date_input(
                    "Start Date",
                    value=date.today(),
                )
                due_date = st.date_input(
                    "Due Date",
                    value=date.today(),
                )

            create = st.form_submit_button(
                "🚀 Create Project",
                use_container_width=True,
                type="primary",
            )

        if create:
            try:
                project_id = create_project(
                    name,
                    description,
                    status,
                    priority,
                    start_date,
                    due_date,
                    admin_id,
                )
                st.success(f"✅ Project created successfully. Project ID: {project_id}")
                st.rerun()
            except ValueError as error:
                st.error(str(error))

    with create_task_tab:
        st.subheader("📝 Assign a New Task")

        projects = get_projects()
        staff = [
            row for row in get_all_staff()
            if row["status"] == "Active"
        ]

        if not staff:
            st.warning("Create an active staff account before assigning tasks.")
        else:
            project_options = {"No project": None}
            project_options.update({
                f"#{p['id']} — {p['name']}": p["id"]
                for p in projects
            })

            staff_options = {
                f"{person['full_name']} (@{person['username']}) — {person['role']}":
                person["id"]
                for person in staff
            }

            with st.form("task_manager_create_task", clear_on_submit=True):
                project_label = st.selectbox(
                    "Project",
                    list(project_options.keys()),
                )
                title = st.text_input(
                    "Task Title",
                    placeholder="e.g. Prepare pigment sample batch",
                )
                description = st.text_area(
                    "Task Description",
                    placeholder="Give the employee clear instructions.",
                )
                assignee_label = st.selectbox(
                    "Assign To",
                    list(staff_options.keys()),
                )

                c1, c2, c3 = st.columns(3)
                with c1:
                    task_status = st.selectbox(
                        "Status",
                        TASK_STATUSES,
                        index=0,
                    )
                with c2:
                    task_priority = st.selectbox(
                        "Priority",
                        PRIORITIES,
                        index=1,
                    )
                with c3:
                    progress = st.slider(
                        "Initial Progress",
                        0,
                        100,
                        0,
                        5,
                    )

                due_date = st.date_input(
                    "Deadline",
                    value=date.today(),
                )

                create = st.form_submit_button(
                    "📨 Assign Task",
                    use_container_width=True,
                    type="primary",
                )

            if create:
                try:
                    task_id = create_task(
                        project_options[project_label],
                        title,
                        description,
                        staff_options[assignee_label],
                        admin_id,
                        task_status,
                        task_priority,
                        progress,
                        due_date,
                    )
                    st.success(
                        f"✅ Task assigned successfully. Task ID: {task_id}"
                    )
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))

    with task_tab:
        st.subheader("📋 Task Register")

        projects = get_projects(include_archived=True)
        project_filter_options = {"All Projects": None}
        project_filter_options.update({
            f"#{p['id']} — {p['name']}": p["id"]
            for p in projects
        })

        fc1, fc2 = st.columns(2)
        with fc1:
            selected_project = st.selectbox(
                "Project Filter",
                list(project_filter_options.keys()),
                key="admin_task_project_filter",
            )
        with fc2:
            selected_status = st.selectbox(
                "Status Filter",
                ["All"] + TASK_STATUSES,
                key="admin_task_status_filter",
            )

        tasks = get_tasks(
            project_id=project_filter_options[selected_project],
            status=selected_status,
        )

        if not tasks:
            st.info("No tasks match the selected filters.")
        else:
            for task in tasks:
                overdue = _is_overdue(task)
                label = (
                    f"{_status_badge(task['status'])} "
                    f"{task['title']} — {task['assignee_name']}"
                )

                with st.expander(label):
                    top1, top2, top3 = st.columns(3)
                    with top1:
                        st.write(f"**Project:** {task['project_name'] or 'No project'}")
                        st.write(f"**Priority:** {_priority_badge(task['priority'])} {task['priority']}")
                    with top2:
                        st.write(f"**Assigned To:** {task['assignee_name']}")
                        st.write(f"**Created By:** {task['creator_name']}")
                    with top3:
                        st.write(f"**Deadline:** {_date_text(task['due_date'])}")
                        if overdue:
                            st.error("⏰ OVERDUE")

                    if task["description"]:
                        st.write(task["description"])

                    st.progress(task["progress"] / 100)
                    st.caption(f"Progress: {task['progress']}% • Status: {task['status']}")

                    if task["staff_note"]:
                        st.info(f"Staff note: {task['staff_note']}")

                    st.divider()

                    edit1, edit2, edit3 = st.columns(3)
                    with edit1:
                        new_status = st.selectbox(
                            "Status",
                            TASK_STATUSES,
                            index=TASK_STATUSES.index(task["status"])
                            if task["status"] in TASK_STATUSES
                            else 0,
                            key=f"admin_task_status_{task['id']}",
                        )
                    with edit2:
                        new_progress = st.slider(
                            "Progress",
                            0,
                            100,
                            int(task["progress"]),
                            5,
                            key=f"admin_task_progress_{task['id']}",
                        )
                    with edit3:
                        new_due = st.date_input(
                            "Deadline",
                            value=(
                                date.fromisoformat(str(task["due_date"]))
                                if task["due_date"]
                                else date.today()
                            ),
                            key=f"admin_task_due_{task['id']}",
                        )

                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button(
                            "💾 Save Task Changes",
                            key=f"admin_save_task_{task['id']}",
                            use_container_width=True,
                        ):
                            update_task(
                                task["id"],
                                status=new_status,
                                progress=new_progress,
                                due_date=new_due,
                                updated_by=admin_id,
                            )
                            st.success("Task updated.")
                            st.rerun()

                    with b2:
                        confirm = st.checkbox(
                            "Confirm permanent deletion",
                            key=f"confirm_delete_task_{task['id']}",
                        )
                        if st.button(
                            "🗑️ Delete Task",
                            key=f"delete_task_{task['id']}",
                            disabled=not confirm,
                            use_container_width=True,
                        ):
                            delete_task(task["id"])
                            st.success("Task deleted.")
                            st.rerun()


def show_staff_task_manager(staff_id, role):
    """Employee-facing task list. Staff can update their own task progress."""
    ensure_task_tables()

    st.title("📋 My Tasks")
    st.caption(
        "View your assigned work, update progress and keep your manager "
        "informed about task status."
    )

    counts = get_task_counts(staff_id)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📋 My Tasks", counts["total"])
    c2.metric("🔵 In Progress", counts["in_progress"])
    c3.metric("🟠 Blocked", counts["blocked"])
    c4.metric("🟢 Completed", counts["completed"])

    st.divider()

    status_filter = st.selectbox(
        "Filter My Tasks",
        ["All"] + TASK_STATUSES,
        key="my_task_status_filter",
    )

    tasks = get_tasks(
        assigned_to=staff_id,
        status=status_filter,
    )

    if not tasks:
        st.success("🎉 You currently have no tasks matching this filter.")
        return

    for task in tasks:
        overdue = _is_overdue(task)

        with st.container(border=True):
            title_col, badge_col = st.columns([5, 2])

            with title_col:
                st.subheader(f"📋 {task['title']}")
                st.caption(
                    f"Project: {task['project_name'] or 'No project'}"
                )

            with badge_col:
                st.write(
                    f"{_priority_badge(task['priority'])} "
                    f"**{task['priority']} Priority**"
                )
                st.write(
                    f"{_status_badge(task['status'])} "
                    f"**{task['status']}**"
                )

            if overdue:
                st.error(
                    f"⏰ This task was due on {_date_text(task['due_date'])}."
                )
            else:
                st.caption(
                    f"Deadline: {_date_text(task['due_date'])}"
                )

            if task["description"]:
                st.write(task["description"])

            st.progress(task["progress"] / 100)
            st.caption(f"Current progress: {task['progress']}%")

            if task["staff_note"]:
                st.info(f"Your latest note: {task['staff_note']}")

            with st.expander("✏️ Update My Task"):
                with st.form(f"update_my_task_{task['id']}"):
                    new_status = st.selectbox(
                        "Status",
                        TASK_STATUSES,
                        index=TASK_STATUSES.index(task["status"])
                        if task["status"] in TASK_STATUSES
                        else 0,
                    )
                    new_progress = st.slider(
                        "Progress",
                        0,
                        100,
                        int(task["progress"]),
                        5,
                    )
                    new_note = st.text_area(
                        "Progress / Staff Note",
                        value=task["staff_note"] or "",
                        placeholder=(
                            "Explain what has been completed, what remains, "
                            "or any issue blocking the work."
                        ),
                        height=120,
                    )

                    save = st.form_submit_button(
                        "💾 Save Update",
                        use_container_width=True,
                        type="primary",
                    )

                if save:
                    try:
                        update_task(
                            task["id"],
                            status=new_status,
                            progress=new_progress,
                            staff_note=new_note.strip(),
                            updated_by=staff_id,
                        )
                        st.success("✅ Task update saved.")
                        st.rerun()
                    except ValueError as error:
                        st.error(str(error))
