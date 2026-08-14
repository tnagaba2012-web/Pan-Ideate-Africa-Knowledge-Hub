import sqlite3
from pathlib import Path
from datetime import date
import streamlit as st

# ============================================================
# PAN IDEATE AFRICA — APPROVAL CENTRE V1
# ============================================================
# Central approval inbox for existing operational modules.
#
# IMPORTANT DESIGN:
# This module does NOT replace Leave & Attendance or
# Expenses & Procurement. Those modules remain the owners of
# their records and business rules.
#
# Approval Centre provides one management screen over:
# - Leave requests
# - Early sign-out requests
# - Expense claims
# - Purchase / procurement requests
#
# Decisions are passed back to the original module functions,
# preserving their existing validation, audit trail and
# Notification Centre integration.
#
# Future:
# - Department-based approval routing
# - Multi-level approvals
# - Approval thresholds
# - Delegation
# - Approval history
# - SLA / overdue approval warnings
# - Document/signature requirements
# - Permission Centre integration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "pan_ideate.db"

APPROVER_ROLES = {
    "Super Admin",
    "Administrator",
    "Manager",
    "Finance",
}


def db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def get_staff(staff_id):
    con = db()
    try:
        row = con.execute("""
            SELECT id, full_name, username, role, status
            FROM staff_users
            WHERE id = ?
            LIMIT 1
        """, (staff_id,)).fetchone()
    except sqlite3.OperationalError:
        row = None
    con.close()
    return row


def is_approver(staff_id):
    person = get_staff(staff_id)
    return bool(
        person
        and person["status"] == "Active"
        and person["role"] in APPROVER_ROLES
    )


# ============================================================
# SAFE IMPORTS OF EXISTING MODULE OWNERS
# ============================================================

def leave_module():
    try:
        from pages.leave_attendance import (
            leave_requests,
            review_leave,
            review_early_signout,
        )
        return leave_requests, review_leave, review_early_signout
    except Exception:
        return None, None, None


def finance_module():
    try:
        from pages.expenses_procurement import (
            expense_claims,
            purchase_requests,
            review_expense,
            review_purchase_request,
        )
        return (
            expense_claims,
            purchase_requests,
            review_expense,
            review_purchase_request,
        )
    except Exception:
        return None, None, None, None


# ============================================================
# PENDING EARLY SIGN-OUTS
# ============================================================

def pending_early_signouts():
    con = db()

    try:
        rows = con.execute("""
            SELECT
                a.*,
                s.full_name,
                s.username,
                s.role
            FROM attendance_records a
            JOIN staff_users s
                ON s.id = a.staff_id
            WHERE a.early_signout_requested = 1
              AND a.early_signout_approved = 0
              AND a.sign_out_at IS NULL
            ORDER BY
                a.early_signout_requested_at ASC,
                a.id ASC
        """).fetchall()
    except sqlite3.OperationalError:
        rows = []

    con.close()
    return rows


# ============================================================
# CENTRAL METRICS
# ============================================================

def approval_metrics():
    metrics = {
        "leave": 0,
        "early": 0,
        "expenses": 0,
        "procurement": 0,
        "total": 0,
    }

    leave_requests, _, _ = leave_module()
    expense_claims, purchase_requests, _, _ = finance_module()

    if leave_requests:
        try:
            metrics["leave"] = len(leave_requests(status="Pending"))
        except Exception:
            pass

    metrics["early"] = len(pending_early_signouts())

    if expense_claims:
        try:
            metrics["expenses"] = len(
                expense_claims(status="Pending")
            )
        except Exception:
            pass

    if purchase_requests:
        try:
            metrics["procurement"] = len(
                purchase_requests(status="Pending")
            )
        except Exception:
            pass

    metrics["total"] = (
        metrics["leave"]
        + metrics["early"]
        + metrics["expenses"]
        + metrics["procurement"]
    )

    return metrics


# ============================================================
# APPROVAL CENTRE
# ============================================================

