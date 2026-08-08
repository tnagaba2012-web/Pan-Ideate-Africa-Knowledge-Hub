import streamlit as st


def show():
    st.header("💳 Membership & Subscription Plans")

    st.caption("Choose a plan to unlock the Pan Ideate Africa experience.")

    # ============================================================
    # TEST MODE
    # ============================================================

    st.info(
        "🧪 TEST MODE: Subscription buttons are active for testing. "
        "No real payment will be taken."
    )

    # ============================================================
    # PLAN COLUMNS
    # ============================================================

    free, student, professional, enterprise = st.columns(4)

    # ============================================================
    # FREE PLAN
    # ============================================================

    with free:
        st.success("🟢 FREE")

        st.write("""
        ✓ Basic Handbook

        ✓ Community Access

        ✓ Basic AI Assistant

        ✓ News Updates
        """)

        if st.button(
            "Choose FREE",
            key="subscribe_free",
            use_container_width=True
        ):
            st.session_state["selected_plan"] = "FREE"

    # ============================================================
    # STUDENT PLAN
    # ============================================================

    with student:
        st.info("🔵 STUDENT")

        st.write("""
        ✓ Everything in FREE

        ✓ Full Courses

        ✓ Quizzes

        ✓ Certificates
        """)

        if st.button(
            "Subscribe",
            key="subscribe_student",
            use_container_width=True
        ):
            st.session_state["selected_plan"] = "STUDENT"

    # ============================================================
    # PROFESSIONAL PLAN
    # ============================================================

    with professional:
        st.warning("🟠 PROFESSIONAL")

        st.write("""
        ✓ Everything in STUDENT

        ✓ Business Suite

        ✓ Production Guides

        ✓ Premium Downloads
        """)

        if st.button(
            "Subscribe",
            key="subscribe_professional",
            use_container_width=True
        ):
            st.session_state["selected_plan"] = "PROFESSIONAL"

    # ============================================================
    # ENTERPRISE PLAN
    # ============================================================

    with enterprise:
        st.error("👑 ENTERPRISE")

        st.write("""
        ✓ Everything Included

        ✓ AI Business Tools

        ✓ Team Accounts

        ✓ Analytics

        ✓ Priority Support
        """)

        if st.button(
            "Subscribe",
            key="subscribe_enterprise",
            use_container_width=True
        ):
            st.session_state["selected_plan"] = "ENTERPRISE"

    # ============================================================
    # SUBSCRIPTION FORM
    # ============================================================

    if "selected_plan" in st.session_state:

        selected_plan = st.session_state["selected_plan"]

        st.divider()

        st.header(
            f"📝 Subscribe to the {selected_plan} Plan"
        )

        st.write(
            f"You selected the **{selected_plan}** membership plan."
        )

        st.warning(
            "🧪 TEST MODE — This is only a subscription-flow test. "
            "No payment will be processed."
        )

        with st.form("subscription_form"):

            full_name = st.text_input(
                "Full Name",
                placeholder="Enter your full name"
            )

            email = st.text_input(
                "Email Address",
                placeholder="Enter your email address"
            )

            confirm = st.checkbox(
                "I confirm that I want to subscribe to this plan."
            )

            submitted = st.form_submit_button(
                "🚀 TEST SUBSCRIBE",
                use_container_width=True
            )

            if submitted:

                if not full_name:
                    st.error(
                        "Please enter your full name."
                    )

                elif not email:
                    st.error(
                        "Please enter your email address."
                    )

                elif not confirm:
                    st.error(
                        "Please confirm your subscription."
                    )

                else:

                    st.success(
                        f"✅ Subscription request successful!"
                    )

                    st.info(
                        f"""
                        **TEST SUBSCRIPTION**

                        👤 Member: {full_name}

                        📧 Email: {email}

                        💳 Plan: {selected_plan}

                        🧪 Status: TEST SUBSCRIPTION ACTIVE
                        """
                    )

                    st.balloons()

    # ============================================================
    # PREMIUM FEATURES
    # ============================================================

    st.divider()

    st.header("🔒 Premium Features")

    st.write("""
    Premium members will unlock:

    ⭐ Advanced Production Manuals

    ⭐ Business Templates

    ⭐ Equipment Guides

    ⭐ Market Intelligence

    ⭐ AI Business Planning

    ⭐ Downloadable Professional PDFs

    ⭐ Premium Video Lessons

    ⭐ Investor Resources
    """)

    # ============================================================
    # FUTURE DEVELOPMENT
    # ============================================================

    st.info(
        """
        🚀 Future versions will include:

        • Secure user accounts
        • Real subscription management
        • Online payments
        • Automatic membership activation
        • Premium-content access control
        • Member dashboards
        • Subscription history
        • Business and Enterprise accounts
        """
    )