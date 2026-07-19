import streamlit as st


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

    st.success("✅ Agriculture Innovation Centre Version 1.0 Loaded Successfully")

    st.caption("Pan Ideate Africa Ltd | Learn → Practice → Produce → Innovate → Earn")