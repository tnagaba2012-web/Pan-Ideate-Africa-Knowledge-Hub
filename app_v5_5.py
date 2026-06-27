import streamlit as st

st.set_page_config(
    page_title="Pan Ideate Africa Knowledge Hub",
    page_icon="🌍",
    layout="wide"
)
# ======================================
# SIDEBAR
# ======================================

st.sidebar.image(
    "https://img.icons8.com/color/96/africa.png",
    width=80
)

st.sidebar.title("Pan Ideate Africa")

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
# ======================================
# HOME PAGE
# ======================================

if page == "🏠 Home":
    st.title("🌍 Pan Ideate Africa Knowledge Hub")

    st.markdown("""
    # Building Africa Through Science, Innovation & Practical Education

    Welcome to the Pan Ideate Africa Knowledge Hub.

    Our mission is to empower African youth through science,
    technology, innovation, entrepreneurship and practical education.

    Together we can transform ideas into industries.

    """)

    st.info("🚀 Welcome to Version 2 of the Pan Ideate Africa Knowledge Hub!")

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
       st.metric("📚 Learning Articles", "250+")

with col2:
       st.metric("🧪 Science Projects", "40+")

with col3:
       st.metric("🌱 Innovation Goal", "100+")

st.divider()

st.subheader("⭐ Featured Innovation Projects")

project1, project2 = st.columns(2)

with project1:

    st.success("🌱 Biochar Project")

    st.write(
        "Transform agricultural waste into valuable biochar for improving soil fertility and supporting climate-smart agriculture."
    )

    st.success("🟤 Bentonite Project")

    st.write(
        "Develop water-retention products, livestock feed additives and industrial applications using locally available bentonite."
    )

with project2:

    st.success("🧪 Iron Oxide Pigments")

    st.write(
        "Produce natural pigments for paints, construction materials and educational demonstrations."
    )

    st.success("⚪ Kaolin & Silicon")

    st.write(
        "Research advanced materials for ceramics, electronics and future semiconductor industries."
    )

st.divider()

st.success("🌍 Together we are building Africa through Science, Innovation and Practical Education.")
   

st.divider()     
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Projects", "20+")
with col2:
    st.metric("Youth Skills", "100+")
with col3:
    st.metric("Innovation Goal", "Africa")
    st.metric("Youth Skills", "100+")
with col3:
    st.metric("Innovation Goal", "Africa")
st.divider()
st.header("🚀 Featured Projects")

project1, project2 = st.columns(2)

with project1:
    st.info("""
### 🧪 Minerals & Chemistry

Explore Uganda's minerals including:

- Iron Oxide Pigments
- Kaolin
- Bentonite
- Silicon
- Rock Salt

Learn the chemistry, extraction methods and business opportunities.
""")

with project2:
    st.success("""
### 🌱 Agriculture & Innovation

Discover projects in:

- Biochar
- Water Retention
- Organic Fertilizers
- Climate Smart Agriculture
- Youth Agribusiness

Turning science into practical solutions.
""")

st.divider()
st.header("🌟 Our Main Innovation Areas")
st.markdown("""
- 🧪 Minerals & Chemistry
- 🌱 Agriculture
- 🔥 Biochar Technology
- 🧱 Bentonite
- 🤍 Kaolin
- 💎 Silicon
- 🧂 Rock Salt
- 🤖 Artificial Intelligence
- 💼 Business Development
- 📚 Learning Centre
""")
   # ===========================================
# MINERALS & CHEMISTRY PAGE
# ===========================================

