import streamlit as st


def show_page():

    st.title("📚 Pan Ideate Africa Learning Centre")

    st.success(
        "Welcome to the Pan Ideate Africa Learning Centre!"
    )

    st.markdown("---")

    # ==========================================================
    # INTRODUCTION
    # ==========================================================

    st.header("🌍 Learn. Practice. Produce. Earn. Innovate.")

    st.write(
        """
        The Pan Ideate Africa Learning Centre is designed to provide
        practical African education for young people, schools, students,
        researchers, entrepreneurs and innovators.

        Our goal is to connect knowledge with practical work.

        Learning should not end with theory.

        We want learners to understand an idea, practice it, develop
        something useful and discover opportunities to create value.
        """
    )

    st.markdown("---")

    # ==========================================================
    # LEARNING MODEL
    # ==========================================================

    st.header("🎯 Our Learning Model")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.subheader("📖 Learn")
        st.write(
            "Understand the science, technology, agriculture and business."
        )

    with col2:
        st.subheader("🧪 Practice")
        st.write(
            "Turn knowledge into practical experiments and activities."
        )

    with col3:
        st.subheader("🏭 Produce")
        st.write(
            "Develop useful products, prototypes and solutions."
        )

    with col4:
        st.subheader("💰 Earn")
        st.write(
            "Explore entrepreneurship and income-generating opportunities."
        )

    with col5:
        st.subheader("💡 Innovate")
        st.write(
            "Improve ideas and create new African solutions."
        )

    st.markdown("---")

    # ==========================================================
    # MAIN LEARNING AREAS
    # ==========================================================

    st.header("📚 Learning Areas")

    learning_areas = [

        "⛏️ Minerals & Chemistry",

        "🌱 Agriculture",

        "🤖 Artificial Intelligence",

        "💼 Business Development",

        "🧪 Practical Science",

        "🔬 Research & Experimentation",

        "💡 Innovation",

        "🌍 African Knowledge",

        "👨‍🎓 Youth Skills Development",

        "🏭 Entrepreneurship & Production",
    ]

    for area in learning_areas:

        st.write(f"### {area}")

    st.markdown("---")

    # ==========================================================
    # MINERALS & CHEMISTRY
    # ==========================================================

    st.header("⛏️ Minerals & Chemistry Learning")

    st.write(
        """
        Learners can explore minerals, rocks, chemistry and practical
        applications using locally available materials.

        Topics can include:

        • Minerals and rocks

        • Mineral identification

        • Basic chemistry

        • Clay minerals

        • Iron oxide pigments

        • Kaolin

        • Bentonite

        • Silica and sand

        • Materials processing

        • Practical laboratory work
        """
    )

    st.markdown("---")

    # ==========================================================
    # AGRICULTURE
    # ==========================================================

    st.header("🌱 Agriculture Learning")

    st.write(
        """
        Agriculture learning connects scientific knowledge with practical
        farming and agricultural innovation.

        Areas include:

        • Soil improvement

        • Biochar

        • Water retention

        • Sustainable agriculture

        • Agricultural materials

        • Crop productivity

        • Agricultural entrepreneurship
        """
    )

    st.markdown("---")

    # ==========================================================
    # ARTIFICIAL INTELLIGENCE
    # ==========================================================

    st.header("🤖 Artificial Intelligence")

    st.write(
        """
        Learners can explore how artificial intelligence can support
        education, agriculture, research, business development,
        entrepreneurship and innovation.
        """
    )

    st.markdown("---")

    # ==========================================================
    # BUSINESS
    # ==========================================================

    st.header("💼 Business & Entrepreneurship")

    st.write(
        """
        Knowledge should create opportunities.

        The Learning Centre will help learners understand:

        • Business ideas

        • Product development

        • Market research

        • Costing

        • Production

        • Marketing

        • Entrepreneurship

        • Business planning
        """
    )

    st.markdown("---")

    # ==========================================================
    # PRACTICAL PROJECTS
    # ==========================================================

    st.header("🛠️ Practical Learning Projects")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🎨 Iron Oxide Pigments")

        st.write(
            """
            Learn about iron-rich materials, pigment preparation,
            processing and potential applications.
            """
        )

        st.subheader("🌱 Biochar")

        st.write(
            """
            Explore biochar production and agricultural applications.
            """
        )

        st.subheader("🪨 Kaolin")

        st.write(
            """
            Study kaolin properties and possible practical applications.
            """
        )

    with col2:

        st.subheader("🧱 Building Materials")

        st.write(
            """
            Explore clay, bricks, tiles and sustainable construction
            materials.
            """
        )

        st.subheader("💧 Water Retention")

        st.write(
            """
            Study materials and approaches that may improve agricultural
            water management.
            """
        )

        st.subheader("💡 Innovation Projects")

        st.write(
            """
            Turn learning into practical ideas, prototypes and products.
            """
        )

    st.markdown("---")

    # ==========================================================
    # HANDBOOKS
    # ==========================================================

    st.header("📘 Knowledge & Handbooks")

    st.write(
        """
        The Pan Ideate Africa Knowledge Hub will progressively provide
        structured learning materials, handbooks, practical guides,
        demonstrations and project-based learning resources.
        """
    )

    st.info(
        "📘 Uganda Minerals Handbook and other learning resources are "
        "being developed as part of the Knowledge Hub."
    )

    st.markdown("---")

    # ==========================================================
    # WHO CAN USE THE CENTRE?
    # ==========================================================

    st.header("👥 Who Can Learn Here?")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.subheader("🎓 Students")

        st.write(
            "Practical learning, projects, demonstrations and skills."
        )

    with col2:

        st.subheader("🏫 Schools")

        st.write(
            "Science education, practical activities and innovation."
        )

    with col3:

        st.subheader("👨‍🔬 Researchers")

        st.write(
            "Research ideas, experiments and African knowledge development."
        )

    st.markdown("---")

    # ==========================================================
    # FUTURE LEARNING PLATFORM
    # ==========================================================

    st.header("🚀 Future Learning Platform")

    st.write(
        """
        As Pan Ideate Africa develops, the Learning Centre can grow into
        an interactive learning platform containing:

        • Courses

        • Practical lessons

        • Quizzes

        • Project guides

        • Demonstrations

        • Learning progress

        • Certificates

        • Research resources

        • Community learning

        • Multilingual learning
        """
    )

    st.markdown("---")

    # ==========================================================
    # AFRICAN LANGUAGES
    # ==========================================================

    st.header("🌍 African Language Support")

    st.write(
        """
        The long-term learning vision includes support for African learners
        through multiple languages.

        Planned language support includes:

        🇺🇬 Luganda

        🌍 Swahili

        🇫🇷 French

        🇸🇦 Arabic

        🇬🇧 English
        """
    )

    st.markdown("---")

    # ==========================================================
    # CALL TO ACTION
    # ==========================================================

    st.header("🚀 Start Learning")

    st.write(
        """
        Explore the Knowledge Hub, choose a subject, study the material,
        practice the concepts and work toward a practical project.
        """
    )

    st.success(
        """
        📚 PAN IDEATE AFRICA LEARNING CENTRE

        Learn • Practice • Produce • Earn • Innovate
        """
    )

    st.markdown("---")

    st.caption(
        "Pan Ideate Africa — Building Africa Through Science, "
        "Innovation & Practical Education."
    )