def show_approval_centre(admin_id):
    if not is_approver(admin_id):
        st.error(
            "🔒 You are not authorized to access the Approval Centre."
        )
        return

    person = get_staff(admin_id)
    metrics = approval_metrics()

    st.title("✅ Approval Centre")
    st.caption(
        "Pan Ideate Africa — Central Request Review & Authorization"
    )

    st.success(
        f"Signed in as: {person['full_name']} • {person['role']}"
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("📥 Total Pending", metrics["total"])
    c2.metric("🏖️ Leave", metrics["leave"])
    c3.metric("🚪 Early Exit", metrics["early"])
    c4.metric("💰 Expenses", metrics["expenses"])
    c5.metric("🛒 Procurement", metrics["procurement"])

    if metrics["total"] == 0:
        st.success(
            "✅ There are currently no pending approval requests."
        )

    tabs = st.tabs([
        "📥 All Pending",
        "🏖️ Leave",
        "🚪 Early Sign-Out",
        "💰 Expenses",
        "🛒 Procurement",
    ])

    # --------------------------------------------------------
    # ALL PENDING
    # --------------------------------------------------------
    with tabs[0]:
        st.subheader("📥 Central Approval Inbox")

        if metrics["total"] == 0:
            st.info("The approval inbox is clear.")
        else:
            st.info(
                "Use the category tabs to review and decide each request. "
                "The original module remains responsible for final validation."
            )

            if metrics["leave"]:
                st.write(
                    f"🏖️ **{metrics['leave']}** leave request(s) awaiting review."
                )

            if metrics["early"]:
                st.write(
                    f"🚪 **{metrics['early']}** early sign-out request(s) awaiting review."
                )

            if metrics["expenses"]:
                st.write(
                    f"💰 **{metrics['expenses']}** expense claim(s) awaiting review."
                )

            if metrics["procurement"]:
                st.write(
                    f"🛒 **{metrics['procurement']}** purchase request(s) awaiting review."
                )

    # --------------------------------------------------------
    # LEAVE
    # --------------------------------------------------------
    with tabs[1]:
        st.subheader("🏖️ Leave Requests")

        leave_requests, review_leave, _ = leave_module()

        if not leave_requests or not review_leave:
            st.warning(
                "Leave & Attendance could not be loaded. "
                "The existing module remains unchanged."
            )
        else:
            rows = leave_requests(status="Pending")

            if not rows:
                st.success("No pending leave requests.")
            else:
                for row in rows:
                    with st.container(border=True):
                        st.markdown(
                            f"### 🏖️ #{row['id']} — {row['full_name']}"
                        )

                        st.write(
                            f"**Leave:** {row['leave_type']} • "
                            f"{row['start_date']} → {row['end_date']}"
                        )

                        st.write(
                            f"**Reason:** {row['reason']}"
                        )

                        with st.form(
                            f"approval_leave_{row['id']}"
                        ):
                            note = st.text_area(
                                "Review Note",
                                key=f"approval_leave_note_{row['id']}",
                            )

                            a, b = st.columns(2)

                            approve = a.form_submit_button(
                                "✅ Approve Leave",
                                use_container_width=True,
                            )

                            reject = b.form_submit_button(
                                "❌ Reject Leave",
                                use_container_width=True,
                            )

                            if approve or reject:
                                decision = (
                                    "Approved"
                                    if approve
                                    else "Rejected"
                                )

                                ok, msg = review_leave(
                                    row["id"],
                                    admin_id,
                                    decision,
                                    note,
                                )

                                (st.success if ok else st.error)(msg)

                                if ok:
                                    st.rerun()

    # --------------------------------------------------------
    # EARLY SIGN-OUT
    # --------------------------------------------------------
    with tabs[2]:
        st.subheader("🚪 Early Sign-Out Requests")

        rows = pending_early_signouts()

        if not rows:
            st.success(
                "No pending early sign-out requests."
            )
        else:
            _, _, review_early_signout = leave_module()

            if not review_early_signout:
                st.warning(
                    "The Leave & Attendance approval function "
                    "could not be loaded."
                )
            else:
                for row in rows:
                    with st.container(border=True):
                        st.markdown(
                            f"### 🚪 #{row['id']} — "
                            f"{row['full_name']}"
                        )

                        st.write(
                            f"**Date:** {row['work_date']}"
                        )

                        st.write(
                            f"**Reason:** "
                            f"{row['early_signout_reason'] or 'Not provided'}"
                        )

                        st.caption(
                            f"Requested: "
                            f"{row['early_signout_requested_at'] or 'Unknown'}"
                        )

                        with st.form(
                            f"approval_early_{row['id']}"
                        ):
                            note = st.text_area(
                                "Authorization Note",
                                key=f"approval_early_note_{row['id']}",
                            )

                            a, b = st.columns(2)

                            approve = a.form_submit_button(
                                "✅ Approve",
                                use_container_width=True,
                            )

                            reject = b.form_submit_button(
                                "❌ Reject",
                                use_container_width=True,
                            )

                            if approve or reject:
                                decision = (
                                    "Approved"
                                    if approve
                                    else "Rejected"
                                )

                                ok, msg = review_early_signout(
                                    row["id"],
                                    admin_id,
                                    decision,
                                    note,
                                )

                                (st.success if ok else st.error)(msg)

                                if ok:
                                    st.rerun()

    # --------------------------------------------------------
    # EXPENSES
    # --------------------------------------------------------
    with tabs[3]:
        st.subheader("💰 Expense Claims")

        expense_claims, _, review_expense, _ = finance_module()

        if not expense_claims or not review_expense:
            st.warning(
                "Expenses & Procurement could not be loaded."
            )
        else:
            rows = expense_claims(status="Pending")

            if not rows:
                st.success("No pending expense claims.")
            else:
                for row in rows:
                    with st.container(border=True):
                        st.markdown(
                            f"### 💰 #{row['id']} — "
                            f"{row['full_name']}"
                        )

                        st.write(
                            f"**Category:** {row['category']}"
                        )

                        st.write(
                            f"**Amount:** "
                            f"{row['amount']:,.2f} "
                            f"{row['currency']}"
                        )

                        st.write(
                            f"**Date:** {row['expense_date']}"
                        )

                        st.write(
                            f"**Description:** {row['description']}"
                        )

                        if row["receipt_reference"]:
                            st.caption(
                                f"Receipt/reference: "
                                f"{row['receipt_reference']}"
                            )

                        with st.form(
                            f"approval_expense_{row['id']}"
                        ):
                            note = st.text_area(
                                "Review Note",
                                key=f"approval_expense_note_{row['id']}",
                            )

                            a, b = st.columns(2)

                            approve = a.form_submit_button(
                                "✅ Approve Expense",
                                use_container_width=True,
                            )

                            reject = b.form_submit_button(
                                "❌ Reject Expense",
                                use_container_width=True,
                            )

                            if approve or reject:
                                decision = (
                                    "Approved"
                                    if approve
                                    else "Rejected"
                                )

                                ok, msg = review_expense(
                                    row["id"],
                                    admin_id,
                                    decision,
                                    note,
                                )

                                (st.success if ok else st.error)(msg)

                                if ok:
                                    st.rerun()

    # --------------------------------------------------------
    # PROCUREMENT
    # --------------------------------------------------------
    with tabs[4]:
        st.subheader("🛒 Purchase Requests")

        _, purchase_requests, _, review_purchase_request = (
            finance_module()
        )

        if not purchase_requests or not review_purchase_request:
            st.warning(
                "Expenses & Procurement could not be loaded."
            )
        else:
            rows = purchase_requests(status="Pending")

            if not rows:
                st.success(
                    "No pending purchase requests."
                )
            else:
                for row in rows:
                    total = (
                        row["quantity"]
                        * row["estimated_unit_cost"]
                    )

                    with st.container(border=True):
                        st.markdown(
                            f"### 🛒 #{row['id']} — "
                            f"{row['full_name']}"
                        )

                        st.write(
                            f"**Item:** {row['item_name']}"
                        )

                        st.write(
                            f"**Quantity:** {row['quantity']:g} "
                            f"{row['unit']}"
                        )

                        st.write(
                            f"**Estimated Total:** "
                            f"**{total:,.2f} "
                            f"{row['currency']}**"
                        )

                        st.write(
                            f"**Category:** {row['category']}"
                        )

                        st.write(
                            f"**Justification:** "
                            f"{row['justification']}"
                        )

                        if row["supplier"]:
                            st.caption(
                                f"Preferred supplier: {row['supplier']}"
                            )

                        if row["required_by"]:
                            st.caption(
                                f"Required by: {row['required_by']}"
                            )

                        with st.form(
                            f"approval_purchase_{row['id']}"
                        ):
                            note = st.text_area(
                                "Review Note",
                                key=f"approval_purchase_note_{row['id']}",
                            )

                            a, b = st.columns(2)

                            approve = a.form_submit_button(
                                "✅ Approve Purchase",
                                use_container_width=True,
                            )

                            reject = b.form_submit_button(
                                "❌ Reject Purchase",
                                use_container_width=True,
                            )

                            if approve or reject:
                                decision = (
                                    "Approved"
                                    if approve
                                    else "Rejected"
                                )

                                ok, msg = review_purchase_request(
                                    row["id"],
                                    admin_id,
                                    decision,
                                    note,
                                )

                                (st.success if ok else st.error)(msg)

                                if ok:
                                    st.rerun()


# Generic aliases for future connection
def show(admin_id):
    show_approval_centre(admin_id)


def show_admin(admin_id):
    show_approval_centre(admin_id)
