"""
PAN-ID8 INNOVATION ENGINE
=========================
From Problems -> Opportunities -> Projects -> Products -> Impact

Designed for the existing Pan Ideate Africa Streamlit application.
- Uses the existing utils.database.get_connection() when available.
- Creates only its own tables.
- Works with the existing staff_users table.
- Connects to the existing Audit & Activity Log when available.
- Does not modify Staff Voice, Finance, Procurement or Approval tables.

Public entry point:
    show_page(staff=None)

Admin entry point:
    show_admin(staff)
"""

from datetime import datetime
import sqlite3
import streamlit as st

try:
    from utils.database import get_connection
except Exception:
    get_connection = None

try:
    from pages.audit_log import log_audit_event
except Exception:
    log_audit_event = None

try:
    from utils.approval_engine import get_active_staff, is_super_admin
except Exception:
    get_active_staff = None
    is_super_admin = None


PIPELINE = [
    "Submitted",
    "Screening",
    "Research",
    "Project Approved",
    "Experiment",
    "Prototype",
    "Field Test",
    "Business Assessment",
    "Product",
    "Commercialization",
    "Impact",
    "On Hold",
    "Rejected",
]

CATEGORIES = [
    "Agriculture",
    "Minerals & Chemistry",
    "Business Development",
    "Artificial Intelligence",
    "Learning & Education",
    "Environment",
    "Engineering & Manufacturing",
    "Community / Social Impact",
    "Digital Technology",
    "Other",
]

PRIORITIES = ["Low", "Normal", "High", "Critical"]

CRITERIA = [
    ("social_impact", "Social Impact", 15),
    ("local_resources", "Local-Resource Availability", 10),
    ("technical_feasibility", "Technical Feasibility", 15),
    ("cost_feasibility", "Cost Feasibility", 10),
    ("market_potential", "Market Potential", 15),
    ("youth_employment", "Youth Employment Potential", 10),
    ("environmental_benefit", "Environmental Benefit", 10),
    ("innovation_potential", "Innovation Potential", 15),
]


