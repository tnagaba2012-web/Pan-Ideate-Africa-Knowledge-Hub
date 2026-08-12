import re
import streamlit as st

from utils.database import get_connection


# ============================================================
# PAN IDEATE AFRICA
# MEMBERSHIP & SUBSCRIPTION MODULE
# ============================================================


# ------------------------------------------------------------
# SUBSCRIPTION PLANS
# ------------------------------------------------------------

PLANS = {
    "FREE": {
        "icon": "🟢",
        "description": "A starting point for learners and community members.",
        "features": [
            "Basic Handbook",
            "Community Access",
            "Basic AI Assistant",
            "News Updates",
        ],
    },

    "STUDENT": {
        "icon": "🔵",
        "description": "Designed for students, learners and young innovators.",
        "features": [
            "Everything in FREE",
            "Full Courses",
            "Quizzes",
            "Certificates",
        ],
    },

    "PROFESSIONAL": {
        "icon": "🟠",
        "description": "For entrepreneurs, producers and professionals.",
        "features": [
            "Everything in STUDENT",
            "Business Suite",
            "Production Guides",
            "Premium Downloads",
        ],
    },

    "ENTERPRISE": {
        "icon": "👑",
        "description": "For organisations, teams, institutions and enterprises.",
        "features": [
            "Everything Included",
            "AI Business Tools",
            "Team Accounts",
            "Analytics",
            "Priority Support",
        ],
    },
}


# ------------------------------------------------------------
# DATABASE SETUP
# ------------------------------------------------------------

def ensure_subscription_table():
    """
    Create the subscriptions table if it does not already exist.

    If the table already exists, safely add any columns that are
    missing from the existing Pan Ideate Africa database.
    """

    connection = get_connection()
    cursor = connection.cursor()

    # --------------------------------------------------------
    # CREATE TABLE IF IT DOES NOT EXIST
    # --------------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            plan TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            payment_status TEXT DEFAULT 'Not Required',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # --------------------------------------------------------
    # CHECK EXISTING COLUMNS
    # --------------------------------------------------------

    cursor.execute("PRAGMA table_info(subscriptions)")

    existing_columns = {
        row["name"] for row in cursor.fetchall()
    }

    # --------------------------------------------------------
    # UPGRADE EXISTING DATABASE SAFELY
    # --------------------------------------------------------

    if "phone" not in existing_columns:
        cursor.execute(
            "ALTER TABLE subscriptions ADD COLUMN phone TEXT"
        )

    if "status" not in existing_columns:
        cursor.execute(
            """
            ALTER TABLE subscriptions
            ADD COLUMN status TEXT DEFAULT 'Pending'
            """
        )

    if "payment_status" not in existing_columns:
        cursor.execute(
            """
            ALTER TABLE subscriptions
            ADD COLUMN payment_status TEXT
            DEFAULT 'Not Required'
            """
        )

    if "created_at" not in existing_columns:
        cursor.execute(
            """
            ALTER TABLE subscriptions
            ADD COLUMN created_at TIMESTAMP
            """
        )

    # --------------------------------------------------------
    # SAVE DATABASE CHANGES
    # --------------------------------------------------------

    connection.commit()
    connection.close()


# ------------------------------------------------------------
# SAVE SUBSCRIPTION
# ------------------------------------------------------------

def save_subscription(full_name, email, phone, plan):
    """
    Save a subscription request into the Pan Ideate Africa
    SQLite database and return the generated subscription ID.
    """

    ensure_subscription_table()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO subscriptions
        (
            full_name,
            email,
            phone,
            plan,
            status,
            payment_status
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            full_name,
            email,
            phone,
            plan,
            "Pending",
            "Not Required",
        ),
    )

    subscription_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return subscription_id


# ------------------------------------------------------------
# EMAIL VALIDATION
# ------------------------------------------------------------

def valid_email(email):
    """
    Basic email validation.
    """

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return re.match(pattern, email) is not None


# ------------------------------------------------------------
# MAIN PAGE
# ------------------------------------------------------------

