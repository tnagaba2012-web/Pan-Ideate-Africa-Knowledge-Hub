import streamlit as st
from pages import home
from pages import minerals
from pages import agriculture
from pages import business
from pages import ai
from pages import learning
from pages import innovation
from pages import contact
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

div[data-testid="stSidebar"]{
    background-color:#0B6E4F;
}

div[data-testid="stSidebar"] *{
    color:white;
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

        "🧪 Minerals & Chemistry",

        "🌱 Agriculture",

        "💼 Business Development",

        "🤖 Artificial Intelligence",

        "📚 Learning Centre",

        "🚀 Innovation",

        "📞 Contact"

    ]

)

st.sidebar.divider()

st.sidebar.success("Version 7.1")

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

# ============================================

elif page == "🌱 Agriculture":
    agriculture.show_page()

# ============================================

elif page=="🤖 Artificial Intelligence":

    st.title("🤖 Artificial Intelligence")

    st.info("AI Assistant arrives in Build 7.3")

# ============================================

elif page=="📚 Learning Centre":

    st.title("📚 Learning Centre")

    st.info("Learning Centre arrives in Build 7.3")

# ============================================

elif page=="🚀 Innovation":

    st.title("🚀 Innovation")

    st.info("Innovation Hub arrives in Build 7.3")

# ============================================

elif page=="📞 Contact":

    st.title("📞 Contact")

    st.write("""

Pan Ideate Africa Ltd.

Building Africa Through Science,
Innovation & Practical Education.

""")

# ============================================
# FOOTER
# ============================================

st.divider()

st.markdown(
"""
<div class="footer">

© 2026 Pan Ideate Africa Ltd.

Version 7 • Build 7.1

</div>
""",
unsafe_allow_html=True
)