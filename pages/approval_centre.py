import streamlit as st

from pages.admin_access_control import STAFF_MODULES, get_staff_tool_access, save_staff_tool_access

from utils.approval_engine import (
    AUTHORITY_LEVELS,
    REQUEST_LABELS,
    get_staff,
    get_active_staff,
    get_authority_profile,
    get_authority_profiles,
    has_approval_access,
    is_super_admin,
    save_authority_profile,
    visible_requests_for_user,
    decision_history,
    can_review_request,
)


def _review_functions():
    leave = None
    finance = None

    try:
        from pages.leave_attendance import review_leave, review_early_signout
        leave = (review_leave, review_early_signout)
    except Exception:
        pass

    try:
        from pages.expenses_procurement import (
            review_expense,
            review_purchase_request,
        )
        finance = (review_expense, review_purchase_request)
    except Exception:
        pass

    return leave, finance


def _staff_options():
    return {
        f"{p['full_name']} (@{p['username']}) — {p['role']}": p["id"]
        for p in get_active_staff()
    }


def _review_request(ctx, approver_id, decision, note):
    allowed, message = can_review_request(
        approver_id,
        ctx["source_type"],
        ctx["source_id"],
    )

    if not allowed:
        return False, message

    leave, finance = _review_functions()

    if ctx["source_type"] == "leave":
        if not leave:
            return False, "Leave approval functions could not be loaded."
        return leave[0](
            ctx["source_id"],
            approver_id,
            decision,
            note,
        )

    if ctx["source_type"] == "early_signout":
        if not leave:
            return False, "Early sign-out approval function could not be loaded."
        return leave[1](
            ctx["source_id"],
            approver_id,
            decision,
            note,
        )

    if ctx["source_type"] == "expense":
        if not finance:
            return False, "Expense approval function could not be loaded."
        return finance[0](
            ctx["source_id"],
            approver_id,
            decision,
            note,
        )

    if ctx["source_type"] == "procurement":
        if not finance:
            return False, "Procurement approval function could not be loaded."
        return finance[1](
            ctx["source_id"],
            approver_id,
            decision,
            note,
        )

    return False, "Unsupported approval type."


def _render_request(ctx, user_id):
    routing = ctx.get("routing", {})
    is_override = is_super_admin(user_id) and routing.get("level", 4) < 4

    with st.container(border=True):
        st.subheader(
            f"{REQUEST_LABELS[ctx['source_type']]} — "
            f"#{ctx['source_id']} — {ctx['title']}"
        )

        if is_override:
            st.warning(
                "🔓 Super Admin oversight: this request is currently "
                f"routed to {routing.get('label', 'a lower level')}, "
                "but you can see and act on it."
            )
        else:
            st.info(
                f"🔐 Current route: "
                f"**{routing.get('label', 'Approval Authority')}**"
            )

        st.write(f"**Requester:** {ctx['requester_name']}")
        st.write(
            f"**Department:** "
            f"{ctx['department'] or 'Not assigned'}"
        )

        if ctx["source_type"] == "leave":
            st.write(
                f"**Leave length:** {ctx['leave_days'] or '?'} day(s)"
            )

        if ctx["source_type"] in {"expense", "procurement"}:
            st.write(
                f"**Amount:** {ctx['amount']:,.2f} {ctx['currency']}"
            )

        st.write(f"**Details:** {ctx['details']}")

        with st.form(
            f"approval_{ctx['source_type']}_{ctx['source_id']}_{user_id}"
        ):
            note = st.text_area(
                "Approval / rejection note",
                key=f"note_{ctx['source_type']}_{ctx['source_id']}_{user_id}",
            )

            left, right = st.columns(2)

            approve = left.form_submit_button(
                "✅ Approve",
                use_container_width=True,
                type="primary",
            )

            reject = right.form_submit_button(
                "❌ Reject",
                use_container_width=True,
            )

            if approve or reject:
                decision = "Approved" if approve else "Rejected"

                ok, message = _review_request(
                    ctx,
                    user_id,
                    decision,
                    note,
                )

                (st.success if ok else st.error)(message)

                if ok:
                    st.rerun()


