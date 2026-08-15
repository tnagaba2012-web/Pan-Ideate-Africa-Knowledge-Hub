import sqlite3
from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
DB_PATH = DATA_DIR / 'pan_ideate.db'

MODULES = [
    ('membership', '💳 Membership & Subscriptions', 'Manage memberships and subscription records.'),
    ('contact_messages', '📨 Contact Messages', 'Review public contact messages.'),
    ('partnerships', '🤝 Partnership Requests', 'Review partnership enquiries.'),
    ('donations', '❤️ Donation Requests', 'Review donation requests.'),
    ('staff_management', '👥 Staff Management', 'Create, edit and manage staff accounts.'),
    ('staff_directory', '👥 Staff Directory', 'Manage and view the staff directory.'),
    ('leave_attendance', '🕘 Leave & Attendance', 'Manage attendance and leave operations.'),
    ('expenses_procurement', '💰 Expenses & Procurement', 'Handle expenses, procurement and finance operations.'),
    ('tasks', '📋 Task & Project Manager', 'Manage tasks, assignments and projects.'),
    ('staff_communications', '💬 Staff Communications', 'Review organizational staff communications.'),
    ('staff_messages', '✉️ Staff Messages', 'Review authorized staff message operations.'),
    ('notifications', '🔔 Notification Centre', 'Manage staff notifications.'),
    ('ai_assistant', '🤖 AI Staff Assistant', 'Manage the authorized AI staff assistant.'),
    ('meetings', '📅 Meeting Centre', 'Manage meetings, agendas and follow-up actions.'),
    ('approvals', '✅ Approval Centre', 'Review and manage delegated approvals.'),
    ('audit_log', '🔐 Audit & Activity Log', 'Review organizational audit activity.'),
    ('documents', '📁 Document Centre', 'Manage organizational documents.'),
    ('innovation', '💡 Innovation Ideas', 'Manage innovation ideas.'),
    ('learning', '🎓 Learning Centre', 'Manage internal learning operations.'),
    ('knowledge_hub', '📚 Knowledge Hub', 'Manage Knowledge Hub administration.'),
]


def db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def init_access_control():
    con = db()
    con.execute('''
        CREATE TABLE IF NOT EXISTS staff_module_access (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER NOT NULL,
            module_key TEXT NOT NULL,
            can_access INTEGER NOT NULL DEFAULT 0,
            updated_by INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(staff_id, module_key)
        )
    ''')
    con.execute('CREATE INDEX IF NOT EXISTS idx_staff_module_access_staff ON staff_module_access(staff_id)')
    con.commit()
    con.close()


def is_super_admin(staff_id):
    con = db()
    row = con.execute("SELECT role, status FROM staff_users WHERE id = ? LIMIT 1", (staff_id,)).fetchone()
    con.close()
    return bool(row and row['status'] == 'Active' and row['role'] == 'Super Admin')


def has_module_access(staff_id, module_key):
    if not staff_id:
        return False
    if is_super_admin(staff_id):
        return True
    init_access_control()
    con = db()
    row = con.execute(
        'SELECT can_access FROM staff_module_access WHERE staff_id = ? AND module_key = ? LIMIT 1',
        (staff_id, module_key),
    ).fetchone()
    con.close()
    return bool(row and row['can_access'])


def get_staff_access(staff_id):
    init_access_control()
    con = db()
    rows = con.execute(
        'SELECT module_key, can_access FROM staff_module_access WHERE staff_id = ?',
        (staff_id,),
    ).fetchall()
    con.close()
    return {row['module_key']: bool(row['can_access']) for row in rows}


def save_staff_access(staff_id, updated_by, permissions):
    if not is_super_admin(updated_by):
        return False, 'Only the Super Admin can change module access.'
    init_access_control()
    con = db()
    for key, allowed in permissions.items():
        con.execute('''
            INSERT INTO staff_module_access (staff_id, module_key, can_access, updated_by, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(staff_id, module_key) DO UPDATE SET
                can_access = excluded.can_access,
                updated_by = excluded.updated_by,
                updated_at = CURRENT_TIMESTAMP
        ''', (staff_id, key, 1 if allowed else 0, updated_by))
    con.commit()
    con.close()
    return True, 'Module access permissions saved successfully.'


def show_access_control(super_admin_id):
    if not is_super_admin(super_admin_id):
        st.error('🔒 Only the Super Admin can manage staff module access.')
        return

    init_access_control()
    con = db()
    staff = con.execute("SELECT id, full_name, username, role, status FROM staff_users ORDER BY full_name").fetchall()
    con.close()

    st.title('🛡️ Staff Module Access Control')
    st.caption('Decide which staff members are authorized to handle each Administration Centre function. Permissions are enforced by the application.')

    if not staff:
        st.info('No staff accounts are available.')
        return

    options = {f"{p['full_name']} (@{p['username']}) — {p['role']}": p['id'] for p in staff}
    selected = st.selectbox('👤 Staff Member', list(options), key='module_access_staff')
    staff_id = options[selected]
    person = next(p for p in staff if p['id'] == staff_id)

    if person['role'] == 'Super Admin':
        st.success('👑 Super Admin: full module access is always granted.')
        return

    current = get_staff_access(staff_id)
    st.markdown('### 🔐 Authorized Administration Functions')
    st.info('Tick only the functions this staff member should handle. Approval amounts and departmental limits remain controlled by the Approval Authority system.')

    permissions = {}
    with st.form('module_access_form'):
        cols = st.columns(2)
        for index, (key, label, description) in enumerate(MODULES):
            with cols[index % 2]:
                permissions[key] = st.checkbox(
                    label,
                    value=current.get(key, False),
                    key=f'access_{staff_id}_{key}',
                    help=description,
                )
        st.divider()
        save = st.form_submit_button('💾 Save Staff Access Profile', type='primary', use_container_width=True)

    if save:
        ok, message = save_staff_access(staff_id, super_admin_id, permissions)
        (st.success if ok else st.error)(message)
        if ok:
            st.rerun()

    st.divider()
    st.subheader('📋 Current Access Summary')
    refreshed = get_staff_access(staff_id)
    enabled = [label for key, label, _ in MODULES if refreshed.get(key)]
    if enabled:
        for label in enabled:
            st.write(f'✅ {label}')
    else:
        st.warning('No Administration Centre functions have been assigned to this staff member.')
