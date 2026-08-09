import streamlit as st


def show_page():

    st.title("💡 Pan Ideate Africa Innovation Centre")

    st.success(
        "Welcome to the Pan Ideate Africa Innovation Centre!"
    )

    st.markdown("---")

    # ==========================================================
    # INTRODUCTION
    # ==========================================================

    st.header("🚀 Innovation for Africa")

    st.write(
        """
        The Pan Ideate Africa Innovation Centre is designed to help
        African young people, students, researchers, entrepreneurs and
        innovators transform ideas into practical solutions.

        Our approach is simple:

        **Learn → Practice → Produce → Earn → Innovate**
        """
    )

    st.markdown("---")

    # ==========================================================
    # THREE MAIN AREAS
    # ==========================================================

    st.header("🌍 What Innovation Means Here")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.subheader("💡 Ideas")

        st.write(
            """
            We encourage young people to identify problems in their
            communities and develop practical ideas to solve them.
            """
        )

    with col2:

        st.subheader("🧪 Prototypes")

        st.write(
            """
            Ideas can be transformed into experiments, prototypes,
            demonstrations and practical products.
            """
        )

    with col3:

        st.subheader("💰 Enterprise")

        st.write(
            """
            Promising innovations can be developed into businesses,
            enterprises and income-generating opportunities.
            """
        )

    st.markdown("---")

    # ==========================================================
    # INNOVATION AREAS
    # ==========================================================

    st.header("🔬 Our Innovation Areas")

    innovation_areas = [

        "⛏️ Minerals & Chemistry",

        "🌱 Agriculture & Biochar",

        "🧱 Sustainable Building Materials",

        "🎨 Iron Oxide Pigments",

        "🪨 Kaolin & Clay Applications",

        "💧 Water Retention Technologies",

        "🤖 Artificial Intelligence",

        "💻 Digital Technology",

        "🎓 Practical Education",

        "🏭 Small-Scale Manufacturing",

        "♻️ Environmental Innovation",

        "🚀 Youth Entrepreneurship",
    ]

    for area in innovation_areas:

        st.write(f"### {area}")

    st.markdown("---")

    # ==========================================================
    # CURRENT PROJECTS
    # ==========================================================

    st.header("🛠️ Innovation Projects")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🎨 Iron Oxide Pigments")

        st.write(
            """
            Exploring locally available iron-rich materials and developing
            practical pigment preparation methods and applications.
            """
        )

        st.subheader("🌱 Biochar")

        st.write(
            """
            Exploring biochar applications in agriculture, soil improvement,
            water management and value-added agricultural products.
            """
        )

        st.subheader("🪨 Kaolin")

        st.write(
            """
            Investigating kaolin properties and potential applications
            in agriculture, materials and practical chemistry.
            """
        )

    with col2:

        st.subheader("🧱 Building Materials")

        st.write(
            """
            Developing ideas around sustainable bricks, tiles, clay-based
            materials and locally sourced construction materials.
            """
        )

        st.subheader("💧 Water Retention")

        st.write(
            """
            Exploring materials and formulations that can help improve
            water retention and agricultural productivity.
            """
        )

        st.subheader("🤖 Artificial Intelligence")

        st.write(
            """
            Using AI and digital technologies to improve learning,
            entrepreneurship, research and innovation.
            """
        )

    st.markdown("---")

    # ==========================================================
    # INNOVATION PROCESS
    # ==========================================================

    st.header("🔄 Our Innovation Process")

    steps = [

        ("1️⃣ Identify",
         "Identify a real problem or opportunity."),

        ("2️⃣ Research",
         "Study the science, materials, technology and market."),

        ("3️⃣ Experiment",
         "Test the idea through practical experiments."),

        ("4️⃣ Prototype",
         "Build and improve a working prototype."),

        ("5️⃣ Validate",
         "Test quality, safety, usefulness and feasibility."),

        ("6️⃣ Produce",
         "Develop a practical production process."),

        ("7️⃣ Market",
         "Connect the innovation to real customers and markets."),

        ("8️⃣ Scale",
         "Develop partnerships and expand the successful innovation."),
    ]

    for title, description in steps:

        st.subheader(title)

        st.write(description)

    st.markdown("---")

    # ==========================================================
    # INNOVATION MARKETPLACE
    # ==========================================================

    st.header("🛒 Innovation Marketplace")

    st.write(
        """
        The future Pan Ideate Africa Innovation Marketplace will provide
        a space where African innovators can showcase:

        • Products

        • Prototypes

        • Research outputs

        • Agricultural technologies

        • Mineral-based products

        • Educational innovations

        • Digital solutions

        • Business ideas
        """
    )

    st.info(
        "Innovation Marketplace features will be connected as the platform develops."
    )

    st.markdown("---")

    # ==========================================================
    # YOUTH INNOVATION
    # ==========================================================

    st.header("👨‍🎓 Youth Innovation")

    st.write(
        """
        Pan Ideate Africa aims to give young Africans an opportunity to
        move beyond theoretical learning and participate in practical
        problem-solving.

        Young people should be able to learn a skill, practice it,
        develop something useful and eventually create an income from it.
        """
    )

    st.markdown("---")

    # ==========================================================
    # PARTNERSHIPS
    # ==========================================================

    st.header("🤝 Innovation Partnerships")

    st.write(
        """
        We welcome partnerships with:

        • Schools

        • Universities

        • Research institutions

        • Government programmes

        • Businesses

        • NGOs

        • Technology organisations

        • Agricultural organisations

        • Manufacturing companies

        • Investors and development partners
        """
    )

    st.markdown("---")

    # ==========================================================
    # CONTACT
    # ==========================================================

    st.header("📞 Want to Support Innovation?")

    st.write(
        """
        If you would like to support an innovation project, collaborate
        with Pan Ideate Africa, provide equipment, provide technical
        expertise or develop a partnership, please contact us.
        """
    )

    st.success(
        """
        🌐 Website: www.panideateafrica.com

        📞 Phone / WhatsApp: +256 787 098 089
        """
    )

    st.link_button(
        "💬 Contact Pan Ideate Africa on WhatsApp",
        "https://wa.me/256787098089",
        use_container_width=True
    )

    st.markdown("---")

    st.caption(
        "Pan Ideate Africa — Learn • Practice • Produce • Earn • Innovate"
    )