def _db():
    if get_connection:
        return get_connection()
    con = sqlite3.connect("data/pan_ideate.db", check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def _audit(action, summary, actor_id=None, target_id=None, details=None, severity="INFO"):
    if not log_audit_event:
        return
    try:
        log_audit_event(
            "Innovation Engine",
            action,
            summary,
            actor_id=actor_id,
            actor_name="Innovation Engine User",
            actor_role="Staff",
            target_type="innovation_opportunity" if target_id else None,
            target_id=str(target_id) if target_id else None,
            details=details,
            severity=severity,
        )
    except Exception:
        # Innovation Engine must not become unusable because optional audit wiring is absent.
        pass


def init_innovation_engine():
    con = _db()
    con.execute("""
        CREATE TABLE IF NOT EXISTS innovation_opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opportunity_number TEXT UNIQUE NOT NULL,
            submitted_by INTEGER,
            source_type TEXT DEFAULT 'Direct Submission',
            source_id TEXT,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            problem_statement TEXT NOT NULL,
            affected_people TEXT,
            proposed_solution TEXT,
            local_materials TEXT,
            expected_outcome TEXT,
            priority TEXT NOT NULL DEFAULT 'Normal',
            status TEXT NOT NULL DEFAULT 'Submitted',
            assigned_to INTEGER,
            score INTEGER NOT NULL DEFAULT 0,
            social_impact REAL NOT NULL DEFAULT 0,
            local_resources REAL NOT NULL DEFAULT 0,
            technical_feasibility REAL NOT NULL DEFAULT 0,
            cost_feasibility REAL NOT NULL DEFAULT 0,
            market_potential REAL NOT NULL DEFAULT 0,
            youth_employment REAL NOT NULL DEFAULT 0,
            environmental_benefit REAL NOT NULL DEFAULT 0,
            innovation_potential REAL NOT NULL DEFAULT 0,
            admin_notes TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS innovation_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opportunity_id INTEGER NOT NULL,
            actor_id INTEGER,
            action TEXT NOT NULL,
            note TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.execute("CREATE INDEX IF NOT EXISTS idx_innovation_status ON innovation_opportunities(status)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_innovation_category ON innovation_opportunities(category)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_innovation_score ON innovation_opportunities(score DESC)")
    con.commit()
    con.close()


def _next_number(con):
    year = datetime.now().year
    row = con.execute(
        "SELECT COUNT(*) FROM innovation_opportunities WHERE opportunity_number LIKE ?",
        (f"PIA-IDEA-{year}-%",),
    ).fetchone()
    return f"PIA-IDEA-{year}-{int(row[0] or 0) + 1:04d}"


def calculate_score(values):
    total = 0.0
    for key, _label, weight in CRITERIA:
        value = max(0.0, min(10.0, float(values.get(key, 0))))
        total += (value / 10.0) * weight
    return int(round(total))


def _staff_id(staff):
    if staff is None:
        return st.session_state.get("staff_id")
    try:
        return staff["id"]
    except Exception:
        return getattr(staff, "id", None)


def _staff_name(staff):
    if staff is None:
        return st.session_state.get("staff_name", "Staff Member")
    try:
        return staff["full_name"]
    except Exception:
        return getattr(staff, "full_name", "Staff Member")


def _is_admin(staff):
    try:
        role = staff["role"] if staff is not None else st.session_state.get("staff_role")
    except Exception:
        role = getattr(staff, "role", None) if staff is not None else st.session_state.get("staff_role")
    return role in {"Super Admin", "Administrator", "Manager"}


def submit_opportunity(staff_id, data):
    init_innovation_engine()
    con = _db()
    number = _next_number(con)
    score = calculate_score(data)
    cur = con.cursor()
    cur.execute("""
        INSERT INTO innovation_opportunities
        (opportunity_number, submitted_by, source_type, source_id, category,
         title, problem_statement, affected_people, proposed_solution,
         local_materials, expected_outcome, priority, status, score,
         social_impact, local_resources, technical_feasibility, cost_feasibility,
         market_potential, youth_employment, environmental_benefit, innovation_potential)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Submitted', ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        number, staff_id, data.get("source_type", "Direct Submission"), data.get("source_id"),
        data["category"], data["title"].strip(), data["problem_statement"].strip(),
        data.get("affected_people", "").strip(), data.get("proposed_solution", "").strip(),
        data.get("local_materials", "").strip(), data.get("expected_outcome", "").strip(),
        data["priority"], score,
        data.get("social_impact", 0), data.get("local_resources", 0),
        data.get("technical_feasibility", 0), data.get("cost_feasibility", 0),
        data.get("market_potential", 0), data.get("youth_employment", 0),
        data.get("environmental_benefit", 0), data.get("innovation_potential", 0),
    ))
    opportunity_id = cur.lastrowid
    con.execute(
        "INSERT INTO innovation_activity (opportunity_id, actor_id, action, note) VALUES (?, ?, ?, ?)",
        (opportunity_id, staff_id, "SUBMITTED", "Innovation opportunity submitted."),
    )
    con.commit()
    con.close()
    _audit(
        "SUBMIT_OPPORTUNITY",
        f"Innovation opportunity {number} submitted.",
        actor_id=staff_id,
        target_id=opportunity_id,
        details={"opportunity_number": number, "category": data["category"], "score": score},
    )
    return opportunity_id, number, score


