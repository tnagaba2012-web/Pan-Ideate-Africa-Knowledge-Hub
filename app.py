import streamlit as st
from pages import home
from pages import minerals
from pages import agriculture
from pages import business_suite
from pages import handbook
from pages import artificial_intelligence
from pages import learning
from pages import innovation
from pages import contact
from pages import languages
from pages import donations
from pages import iron_oxide
from pigment_preparation.main import show_pigment_preparation
from admin import show_admin
# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="Pan Ideate Africa Knowledge Hub",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM STYLING
# ============================================

st.markdown("""
<style>

.main {
    background-color: #f7f9fc;
}

h1,h2,h3{
    color:#0B6E4F;
}



.project-card{
    background:white;
    padding:20px;
    border-radius:12px;
    border-left:8px solid #0B6E4F;
    box-shadow:0 4px 12px rgba(0,0,0,0.08);
    margin-bottom:20px;
}

.footer{
    text-align:center;
    color:gray;
    padding-top:40px;
}

</style>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================

st.sidebar.title("🌍 Pan Ideate Africa")

st.sidebar.markdown("### Knowledge Hub")

page = st.sidebar.radio(

    "Navigation",

    [

        "🏠 Home",
        "🌍 Choose a Language",  
        "🧪 Minerals & Chemistry",
        "📖 Uganda Minerals Handbook",
        "🗺️ Project Roadmap",
        "🌱 Agriculture",
        "❤️ Donations & Partnerships",
        "💼 Business Suite",
        "🟥 Iron Oxide Pigments Handbook",
        "🧪 Pigment Preparation Laboratory",
        "🤖 Artificial Intelligence",
        "🔐 Admin Centre",
        "📚 Learning Centre",

        "🚀 Innovation",

        "📞 Contact"

    ]

)

st.sidebar.divider()

st.sidebar.success("🚀 Empowering Africa Through Knowledge")

# ============================================
# HOME
# ============================================

if page == "🏠 Home":
    home.show_page()

# ============================================
# MINERALS
# ============================================

elif page == "🧪 Minerals & Chemistry":
    minerals.show_page()
elif page == "📖 Uganda Minerals Handbook":
    handbook.show_page()
elif page == "🟥 Iron Oxide Pigments Handbook":
    iron_oxide.show_page()
elif page == "🧪 Pigment Preparation Laboratory":
    show_pigment_preparation()
# ============================================
elif page == "🗺️ Project Roadmap":

    st.title("🗺️ Pan Ideate Africa Project Roadmap")

    st.success("Building Africa's Leading Science, Minerals & Innovation Knowledge Hub")

    st.header("✅ Completed")
    st.markdown("""
- Streamlit Knowledge Hub
- Chapter 1 Handbook
- GitHub Backup
- Stable Project Versions
- Media Folder Structure
""")

    st.header("🚧 Currently Building")
    st.markdown("""
- Project Roadmap
- Mineral Gallery
- Educational Media Pack
""")

    st.header("🎯 Coming Next")
    st.markdown("""
- Uganda Minerals Gallery
- Interactive Maps
- Chemistry Diagrams
- AI Assistant
- Agriculture Innovation Centre
- Innovation Marketplace
""")
elif page == "🌱 Agriculture":
    agriculture.show_page()

# ============================================
# ============================================
# BUSINESS SUITE
# ============================================

elif page == "💼 Business Suite":
   business_suite.show_business_suite()
elif page == "🤖 Artificial Intelligence":
    artificial_intelligence.show_page()
elif page == "🌍 Choose a Language":
    languages.show_page()
    
elif page == "❤️ Donations & Partnerships":
    donations.show_page()
# ============================================
elif page=="🔐 Admin Centre":
    show_admin()
# ============================================================
# LEARNING CENTRE
# ============================================================

elif page == "📚 Learning Centre":
    learning.show_page()


# ============================================================
# INNOVATION
# ============================================================

elif page == "🚀 Innovation":
    innovation.show_page()


# ============================================================
# CONTACT
# ============================================================

elif page == "📞 Contact":

    st.title("📞 Contact Pan Ideate Africa")

    st.success(
        "Welcome to Pan Ideate Africa — Building Africa Through Science, "
        "Innovation & Practical Education."
    )

    st.markdown("---")

    st.header("🌍 Get in Touch")

    st.write(
        "Pan Ideate Africa is building a practical African knowledge platform "
        "where young people, schools, researchers, entrepreneurs and innovators "
        "can learn, practice, produce, earn and innovate."
    )

    st.write(
        "We welcome questions, ideas, partnerships, research collaboration, "
        "training opportunities and innovation proposals."
    )

    st.markdown("---")

    st.header("📱 Our Contact Details")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📞 Phone / WhatsApp")
        st.write("+256 775 169 458")

        st.markdown(
            '[💬 WhatsApp — 0775 169 458]'
            '(https://wa.me/256775169458)'
        )

        st.markdown(
            '[🔵 Signal — 0775 169 458]'
            '(https://signal.me/#p/+256775169458)'
        )

    with col2:
        st.subheader("📞 Phone / WhatsApp")
        st.write("+256 787 098 089")

        st.markdown(
            '[💬 WhatsApp — 0787 098 089]'
            '(https://wa.me/256787098089)'
        )

        st.markdown(
            '[🔵 Signal — 0787 098 089]'
            '(https://signal.me/#p/+256787098089)'
        )

    st.markdown("---")

    st.subheader("🌐 Website")

    st.markdown(
        "[Visit Pan Ideate Africa Website](https://www.panideateafrica.com)"
    )

    st.markdown("---")

    st.subheader("🤝 How Can We Work Together?")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🎓 Education")
        st.write(
            "Schools, universities, teachers and students can contact us "
            "about practical science education, minerals, chemistry, "
            "agriculture, technology and innovation."
        )

    with col2:
        st.markdown("### 🔬 Research")
        st.write(
            "Researchers and technical professionals can contact us about "
            "research collaboration, practical experiments, minerals, "
            "chemistry and African knowledge development."
        )

    with col3:
        st.markdown("### 💡 Innovation")
        st.write(
            "Innovators and entrepreneurs can contact us about ideas, "
            "products, prototypes, technology and business opportunities."
        )

    st.markdown("---")

    st.header("❤️ Donations & Partnerships")

    st.write(
        "If you would like to support Pan Ideate Africa through donations, "
        "research support, equipment, training, partnerships or other forms "
        "of collaboration, please visit our Donations & Partnerships Centre."
    )

    st.markdown("---")

    st.subheader("✉️ Send Us a Message")

    name = st.text_input("Your Name")
    organization = st.text_input("Organization / Institution (optional)")
    subject = st.text_input("Subject")
    message = st.text_area("Your Message")

    if st.button("📨 Submit Message"):
        st.success(
            "Thank you! Your message has been received by the Pan Ideate Africa "
            "Knowledge Hub."
        )
# ============================================
# FOOTER
# ============================================

st.divider()

st.markdown(
"""
<div class="footer">

© 2026 Pan Ideate Africa Ltd.

Version 8 • Build 8.0

</div>
""",
unsafe_allow_html=True
)