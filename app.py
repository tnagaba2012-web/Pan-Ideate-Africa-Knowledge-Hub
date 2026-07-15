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

if page=="🏠 Home":

    st.title("🌍 Pan Ideate Africa Knowledge Hub")

    st.subheader(
        "Building Africa Through Science, Innovation & Practical Education"
    )

    st.info(
        "Welcome to Version 7 Build 7.1"
    )

    st.write("""

Pan Ideate Africa is building an African knowledge platform
that empowers young people through science, chemistry,
innovation, entrepreneurship and practical education.

This platform will continue growing into one of Africa's
largest knowledge and innovation hubs.

""")

    st.divider()

    col1,col2,col3,col4 = st.columns(4)

    with col1:
        st.metric("Projects","20+")

    with col2:
        st.metric("Research Areas","10+")

    with col3:
        st.metric("Youth Goal","1 Million")

    with col4:
        st.metric("Countries","Africa")

    st.divider()

    st.header("⭐ Featured Projects")

    left,right = st.columns(2)

    with left:

        st.markdown("""
<div class="project-card">

## 🌱 Biochar

Climate-smart agriculture

Carbon storage

Soil improvement

</div>
""",unsafe_allow_html=True)

        st.markdown("""
<div class="project-card">

## 🟤 Bentonite

Water retention

Animal feeds

Industrial applications

</div>
""",unsafe_allow_html=True)

    with right:

        st.markdown("""
<div class="project-card">

## 🧪 Iron Oxide Pigments

Natural pigments

Construction

Education

</div>
""",unsafe_allow_html=True)

        st.markdown("""
<div class="project-card">

## ⚪ Kaolin & Silicon

Advanced materials

Ceramics

Future electronics

</div>
""",unsafe_allow_html=True)

    st.divider()

    st.success("🚀 Version 7 is now under active development.")

# ============================================
# MINERALS
# ============================================

elif page=="🧪 Minerals & Chemistry":

    st.title("🧪 Minerals & Chemistry")

    st.info("Detailed content arrives in Build 7.2")

# ============================================

elif page=="🌱 Agriculture":

    st.title("🌱 Agriculture")

    st.info("Detailed content arrives in Build 7.2")

# ============================================

elif page=="💼 Business Development":

    st.title("💼 Business Development")

    st.info("Detailed content arrives in Build 7.2")

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