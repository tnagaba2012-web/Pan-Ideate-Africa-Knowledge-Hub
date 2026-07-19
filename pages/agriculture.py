import streamlit as st
def technology_card(icon, title, description):
    with st.container(border=True):
        st.subheader(f"{icon} {title}")
        st.write(description)

def show_page():

    # ==========================================================
    # HERO SECTION
    # ==========================================================

    st.title("🌱 Agriculture Innovation Centre")

    st.subheader(
        "Empowering Uganda Through Science, Innovation and Sustainable Agriculture"
    )

    st.write("""
Welcome to the **Agriculture Innovation Centre** of the **Pan Ideate Africa Knowledge Hub**.

This centre brings together practical agricultural knowledge, science, mineral technologies,
and innovation to improve food production, create employment, and promote sustainable farming
across Uganda and Africa.

Whether you are a farmer, student, researcher, entrepreneur or innovator,
this platform is designed to help you learn, practice, produce, innovate and earn.
""")

    st.divider()

    # ==========================================================
    # MISSION
    # ==========================================================

    st.header("🎯 Our Mission")

    st.info("""
To become Africa's leading agricultural innovation platform by combining scientific
knowledge, local resources, practical training, and modern technologies that improve
food security and create sustainable businesses.
""")

    st.divider()

    # ==========================================================
    # FOCUS AREAS
    # ==========================================================

    st.header("🌍 Focus Areas")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.success("🌱 Soil Improvement")
        st.success("💧 Water Retention")
        st.success("🌾 Crop Production")

    with col2:
        st.success("🪨 Kaolin Applications")
        st.success("🔥 Biochar Technologies")
        st.success("🧱 Bentonite Solutions")

    with col3:
        st.success("🐄 Livestock Innovation")
        st.success("🚜 Agribusiness")
        st.success("🎓 Agricultural Education")

    st.divider()

    # ==========================================================
    # DASHBOARD
    # ==========================================================

    st.header("📊 Innovation Dashboard")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Projects", "25+")

    with c2:
        st.metric("Technologies", "80+")

    with c3:
        st.metric("Training Modules", "40+")

    with c4:
        st.metric("Focus", "Uganda & Africa")

   st.divider()

# ==========================================================
# FEATURED TECHNOLOGIES
# ==========================================================

st.header("🚀 Featured Technologies")

col1, col2 = st.columns(2)

with col1:
    technology_card(
        "🔥",
        "Biochar",
        "Improve soil fertility, increase crop yields, retain moisture and store carbon."
    )

    technology_card(
        "🪨",
        "Kaolin",
        "Used in crop protection, seed coating, moisture conservation and agricultural research."
    )

    technology_card(
        "🧱",
        "Bentonite",
        "Excellent for water retention, livestock feed binders and fertilizer improvement."
    )

with col2:
    technology_card(
        "💧",
        "Water Retention",
        "Innovative technologies that help crops survive drought and reduce irrigation costs."
    )

    technology_card(
        "🐄",
        "Livestock Innovation",
        "Modern animal nutrition, mineral supplements and sustainable livestock management."
    )

    technology_card(
        "🌾",
        "Climate Smart Agriculture",
        "Technologies that increase productivity while adapting to climate change."
    )

st.divider()

# ==========================================================
# COMING NEXT
# ==========================================================

st.info("""
🚀 Version 1.2 will introduce:

• Uganda Agricultural Opportunities
• Expandable Knowledge Library
• Project Guides
• Image Gallery
• Interactive Learning Sections
""")

st.success("✅ Agriculture Innovation Centre Version 1.1 Running Successfully")

st.caption(
    "Pan Ideate Africa Ltd | Learn → Practice → Produce → Innovate → Earn"
)