def _show_pending(requests, user_id, heading, source_type=None):
    st.subheader(heading)

    visible = [
        request for request in requests
        if source_type is None or request["source_type"] == source_type
    ]

    if not visible:
        st.success("✅ No approvals currently require your attention.")
        return

    for request in visible:
        _render_request(request, user_id)


def _show_history(user_id):
    rows = decision_history(
        user_id,
        all_history=is_super_admin(user_id),
    )

    if is_super_admin(user_id):
        st.subheader("📜 Organization-wide Approval History")
        st.info(
            "Super Admin view: this includes approvals and rejections "
            "given by other authorized staff."
        )
    else:
        st.subheader("📜 My Approval History")

    if not rows:
        st.success("No approval decisions recorded yet.")
        return

    for row in rows:
        icon = "✅" if row["decision"] == "Approved" else "❌"

        with st.container(border=True):
            st.write(
                f"{icon} **{REQUEST_LABELS.get(row['source_type'], row['source_type'])}** "
                f"#{row['source_id']}"
            )
            st.write(
                f"**Requester:** {row['requester_name'] or 'Unknown'}"
            )
            st.write(
                f"**Decision by:** {row['approver_name'] or 'Unknown'} "
                f"({row['approver_role'] or 'Unknown'})"
            )
            st.caption(
                f"Authority Level {row['authority_level']} • "
                f"{row['acted_at']}"
            )
            if row["department"]:
                st.write(
                    f"**Department:** {row['department']}"
                )
            if row["note"]:
                st.write(
                    f"**Note:** {row['note']}"
                )


