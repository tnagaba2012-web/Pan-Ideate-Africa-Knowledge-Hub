import streamlit as st
from utils.database import save_donation, save_partnership


def show_page():
    st.title("❤️ Donations & Partnerships Centre")

    st.success(
        "Welcome to the Pan Ideate Africa Donations & Partnerships Centre!"
    )

    st.write(
        """
        Pan Ideate Africa is building a practical African knowledge platform
        where young people, schools, researchers, entrepreneurs and innovators
        can learn, practice, produce, earn and innovate.

        Your support can help us expand access to practical science, technology,
        agriculture, minerals, artificial intelligence, business development
        and youth skills.
        """
    )

    st.divider()

    # ============================================================
    # WHAT SUPPORT MAKES POSSIBLE
    # ============================================================

    st.header("🌍 What Your Support Makes Possible")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🔬 Science")
        st.write(
            "Support practical science learning, experiments and research."
        )

    with col2:
        st.subheader("🌱 Agriculture")
        st.write(
            "Support agricultural innovation, biochar, soil improvement "
            "and practical farming knowledge."
        )

    with col3:
        st.subheader("💡 Innovation")
        st.write(
            "Help young Africans develop useful ideas, products and businesses."
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        st.subheader("🪨 Minerals")
        st.write(
            "Support practical mineral and chemistry education using "
            "African resources."
        )

    with col5:
        st.subheader("🤖 AI & Technology")
        st.write(
            "Help young people access artificial intelligence and "
            "digital learning tools."
        )

    with col6:
        st.subheader("🎓 Youth Skills")
        st.write(
            "Support training, learning resources and entrepreneurship."
        )

    st.divider()

    # ============================================================
    # DONATIONS
    # ============================================================

    st.header("💝 Support Pan Ideate Africa")

    st.write(
        """
        Individuals, organisations, schools and institutions can express
        their interest in supporting Pan Ideate Africa.

        Your contribution may support learning materials, practical
        demonstrations, research, technology, youth training and innovation.
        """
    )

    st.subheader("💰 Donation / Support Interest Form")

    with st.form("donation_form"):
        donor_name = st.text_input(
            "Your name *"
        )

        organisation = st.text_input(
            "Organisation / Institution (optional)"
        )

        contribution_type = st.selectbox(
            "How would you like to support?",
            [
                "Financial contribution",
                "Learning materials",
                "Laboratory equipment",
                "Computers / technology",
                "Training support",
                "Research support",
                "Other"
            ]
        )

        amount = st.text_input(
            "Estimated contribution amount (UGX, optional)"
        )

        donor_contact = st.text_input(
            "Phone number or email *"
        )

        donor_message = st.text_area(
            "Additional message (optional)"
        )

        donation_submitted = st.form_submit_button(
            "❤️ Submit Support Interest"
        )

        if donation_submitted:

            if not donor_name.strip() or not donor_contact.strip():
                st.error(
                    "Please provide your name and phone number or email."
                )
            else:
                save_donation(
                    name=donor_name,
                    organisation=organisation,
                    contribution_type=contribution_type,
                    amount=amount,
                    contact=donor_contact,
                    message=donor_message
                )

                st.success(
                    "Thank you for your interest in supporting Pan Ideate Africa! "
                    "Your support request has been recorded for follow-up."
                )

                st.info(
                    "Contribution processing and payment options can be "
                    "connected here once the official Pan Ideate Africa "
                    "payment channels are ready."
                )

    st.divider()

    # ============================================================
    # PARTNERSHIPS
    # ============================================================

    st.header("🤝 Partnerships")

    st.write(
        """
        Pan Ideate Africa welcomes partnerships that can strengthen
        African education, science, agriculture, technology, innovation
        and entrepreneurship.
        """
    )

    st.subheader("Partnership Opportunities")

    partnership_options = [
        "School / University Partnership",
        "NGO / Community Partnership",
        "Corporate Partnership",
        "Government / Institutional Partnership",
        "Research Partnership",
        "Agriculture Partnership",
        "Science & Technology Partnership",
        "Innovation Partnership",
        "Other"
    ]

    selected_partnership = st.selectbox(
        "Partnership type",
        partnership_options
    )

    with st.form("partnership_form"):

        partner_name = st.text_input(
            "Your name *",
            key="partner_name"
        )

        partner_organisation = st.text_input(
            "Organisation / Institution *",
            key="partner_organisation"
        )

        partner_contact = st.text_input(
            "Phone number or email *",
            key="partner_contact"
        )

        partnership_message = st.text_area(
            "Tell us about your partnership idea *"
        )

        partnership_submitted = st.form_submit_button(
            "🤝 Submit Partnership Enquiry"
        )

        if partnership_submitted:

            if (
                not partner_name.strip()
                or not partner_organisation.strip()
                or not partner_contact.strip()
                or not partnership_message.strip()
            ):
                st.error(
                    "Please complete all required partnership fields."
                )
            else:
                save_partnership(
                    name=partner_name,
                    
                    organisation=partner_organisation,
                    contact=partner_contact,
                     partnership_type=selected_partnership,
                    idea=partnership_message
                )

                st.success(
                    "Thank you! Your partnership enquiry has been received."
                )

                st.write(
                    f"**Partnership type:** {selected_partnership}"
                )

                st.info(
                    "The Pan Ideate Africa team can follow up using the "
                    "contact information you provided."
                )

    st.divider()

    # ============================================================
    # CONTACT / TRUST
    # ============================================================

    st.header("📞 Contact & Support")

    st.write(
        """
        We welcome individuals and organisations that believe in practical
        African education, innovation and youth empowerment.

        For now, please use the forms above to express your interest.
        Official payment channels and additional contact details can be
        connected here when they are ready.
        """
    )

    st.warning(
        "⚠️ Important: Do not send passwords, PINs, bank passwords or "
        "other confidential security information through these forms."
    )

    st.divider()

    st.success(
        "🌍 Together, we can Learn → Practice → Produce → Earn → Innovate."
    )