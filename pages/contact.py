import streamlit as st


def show_page():
    st.title("📞 Contact Pan Ideate Africa")

    st.success("Pan Ideate Africa")

    st.write("""
    Pan Ideate Africa is building a practical African knowledge platform
    where young people, schools, researchers, entrepreneurs and innovators
    can learn, practice, produce, earn and innovate.
    """)

    st.divider()

    st.header("📬 Get in Touch")

    st.markdown(
        """
        **🌐 Website:** [www.panideateafrica.com](https://www.panideateafrica.com)

        **📱 Phone / WhatsApp:** [+256 787 098 089](tel:+256787098089)

        **💬 WhatsApp:** [Contact us on WhatsApp](https://wa.me/256787098089)
        """
    )

    st.divider()

    st.header("🤝 Donations & Partnerships")

    st.write("""
    If you would like to support Pan Ideate Africa through donations,
    research support, equipment, training, partnerships or other forms
    of collaboration, please visit the Donations & Partnerships Centre.
    """)

    if st.button("❤️ Go to Donations & Partnerships"):
        st.info("Please select the Donations & Partnerships section from the navigation menu.")

    st.divider()

    st.header("🌍 Our Mission")

    st.write("""
    We aim to expand access to practical science, technology, agriculture,
    minerals, artificial intelligence, entrepreneurship and youth skills
    development across Africa.
    """)

    st.caption("Pan Ideate Africa — Learn • Practice • Produce • Earn • Innovate")