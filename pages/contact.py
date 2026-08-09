import streamlit as st
from utils.database import save_message

def show_page():

    st.title("📞 Contact Pan Ideate Africa")

    st.success(
        "Welcome to Pan Ideate Africa — Building Africa Through Science, "
        "Innovation & Practical Education."
    )

    st.markdown("---")

    # ==========================================================
    # INTRODUCTION
    # ==========================================================

    st.header("🌍 Get in Touch")

    st.write(
        """
        Pan Ideate Africa is building a practical African knowledge platform
        where young people, schools, researchers, entrepreneurs and innovators
        can learn, practice, produce, earn and innovate.

        We welcome questions, ideas, partnerships, research collaboration,
        training opportunities and innovation proposals.
        """
    )

    st.markdown("---")

    # ==========================================================
    # CONTACT INFORMATION
    # ==========================================================

    st.header("📱 Our Contact Details")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🌐 Website")

        st.write("**www.panideateafrica.com**")

        st.link_button(
            "🌐 Visit Pan Ideate Africa Website",
            "https://www.panideateafrica.com"
        )

    with col2:
        st.subheader("📞 Phone / WhatsApp")

        st.write("**+256 787 098 089**")

        st.link_button(
            "💬 Contact Us on WhatsApp",
            "https://wa.me/256787098089"
        )

    st.markdown("---")

    # ==========================================================
    # EMAIL
    # ==========================================================

    st.header("📧 Email")

    st.info(
        "Email contact will be connected here when the official "
        "Pan Ideate Africa email address is ready."
    )

    # ==========================================================
    # AREAS OF CONTACT
    # ==========================================================

    st.header("🤝 How Can We Work Together?")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🎓 Education")

        st.write(
            """
            Schools, universities, teachers and students can contact us
            about practical science education, minerals, chemistry,
            agriculture, technology and innovation.
            """
        )

    with col2:
        st.subheader("🔬 Research")

        st.write(
            """
            Researchers and technical professionals can contact us about
            research collaboration, practical experiments, minerals,
            chemistry and African knowledge development.
            """
        )

    with col3:
        st.subheader("💡 Innovation")

        st.write(
            """
            Innovators and entrepreneurs can contact us about ideas,
            products, prototypes, technology and business opportunities.
            """
        )

    st.markdown("---")

    # ==========================================================
    # DONATIONS AND PARTNERSHIPS
    # ==========================================================

    st.header("❤️ Donations & Partnerships")

    st.write(
        """
        If you would like to support Pan Ideate Africa through donations,
        research support, equipment, training, partnerships or other forms
        of collaboration, please visit our Donations & Partnerships Centre.
        """
    )

    if st.button(
        "❤️ Go to Donations & Partnerships",
        use_container_width=True
    ):
        st.info(
            "Please select **❤️ Donations & Partnerships** from the "
            "navigation menu."
        )

    st.markdown("---")

    # ==========================================================
    # MESSAGE
    # ==========================================================

    st.header("✉️ Send Us a Message")

    with st.form("contact_form"):

        name = st.text_input("Your Name")

        organisation = st.text_input(
            "Organisation / Institution (optional)"
        )

        subject = st.text_input("Subject")

        message = st.text_area(
            "Your Message",
            height=150
        )

        submitted = st.form_submit_button(
            "📨 Submit Message",
            use_container_width=True
        )

    if submitted:

       if name and message:

        save_message(
            name=name,
            organisation=organisation,
            subject=subject,
            message=message
        )

        st.success(
            "Thank you! Your message has been received. "
            "We will follow up using the contact details you provide."
        )

    else:

        st.warning(
            "Please enter your name and message before submitting."
        )

    st.markdown("---")

    # ==========================================================
    # OUR MISSION
    # ==========================================================

    st.header("🎯 Our Mission")

    st.write(
        """
        We aim to expand access to practical science, technology,
        agriculture, minerals, artificial intelligence, entrepreneurship
        and youth skills development across Africa.
        """
    )

    st.markdown("---")

    # ==========================================================
    # FINAL CONTACT BOX
    # ==========================================================

    st.success(
        """
        🌍 PAN IDEATE AFRICA

        Building Africa Through Science, Innovation & Practical Education.

        🌐 www.panideateafrica.com

        📞 +256 787 098 089

        💬 WhatsApp: +256 787 098 089
        """
    )

    st.caption(
        "Pan Ideate Africa — Learn • Practice • Produce • Earn • Innovate"
    )