def show():

    # Make sure the database table exists.
    ensure_subscription_table()

    # ========================================================
    # PAGE HEADER
    # ========================================================

    st.header("💳 Membership & Subscription Plans")

    st.caption(
        "Choose the Pan Ideate Africa membership level that "
        "matches your learning, business or organisational needs."
    )

    st.info(
        "🧪 TEST MODE — Membership requests are currently being "
        "recorded for system testing. No real payment is processed."
    )

    # ========================================================
    # PLAN DISPLAY
    # ========================================================

    st.divider()

    st.subheader("🌍 Choose Your Membership")

    free, student, professional, enterprise = st.columns(4)

    # --------------------------------------------------------
    # FREE
    # --------------------------------------------------------

    with free:

        st.success("🟢 FREE")

        st.write(
            "**Perfect for exploring the Pan Ideate Africa "
            "Knowledge Hub.**"
        )

        for feature in PLANS["FREE"]["features"]:
            st.write(f"✓ {feature}")

        if st.button(
            "Choose FREE",
            key="subscribe_free",
            use_container_width=True,
        ):
            st.session_state["selected_plan"] = "FREE"
            st.rerun()

    # --------------------------------------------------------
    # STUDENT
    # --------------------------------------------------------

    with student:

        st.info("🔵 STUDENT")

        st.write(
            "**For students, learners and young innovators.**"
        )

        for feature in PLANS["STUDENT"]["features"]:
            st.write(f"✓ {feature}")

        if st.button(
            "Choose STUDENT",
            key="subscribe_student",
            use_container_width=True,
        ):
            st.session_state["selected_plan"] = "STUDENT"
            st.rerun()

    # --------------------------------------------------------
    # PROFESSIONAL
    # --------------------------------------------------------

    with professional:

        st.warning("🟠 PROFESSIONAL")

        st.write(
            "**For entrepreneurs, producers and professionals.**"
        )

        for feature in PLANS["PROFESSIONAL"]["features"]:
            st.write(f"✓ {feature}")

        if st.button(
            "Choose PROFESSIONAL",
            key="subscribe_professional",
            use_container_width=True,
        ):
            st.session_state["selected_plan"] = "PROFESSIONAL"
            st.rerun()

    # --------------------------------------------------------
    # ENTERPRISE
    # --------------------------------------------------------

    with enterprise:

        st.error("👑 ENTERPRISE")

        st.write(
            "**For organisations, institutions and business "
            "teams.**"
        )

        for feature in PLANS["ENTERPRISE"]["features"]:
            st.write(f"✓ {feature}")

        if st.button(
            "Choose ENTERPRISE",
            key="subscribe_enterprise",
            use_container_width=True,
        ):
            st.session_state["selected_plan"] = "ENTERPRISE"
            st.rerun()

    # ========================================================
    # SELECTED PLAN
    # ========================================================

    if "selected_plan" not in st.session_state:
        return

    selected_plan = st.session_state["selected_plan"]

    plan_info = PLANS[selected_plan]

    st.divider()

    st.header(
        f"{plan_info['icon']} Subscribe to the "
        f"{selected_plan} Plan"
    )

    st.write(
        f"You selected the **{selected_plan}** membership plan."
    )

    st.caption(plan_info["description"])

    # ========================================================
    # PLAN BENEFITS
    # ========================================================

    with st.expander(
        f"📋 View {selected_plan} Benefits",
        expanded=True,
    ):

        for feature in plan_info["features"]:
            st.write(f"⭐ {feature}")

    # ========================================================
    # SUBSCRIPTION FORM
    # ========================================================

    st.subheader("📝 Member Information")

    with st.form("subscription_form"):

        full_name = st.text_input(
            "Full Name *",
            placeholder="Enter your full name",
        )

        email = st.text_input(
            "Email Address *",
            placeholder="Enter your email address",
        )

        phone = st.text_input(
            "Phone Number",
            placeholder="e.g. 07XXXXXXXX",
            help=(
                "Optional for now. This will support future "
                "mobile-money payment integration."
            ),
        )

        confirm = st.checkbox(
            f"I confirm that I want to request the "
            f"{selected_plan} membership plan."
        )

        submitted = st.form_submit_button(
            "🚀 Submit Membership Request",
            use_container_width=True,
        )

        if submitted:

            # ------------------------------------------------
            # VALIDATION
            # ------------------------------------------------

            if not full_name.strip():

                st.error(
                    "❌ Please enter your full name."
                )

            elif not email.strip():

                st.error(
                    "❌ Please enter your email address."
                )

            elif not valid_email(email.strip()):

                st.error(
                    "❌ Please enter a valid email address."
                )

            elif not confirm:

                st.error(
                    "❌ Please confirm your membership request."
                )

            else:

                # --------------------------------------------
                # SAVE TO DATABASE
                # --------------------------------------------

                try:

                    subscription_id = save_subscription(
                        full_name=full_name.strip(),
                        email=email.strip().lower(),
                        phone=phone.strip(),
                        plan=selected_plan,
                    )

                    # Save result in session state.
                    st.session_state["subscription_success"] = True
                    st.session_state["subscription_id"] = (
                        subscription_id
                    )
                    st.session_state["member_name"] = (
                        full_name.strip()
                    )
                    st.session_state["member_email"] = (
                        email.strip().lower()
                    )
                    st.session_state["member_plan"] = (
                        selected_plan
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        "❌ We could not save your membership "
                        "request."
                    )

                    st.exception(error)

    # ========================================================
    # SUCCESS MESSAGE
    # ========================================================

    if st.session_state.get(
        "subscription_success",
        False,
    ):

        st.divider()

        st.success(
            "🎉 Membership request submitted successfully!"
        )

        subscription_id = st.session_state.get(
            "subscription_id"
        )

        member_name = st.session_state.get(
            "member_name"
        )

        member_email = st.session_state.get(
            "member_email"
        )

        member_plan = st.session_state.get(
            "member_plan"
        )

        st.info(
            f"""
### 📄 Membership Request

**Request ID:** #{subscription_id}

**Member:** {member_name}

**Email:** {member_email}

**Plan:** {member_plan}

**Status:** 🟡 Pending

**Payment:** Not Required — Test Mode
"""
        )

        st.warning(
            "🧪 TEST MODE: No payment has been taken. "
            "Real payment and automatic membership activation "
            "will be connected in a future version."
        )

        if st.button(
            "🔄 Start Another Membership Request",
            use_container_width=True,
        ):

            for key in [
                "subscription_success",
                "subscription_id",
                "member_name",
                "member_email",
                "member_plan",
                "selected_plan",
            ]:
                st.session_state.pop(key, None)

            st.rerun()

    # ========================================================
    # PREMIUM FEATURES
    # ========================================================

    st.divider()

    st.header("🔒 Premium Features")

    st.write(
        """
Premium members will progressively gain access to:

⭐ Advanced Production Manuals

⭐ Business Templates

⭐ Equipment Guides

⭐ Market Intelligence

⭐ AI Business Planning

⭐ Downloadable Professional PDFs

⭐ Premium Video Lessons

⭐ Investor Resources

⭐ Advanced Business Development Tools

⭐ Special Pan Ideate Africa learning resources
"""
    )

    # ========================================================
    # FUTURE DEVELOPMENT
    # ========================================================

    st.divider()

    st.subheader("🚀 Membership System Roadmap")

    st.info(
        """
The Pan Ideate Africa membership system is being developed
in stages.

### Current Stage
• Membership plans
• Subscription request form
• SQLite database storage
• Membership request ID
• Test-mode workflow

### Next Stages
• Secure user accounts
• Member login
• Real subscription management
• MTN Mobile Money integration
• Other payment methods
• Automatic payment verification
• Automatic membership activation
• Premium-content access control
• Member dashboards
• Subscription history
• Business accounts
• Enterprise accounts
• Team management
• Administrative subscription management
"""
    )

    # ========================================================
    # SAFETY / PAYMENT NOTICE
    # ========================================================

    st.caption(
        "🔐 Payment processing is intentionally disabled in this "
        "development version. Never enter payment PINs or "
        "financial credentials into this test form."
    )