def _show_authority_profiles(super_admin_id):
    if not is_super_admin(super_admin_id):
        st.error(
            "🔒 Only the Super Admin can manage Approval Authority Profiles."
        )
        return

    st.subheader("⚙️ Approval Authority Profiles")
    st.caption(
        "Use this screen to decide who can access the Approval Centre, "
        "which department they can approve for, and the thresholds "
        "they are authorized to handle."
    )

    options = _staff_options()

    if not options:
        st.info("No active staff members are available.")
        return

    selected_label = st.selectbox(
        "Staff Member",
        list(options.keys()),
        key="approval_authority_staff",
    )
    staff_id = options[selected_label]

    profile = get_authority_profile(staff_id)

    current_level = int(profile["authority_level"]) if profile else 1
    current_department = (
        (profile["department"] or "")
        if profile
        else ""
    )
    current_access = bool(profile["can_access"]) if profile else False
    current_all_departments = (
        bool(profile["all_departments"])
        if profile
        else False
    )
    current_leave = (
        int(profile["max_leave_days"])
        if profile
        else 0
    )
    current_early = (
        bool(profile["can_approve_early_exit"])
        if profile
        else False
    )
    current_expense = (
        float(profile["expense_limit"])
        if profile
        else 0
    )
    current_expense_currency = (
        profile["expense_currency"]
        if profile
        else "UGX"
    )
    current_procurement = (
        float(profile["procurement_limit"])
        if profile
        else 0
    )
    current_procurement_currency = (
        profile["procurement_currency"]
        if profile
        else "UGX"
    )

    st.info(
        "Recommended structure: Level 1 Supervisor, Level 2 Manager/"
        "Department Head, Level 3 Administrator, Level 4 Super Admin. "
        "A request automatically goes to the lowest-authority person "
        "who is eligible to approve it."
    )

    level_labels = {
        1: "Level 1 — Supervisor / Team Approver",
        2: "Level 2 — Manager / Department Head",
        3: "Level 3 — Administrator",
        4: "Level 4 — Super Admin",
    }

    currencies = ["UGX", "USD", "EUR", "GBP"]

    with st.form("approval_authority_profile"):
        level = st.selectbox(
            "Authority Level",
            [1, 2, 3, 4],
            index=[1, 2, 3, 4].index(current_level),
            format_func=lambda x: level_labels[x],
            key=f"approval_authority_level_{staff_id}",
        )

        access = st.checkbox(
            "✅ Allow access to Approval Centre",
            value=current_access or level == 4,
            key=f"approval_access_{staff_id}",
        )

        department = st.text_input(
            "Authorized Department",
            value=current_department,
            placeholder="e.g. Agriculture",
            key=f"approval_department_{staff_id}",
        )

        all_departments = st.checkbox(
            "🌍 Authority covers all departments",
            value=current_all_departments or level == 4,
            key=f"approval_all_departments_{staff_id}",
        )

        col1, col2 = st.columns(2)

        with col1:
            max_leave_days = st.number_input(
                "Maximum leave days (0 = none, -1 = unlimited)",
                min_value=-1,
                value=int(current_leave),
                step=1,
                key=f"approval_max_leave_days_{staff_id}",
            )

            can_approve_early = st.checkbox(
                "🚪 Can approve early sign-out",
                value=current_early,
                key=f"approval_early_exit_{staff_id}",
            )

            expense_currency = st.selectbox(
                "Expense currency",
                currencies,
                index=(
                    currencies.index(current_expense_currency)
                    if current_expense_currency in currencies
                    else 0
                ),
                key=f"approval_expense_currency_{staff_id}",
            )

            expense_limit = st.number_input(
                "Expense limit (0 = none, -1 = unlimited)",
                min_value=-1.0,
                value=float(current_expense),
                step=10000.0 if expense_currency == "UGX" else 100.0,
                key=f"approval_expense_limit_{staff_id}",
            )

        with col2:
            procurement_currency = st.selectbox(
                "Procurement currency",
                currencies,
                index=(
                    currencies.index(current_procurement_currency)
                    if current_procurement_currency in currencies
                    else 0
                ),
                key=f"approval_procurement_currency_{staff_id}",
            )

            procurement_limit = st.number_input(
                "Procurement limit (0 = none, -1 = unlimited)",
                min_value=-1.0,
                value=float(current_procurement),
                step=10000.0 if procurement_currency == "UGX" else 100.0,
                key=f"approval_procurement_limit_{staff_id}",
            )

        save = st.form_submit_button(
            "💾 Save Authority Profile",
            type="primary",
            use_container_width=True,
        )

        if save:
            ok, message = save_authority_profile(
                staff_id,
                level,
                department,
                access,
                all_departments,
                max_leave_days,
                can_approve_early,
                expense_limit,
                expense_currency,
                procurement_limit,
                procurement_currency,
                super_admin_id,
            )
            (st.success if ok else st.error)(message)

            if ok:
                st.rerun()

    st.divider()
    st.subheader("Current Approval Authority Profiles")

    profiles = get_authority_profiles()

    if not profiles:
        st.info("No approval authority profiles configured.")
        return

    for profile in profiles:
        status = (
            "✅ Access Enabled"
            if profile["can_access"]
            else "🚫 Access Disabled"
        )

        scope = (
            "All Departments"
            if profile["all_departments"]
            else (profile["department"] or "No Department")
        )

        if profile["expense_limit"] == -1:
            expense_text = "Unlimited"
        else:
            expense_text = (
                f"{profile['expense_limit']:,.2f} "
                f"{profile['expense_currency']}"
            )

        if profile["procurement_limit"] == -1:
            procurement_text = "Unlimited"
        else:
            procurement_text = (
                f"{profile['procurement_limit']:,.2f} "
                f"{profile['procurement_currency']}"
            )

        with st.container(border=True):
            st.write(
                f"**{profile['full_name']}** — "
                f"{level_labels.get(profile['authority_level'], 'Custom')} — "
                f"{status}"
            )
            st.caption(
                f"Department scope: {scope} • Role: {profile['role']}"
            )
            st.write(
                f"Leave: {profile['max_leave_days']} day(s) • "
                f"Early Exit: "
                f"{'Yes' if profile['can_approve_early_exit'] else 'No'}"
            )
            st.write(
                f"Expenses: {expense_text} • "
                f"Procurement: {procurement_text}"
            )



