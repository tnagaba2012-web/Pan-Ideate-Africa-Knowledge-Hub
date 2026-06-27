import streamlit as st

# -------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------

st.set_page_config(
    page_title="Pan Ideate Africa Knowledge Hub",
    page_icon="🌍",
    layout="wide"
)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

st.sidebar.title("🌍 Pan Ideate Africa")

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

# -------------------------------------------------
# HOME
# -------------------------------------------------

if page == "🏠 Home":

  st.title("🚀 THIS IS VERSION 6") 

  st.subheader(
        "Building Africa Through Science, Innovation & Practical Education"
    )

    
  st.success(
        "Welcome to Version 6 of the Pan Ideate Africa Knowledge Hub."
    )

    
  st.write("""
Our mission is to empower African youth through science,
innovation, entrepreneurship and practical education.

Together we transform ideas into industries.
""")

  st.divider()

  col1, col2, col3 = st.columns(3)

  with col1:
        st.metric("📚 Learning Articles", "250+")

  with col2:
        st.metric("🧪 Science Projects", "40+")

  with col3:
        st.metric("🌱 Innovation Goal", "100+")

  st.divider()

  st.header("⭐ Featured Projects")

  project1, project2 = st.columns(2)

  with project1:
        st.success("🌱 Biochar")
        st.write(
            "Climate-smart agriculture and soil improvement."
        )

        st.success("🟤 Bentonite")
        st.write(
            "Water retention, livestock and industrial products."
        )

  with project2:
        st.success("🧪 Iron Oxide Pigments")
        st.write(
            "Natural pigments for construction and education."
        )

        st.success("⚪ Kaolin & Silicon")
        st.write(
            "Advanced materials for ceramics and future technology."
        )

# -------------------------------------------------
# MINERALS
# -------------------------------------------------

elif page == "🧪 Minerals & Chemistry":

    st.title("🧪 Minerals & Chemistry")

    st.info("Explore Uganda's mineral resources.")

    st.markdown("""
### Topics

- 🟤 Iron Oxide Pigments
- ⚪ Kaolin
- 🟢 Bentonite
- 💎 Silicon
- 🧂 Rock Salt
""")

# -------------------------------------------------
# AGRICULTURE
# -------------------------------------------------

elif page == "🌱 Agriculture":

    st.title("🌱 Agriculture")

    st.write("""
This section will include:

- Biochar
- Water Retention
- Organic Fertilizers
- Climate Smart Agriculture
""")

# -------------------------------------------------
# BUSINESS
# -------------------------------------------------

elif page == "💼 Business Development":

    st.title("💼 Business Development")

    st.write("Business plans, entrepreneurship and investment.")

# -------------------------------------------------
# AI
# -------------------------------------------------

elif page == "🤖 Artificial Intelligence":

    st.title("🤖 Artificial Intelligence")

    st.write("Future Pan Ideate AI Assistant.")

# -------------------------------------------------
# LEARNING
# -------------------------------------------------

elif page == "📚 Learning Centre":

    st.title("📚 Learning Centre")

    st.write("Courses, experiments and practical education.")

# -------------------------------------------------
# INNOVATION
# -------------------------------------------------

elif page == "🚀 Innovation":

    st.title("🚀 Innovation")

    st.write("Showcasing African innovations.")

# -------------------------------------------------
# CONTACT
# -------------------------------------------------

elif page == "📞 Contact":

    st.title("📞 Contact")

    st.write("""
Pan Ideate Africa

Building Africa Through Science,
Innovation & Practical Education.
""")