if page == "🧪 Minerals & Chemistry":

    st.title("🧪 Minerals & Chemistry")

    st.success("Welcome to the Minerals & Chemistry Department")

    st.write("""
This department explores Uganda's mineral wealth,
chemistry, processing technologies and business opportunities.

Our aim is to transform local minerals into valuable products
that create jobs for African youth.
""")

    st.divider()

    st.subheader("🟤 Iron Oxide Pigments")
    st.write("Natural pigments used in paints, bricks, concrete, roofing tiles and construction materials.")

    st.subheader("🤍 Kaolin")
    st.write("High purity clay used in ceramics, paper, cosmetics, pharmaceuticals and paints.")

    st.subheader("🟢 Bentonite")
    st.write("Used for water retention, drilling mud, animal feeds, fertilizers and environmental protection.")

    st.subheader("⚫ Biochar")
    st.write("Improves soil fertility, stores carbon and increases agricultural productivity.")

    st.subheader("💎 Silicon")
    st.write("Important for electronics, solar panels, glass manufacturing and modern technology.")

    st.subheader("🧂 Rock Salt")
    st.write("Can produce table salt, industrial chemicals and livestock salt licks.")

    st.success("More detailed research articles will be added in Version 5.4.")
import streamlit as st

st.set_page_config(
    page_title="Pan Ideate Africa Knowledge Hub",
    page_icon="🌍",
    layout="wide"
)
# ======================================
# SIDEBAR
# ======================================

st.sidebar.image(
    "https://img.icons8.com/color/96/africa.png",
    width=80
)

st.sidebar.title("Pan Ideate Africa")

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
# ======================================
# HOME PAGE
# ======================================

if page == "🏠 Home":

    st.title("🌍 Pan Ideate Africa Knowledge Hub")

    st.subheader(
        "Building Africa Through Science, Innovation & Entrepreneurship"
    )

    st.success(
        "Welcome to Uganda's future Science, Minerals & Innovation Platform."
    )

  
    st.write("""
Welcome to the Pan Ideate Africa Knowledge Hub.

Our mission is to empower African youth through science,
entrepreneurship and practical education.

This platform will become Africa's largest youth innovation platform.
""")

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Projects", "20+")

    with col2:
        st.metric("Youth Skills", "100+")

    with col3:
        st.metric("Innovation Goal", "Africa")
    st.divider()
st.header("🚀 Featured Projects")

project1, project2 = st.columns(2)

with project1:
    st.info("""
### 🧪 Minerals & Chemistry

Explore Uganda's minerals including:

- Iron Oxide Pigments
- Kaolin
- Bentonite
- Silicon
- Rock Salt

Learn the chemistry, extraction methods and business opportunities.
""")

with project2:
    st.success("""
### 🌱 Agriculture & Innovation

Discover projects in:

- Biochar
- Water Retention
- Organic Fertilizers
- Climate Smart Agriculture
- Youth Agribusiness

Turning science into practical solutions.
""")

st.divider()
st.header("🌟 Our Main Innovation Areas")
st.markdown("""
- 🧪 Minerals & Chemistry
- 🌱 Agriculture
- 🔥 Biochar Technology
- 🧱 Bentonite
- 🤍 Kaolin
- 💎 Silicon
- 🧂 Rock Salt
- 🤖 Artificial Intelligence
- 💼 Business Development
- 📚 Learning Centre
""")
   # ===========================================
# MINERALS & CHEMISTRY PAGE
# ===========================================

if page == "🧪 Minerals & Chemistry":

    st.title("🧪 Minerals & Chemistry")

    st.success("Welcome to the Minerals & Chemistry Department")

    st.write("""
This department explores Uganda's mineral wealth,
chemistry, processing technologies and business opportunities.

Our aim is to transform local minerals into valuable products
that create jobs for African youth.
""")

    st.divider()

    st.subheader("🟤 Iron Oxide Pigments")
    st.write("Natural pigments used in paints, bricks, concrete, roofing tiles and construction materials.")

    st.subheader("🤍 Kaolin")
    st.write("High purity clay used in ceramics, paper, cosmetics, pharmaceuticals and paints.")

    st.subheader("🟢 Bentonite")
    st.write("Used for water retention, drilling mud, animal feeds, fertilizers and environmental protection.")

    st.subheader("⚫ Biochar")
    st.write("Improves soil fertility, stores carbon and increases agricultural productivity.")

    st.subheader("💎 Silicon")
    st.write("Important for electronics, solar panels, glass manufacturing and modern technology.")

    st.subheader("🧂 Rock Salt")
    st.write("Can produce table salt, industrial chemicals and livestock salt licks.")

    st.success("More detailed research articles will be added in Version 5.4.")