def _update_opportunity(opportunity_id, actor_id, status, assigned_to, note, score_values=None):
    con = _db()
    row = con.execute("SELECT * FROM innovation_opportunities WHERE id = ?", (opportunity_id,)).fetchone()
    if not row:
        con.close()
        return False, "Opportunity not found."

    score = row["score"]
    score_sql = ""
    values = [status, assigned_to, note.strip(), opportunity_id]
    if score_values is not None:
        score = calculate_score(score_values)
        score_sql = ", social_impact=?, local_resources=?, technical_feasibility=?, cost_feasibility=?, market_potential=?, youth_employment=?, environmental_benefit=?, innovation_potential=?, score=?"
        values = [
            status, assigned_to, note.strip(),
            score_values["social_impact"], score_values["local_resources"], score_values["technical_feasibility"],
            score_values["cost_feasibility"], score_values["market_potential"], score_values["youth_employment"],
            score_values["environmental_benefit"], score_values["innovation_potential"], score, opportunity_id,
        ]

    if score_values is None:
        con.execute(
            "UPDATE innovation_opportunities SET status=?, assigned_to=?, admin_notes=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            values,
        )
    else:
        con.execute(
            "UPDATE innovation_opportunities SET status=?, assigned_to=?, admin_notes=?, updated_at=CURRENT_TIMESTAMP" + score_sql + " WHERE id=?",
            values,
        )

    con.execute(
        "INSERT INTO innovation_activity (opportunity_id, actor_id, action, note) VALUES (?, ?, ?, ?)",
        (opportunity_id, actor_id, f"STATUS: {status}", note.strip()),
    )
    con.commit()
    con.close()
    _audit(
        "UPDATE_OPPORTUNITY",
        f"Innovation opportunity #{opportunity_id} moved to {status}.",
        actor_id=actor_id,
        target_id=opportunity_id,
        details={"status": status, "assigned_to": assigned_to, "score": score},
    )
    return True, "Innovation opportunity updated successfully."


def _render_header():
    st.markdown("""
    <style>
    .pia-hero {padding: 1.2rem 1.4rem; border-radius: 18px; background: linear-gradient(135deg,#0B6E4F,#145DA0); color:white; margin-bottom:1rem;}
    .pia-card {padding: 1rem; border-radius: 14px; background:#ffffff; border:1px solid #e8edf2; box-shadow:0 4px 16px rgba(0,0,0,.05);}
    .pia-score {font-size:2.2rem; font-weight:800;}
    </style>
    <div class="pia-hero">
      <h1>🌍 PAN-ID8 Innovation Engine</h1>
      <p style="font-size:1.05rem;margin:0">From Problems → Opportunities → Projects → Products → Impact</p>
    </div>
    """, unsafe_allow_html=True)