def _show_staff_toolbox_access(super_admin_id):
    if not is_super_admin(super_admin_id):
        st.error("🔒 Only the Super Admin can manage staff toolbox access.")
        return
    st.subheader("🧰 Staff Toolbox Access")
    st.caption("Staff can see the toolbox; this profile decides which tools they can actually open.")
    options = _staff_options()
    if not options:
        st.info("No active staff members are available.")
        return
    selected_label = st.selectbox("Staff Member", list(options.keys()), key="approval_toolbox_staff")
    staff_id = options[selected_label]
    person = get_staff(staff_id)
    if person and person["role"] == "Super Admin":
        st.success("👑 Super Admin: all staff tools are automatically available.")
        return
    current = get_staff_tool_access(staff_id)
    permissions = {}
    with st.form(f"approval_toolbox_access_{staff_id}"):
        cols = st.columns(2)
        for i, (key, label, description) in enumerate(STAFF_MODULES):
            with cols[i % 2]:
                locked = key == "staff_management" and person and person["role"] != "Super Admin"
                permissions[key] = st.checkbox(label, value=current.get(key, False), disabled=locked, key=f"approval_tool_{staff_id}_{key}", help=description)
        save = st.form_submit_button("💾 Save Toolbox Access", type="primary", use_container_width=True)
    if save:
        ok, message = save_staff_tool_access(staff_id, super_admin_id, permissions)
        (st.success if ok else st.error)(message)
        if ok:
            st.rerun()

def show_approval_centre(user_id):
    if not has_approval_access(user_id):
        st.error(
            "🔒 You are not authorized to access the Approval Centre."
        )
        return

    person = get_staff(user_id)
    super_admin = is_super_admin(user_id)
    requests = visible_requests_for_user(user_id)

    leave_count = sum(
        1 for r in requests if r["source_type"] == "leave"
    )
    early_count = sum(
        1 for r in requests if r["source_type"] == "early_signout"
    )
    expense_count = sum(
        1 for r in requests if r["source_type"] == "expense"
    )
    procurement_count = sum(
        1 for r in requests if r["source_type"] == "procurement"
    )

    st.title("✅ Approval Centre")
    st.caption(
        "Pan Ideate Africa — Smart Delegated Approval & Authorization"
    )

    if super_admin:
        st.success(
            f"Signed in as: {person['full_name']} • Super Admin • "
            "Full approval visibility"
        )
    else:
        profile = get_authority_profile(user_id)
        st.success(
            f"Signed in as: {person['full_name']} • "
            f"{AUTHORITY_LEVELS.get(profile['authority_level'], 'Authorized Approver')}"
        )
        st.info(
            "Only requests within your department scope and approval "
            "threshold are shown here."
        )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📥 Pending", len(requests))
    c2.metric("🏖️ Leave", leave_count)
    c3.metric("🚪 Early Exit", early_count)
    c4.metric("💰 Expenses", expense_count)
    c5.metric("🛒 Procurement", procurement_count)

    labels = [
        "📥 All Pending",
        "🏖️ Leave",
        "🚪 Early Sign-Out",
        "💰 Expenses",
        "🛒 Procurement",
        "📜 History",
    ]

    if super_admin:
        labels.append("⚙️ Authority Profiles")

    tabs = st.tabs(labels)

    with tabs[0]:
        _show_pending(
            requests,
            user_id,
            "📥 Approvals Requiring Your Attention",
        )

    with tabs[1]:
        _show_pending(
            requests,
            user_id,
            "🏖️ Leave Requests",
            "leave",
        )

    with tabs[2]:
        _show_pending(
            requests,
            user_id,
            "🚪 Early Sign-Out Requests",
            "early_signout",
        )

    with tabs[3]:
        _show_pending(
            requests,
            user_id,
            "💰 Expense Claims",
            "expense",
        )

    with tabs[4]:
        _show_pending(
            requests,
            user_id,
            "🛒 Procurement Requests",
            "procurement",
        )

    with tabs[5]:
        _show_history(user_id)

    if super_admin:
        with tabs[6]:
            _show_authority_profiles(user_id)
            _show_staff_toolbox_access(user_id)


def show_staff_approval_centre(staff_id):
    show_approval_centre(staff_id)


def show_admin_approval_centre(admin_id):
    show_approval_centre(admin_id)


def show(admin_id):
    show_approval_centre(admin_id)


def show_admin(admin_id):
    show_approval_centre(admin_id)