def show_page(staff=None):
    init_innovation_engine()
    _render_header()
    sid = _staff_id(staff)
    name = _staff_name(staff)
    st.caption(f"Welcome, {name}. Turn a real problem into a structured innovation opportunity.")

    tab1, tab2, tab3, tab4 = st.tabs(["💡 Submit Problem", "📊 Opportunity Pipeline", "🏆 Top Opportunities", "ℹ️ How It Works"])

    with tab1:
        st.subheader("💡 Submit a Problem or Opportunity")
        st.write("A good innovation can begin with a very ordinary problem. Describe it clearly; the system turns it into a trackable opportunity.")
        with st.form("pia_innovation_submit_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                category = st.selectbox("Category", CATEGORIES)
                title = st.text_input("Short title", placeholder="e.g. Affordable soil water-retention solution")
                priority = st.selectbox("Priority", PRIORITIES, index=1)
            with c2:
                affected = st.text_input("Who is affected?", placeholder="Farmers, students, staff, communities...")
                materials = st.text_input("Local materials / resources available", placeholder="Biochar, clay, sand, waste materials...")
                source = st.selectbox("Source", ["Direct Submission", "Staff Voice", "Field Observation", "Research", "Customer / Community Feedback"])
            problem = st.text_area("Problem statement", height=150, placeholder="What problem exists? What is happening now, and why does it matter?")
            solution = st.text_area("Possible solution (optional)", height=110, placeholder="What might solve it? It is okay if you are not sure yet.")
            outcome = st.text_area("Expected outcome", height=90, placeholder="What would success look like?")

            st.markdown("### 🎯 Initial Opportunity Assessment")
            st.caption("Score each item from 0–10. The weighted result becomes the Opportunity Score out of 100. You can revise it during screening.")
            cols = st.columns(4)
            scores = {}
            for i, (key, label, _weight) in enumerate(CRITERIA):
                with cols[i % 4]:
                    scores[key] = st.slider(label, 0, 10, 5, key=f"new_{key}")
            live_score = calculate_score(scores)
            st.metric("Initial Opportunity Score", f"{live_score}/100")
            submitted = st.form_submit_button("🚀 Submit to Innovation Engine", type="primary", use_container_width=True)

        if submitted:
            if not title.strip() or not problem.strip():
                st.error("Please provide both a short title and a problem statement.")
            else:
                data = {
                    "category": category, "title": title, "priority": priority,
                    "affected_people": affected, "local_materials": materials,
                    "problem_statement": problem, "proposed_solution": solution,
                    "expected_outcome": outcome, "source_type": source,
                    **scores,
                }
                oid, number, score = submit_opportunity(sid, data)
                st.success(f"Submitted successfully: **{number}**")
                st.info(f"Initial Opportunity Score: **{score}/100**. Keep the number for reference.")

    with tab2:
        st.subheader("📊 Opportunity Pipeline")
        con = _db()
        rows = con.execute("SELECT * FROM innovation_opportunities ORDER BY updated_at DESC, id DESC LIMIT 200").fetchall()
        con.close()
        if not rows:
            st.info("No innovation opportunities have been submitted yet.")
        else:
            for row in rows:
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([4, 2, 1, 1])
                    c1.markdown(f"**{row['opportunity_number']} — {row['title']}**")
                    c1.caption(f"{row['category']} • {row['priority']} • {row['status']}")
                    c2.write(f"**Stage:** {row['status']}")
                    c3.metric("Score", f"{row['score']}/100")
                    c4.write("🟢 Active" if row['status'] not in {"Rejected", "On Hold", "Impact"} else "⚪ Closed/Paused")

    with tab3:
        st.subheader("🏆 Highest-Potential Opportunities")
        con = _db()
        rows = con.execute("SELECT * FROM innovation_opportunities ORDER BY score DESC, updated_at DESC LIMIT 10").fetchall()
        con.close()
        if not rows:
            st.info("Top opportunities will appear here after submissions.")
        else:
            for rank, row in enumerate(rows, 1):
                with st.container(border=True):
                    a, b = st.columns([5, 1])
                    a.markdown(f"### #{rank} • {row['title']}")
                    a.caption(f"{row['opportunity_number']} • {row['category']} • {row['status']}")
                    b.metric("Score", f"{row['score']}/100")
                    st.write(row['problem_statement'])

    with tab4:
        st.subheader("🔄 Innovation Journey")
        st.markdown("**Submitted → Screening → Research → Project Approved → Experiment → Prototype → Field Test → Business Assessment → Product → Commercialization → Impact**")
        st.markdown("""
        ### What makes this different?
        - Problems become structured organisational knowledge rather than disappearing in messages.
        - The system gives every opportunity a unique **PIA-IDEA** number.
        - Opportunity scoring helps management decide what deserves attention first.
        - The same record can travel from an idea into a real project and eventually a product or business.
        - Staff Voice can become a future source of innovation opportunities without exposing the reporter's identity to ordinary users.
        - Audit events can record important administrative changes.
        """)


def show_admin(staff):
    init_innovation_engine()
    if not _is_admin(staff):
        st.error("🔒 Innovation Engine management is restricted to authorized administrators.")
        return

    _render_header()
    st.subheader("🛡️ Innovation Management Centre")

    con = _db()
    total = con.execute("SELECT COUNT(*) FROM innovation_opportunities").fetchone()[0]
    active = con.execute("SELECT COUNT(*) FROM innovation_opportunities WHERE status NOT IN ('Impact','Rejected','On Hold')").fetchone()[0]
    high = con.execute("SELECT COUNT(*) FROM innovation_opportunities WHERE score >= 80").fetchone()[0]
    projects = con.execute("SELECT COUNT(*) FROM innovation_opportunities WHERE status IN ('Project Approved','Experiment','Prototype','Field Test','Business Assessment','Product','Commercialization','Impact')").fetchone()[0]
    con.close()

    a, b, c, d = st.columns(4)
    a.metric("💡 Total Opportunities", total)
    b.metric("🔄 Active Pipeline", active)
    c.metric("⭐ Score ≥ 80", high)
    d.metric("🛠️ Project/Business Stage", projects)

    st.divider()
    f1, f2, f3 = st.columns(3)
    with f1:
        status_filter = st.selectbox("Status", ["All"] + PIPELINE, key="ie_admin_status")
    with f2:
        category_filter = st.selectbox("Category", ["All"] + CATEGORIES, key="ie_admin_category")
    with f3:
        min_score = st.slider("Minimum Score", 0, 100, 0, key="ie_admin_score")

    con = _db()
    query = "SELECT * FROM innovation_opportunities WHERE score >= ?"
    params = [min_score]
    if status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)
    if category_filter != "All":
        query += " AND category = ?"
        params.append(category_filter)
    query += " ORDER BY score DESC, updated_at DESC"
    rows = con.execute(query, params).fetchall()
    con.close()

    if not rows:
        st.info("No opportunities match these filters.")
        return

    staff_options = {"Unassigned": None}
    if get_active_staff:
        try:
            for person in get_active_staff():
                staff_options[f"{person['full_name']} (@{person['username']})"] = person['id']
        except Exception:
            pass

    for row in rows:
        with st.expander(f"{row['opportunity_number']} • {row['title']} • ⭐ {row['score']}/100 • {row['status']}", expanded=False):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.write(f"**Category:** {row['category']}")
                st.write(f"**Problem:** {row['problem_statement']}")
                st.write(f"**Affected:** {row['affected_people'] or 'Not specified'}")
                st.write(f"**Possible solution:** {row['proposed_solution'] or 'Not specified'}")
                st.write(f"**Local resources:** {row['local_materials'] or 'Not specified'}")
                st.write(f"**Expected outcome:** {row['expected_outcome'] or 'Not specified'}")
            with c2:
                st.metric("Opportunity Score", f"{row['score']}/100")
                st.caption(f"Submitted: {str(row['created_at'])[:16]}")

            st.markdown("### 🧭 Management Decision")
            with st.form(f"ie_admin_form_{row['id']}"):
                x1, x2 = st.columns(2)
                with x1:
                    new_status = st.selectbox("Pipeline Stage", PIPELINE, index=PIPELINE.index(row['status']) if row['status'] in PIPELINE else 0, key=f"ie_status_{row['id']}")
                with x2:
                    labels = list(staff_options.keys())
                    current_assignee = "Unassigned"
                    for label, pid in staff_options.items():
                        if pid == row['assigned_to']:
                            current_assignee = label
                            break
                    assignee = st.selectbox("Assign To", labels, index=labels.index(current_assignee), key=f"ie_assign_{row['id']}")
                note = st.text_area("Management note", value=row['admin_notes'] or "", key=f"ie_note_{row['id']}")

                with st.expander("🎯 Reassess Opportunity Score"):
                    reassess = st.checkbox("Update the score", key=f"ie_reassess_{row['id']}")
                    score_values = {}
                    cols = st.columns(4)
                    for i, (key, label, _weight) in enumerate(CRITERIA):
                        with cols[i % 4]:
                            score_values[key] = st.slider(label, 0, 10, int(round(row[key] or 0)), key=f"ie_{key}_{row['id']}")

                save = st.form_submit_button("💾 Save Innovation Decision", type="primary", use_container_width=True)
                if save:
                    ok, msg = _update_opportunity(
                        row['id'], _staff_id(staff), new_status,
                        staff_options.get(assignee), note,
                        score_values if reassess else None,
                    )
                    (st.success if ok else st.error)(msg)
                    if ok:
                        st.rerun()


# Alias for projects that use a conventional page function.
def show():
    show_page()
