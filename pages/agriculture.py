import streamlit as st


def show_page():

    # =========================================================
    # PAN IDEATE AFRICA - AGRICULTURE INNOVATION CENTRE
    # =========================================================

    st.title("🌱 Agriculture Innovation Centre")

    st.success(
        "Building Africa's Future Through Science, Innovation and Sustainable Agriculture"
    )

    st.markdown("""
    The **Pan Ideate Africa Agriculture Innovation Centre** connects
    mineral science, chemistry, agriculture, technology and entrepreneurship
    to develop practical solutions for Uganda and Africa.

    Our approach is:

    **Learn → Practice → Produce → Earn → Innovate**
    """)

    st.divider()

    # =========================================================
    # FOCUS AREAS
    # =========================================================

    st.header("🌍 Focus Areas")

    focus_areas = [
        "🌱 Soil Improvement",
        "⚪ Kaolin Applications",
        "🐄 Livestock Innovation",
        "💧 Water Retention",
        "🔥 Biochar Technologies",
        "🚜 Agribusiness",
        "🌾 Crop Production",
        "🧱 Bentonite Solutions",
        "🎓 Agricultural Education"
    ]

    cols = st.columns(3)

    for i, area in enumerate(focus_areas):
        with cols[i % 3]:
            st.info(area)

    st.divider()

    # =========================================================
    # AGRICULTURAL INNOVATION DASHBOARD
    # =========================================================

    st.header("📈 Agricultural Innovation Dashboard")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("🌱 Project Areas", "9")

    with c2:
        st.metric("⚪ Kaolin Applications", "10+")

    with c3:
        st.metric("🔥 Biochar Technologies", "5+")

    with c4:
        st.metric("🌍 Focus", "Uganda & Africa")

    st.divider()

    # =========================================================
    # PROJECT SELECTOR
    # =========================================================

    selected = st.selectbox(
        "Choose a project to explore",
        [
            "⚪ Kaolin Applications",
            "🔥 Biochar Technologies",
            "💧 Water Retention",
            "🧱 Bentonite Solutions",
            "🌱 Soil Improvement",
            "🐄 Livestock Innovation",
            "🚜 Agribusiness",
            "🌾 Crop Production",
            "🎓 Agricultural Education"
        ]
    )

    # =========================================================
    # KAOLIN PROJECT
    # =========================================================

    if selected == "⚪ Kaolin Applications":

        st.header("⚪ Kaolin Applications in Agriculture")

        st.markdown("""
        ### Turning Kaolin into Agricultural Technology

        Kaolin is an aluminosilicate clay mineral that can be processed
        into agricultural particle-film products.

        The Pan Ideate Africa project will investigate how locally available
        kaolin can move from:

        **Mineral → Processing → Agricultural Product → Field Trial → Business**
        """)

        st.divider()

        # -----------------------------------------------------
        # KAOLIN TABS
        # -----------------------------------------------------

        tabs = st.tabs([
            "🌿 Applications",
            "🧴 Products",
            "🧪 Chemistry",
            "🏭 Processing",
            "🌾 Crops",
            "💼 Business",
            "🎓 Learning"
        ])

        # =====================================================
        # APPLICATIONS
        # =====================================================

        with tabs[0]:

            st.subheader("🌿 Major Agricultural Applications")

            applications = {

                "☀️ Heat & Sun Protection":
                    """
                    Kaolin particle films can reflect part of incoming
                    radiation and help reduce heat and solar stress on
                    plant surfaces and fruit.
                    """,

                "🐛 Pest Management":
                    """
                    Kaolin particle films can change the physical and
                    visual characteristics of plant surfaces, making
                    them less attractive or suitable to some insect pests.
                    """,

                "💧 Water-Stress Support":
                    """
                    Research has investigated kaolin as a tool for reducing
                    transpiration and supporting plants under water stress.
                    It should be treated as a supplementary technology,
                    not a replacement for good irrigation management.
                    """,

                "🍎 Fruit Protection":
                    """
                    Research has reported reductions in sunburn and other
                    forms of environmental damage in several horticultural
                    crops.
                    """,

                "🌱 Transplant Protection":
                    """
                    Kaolin has been investigated as a means of reducing
                    transplant stress, particularly where water availability
                    is limited.
                    """,

                "🌍 Climate-Smart Agriculture":
                    """
                    Kaolin can form part of an integrated strategy for
                    managing heat, solar radiation, water stress and
                    selected pest pressures.
                    """
            }

            for title, description in applications.items():

                with st.expander(title):

                    st.write(description)

            st.divider()

            st.subheader("🔬 How the Particle Film Works")

            st.markdown("""
            A properly processed kaolin product can be dispersed in water
            and applied to plant surfaces.

            After the water evaporates, mineral particles remain as a
            reflective film.

            The research concept is based on several effects:

            - Reflection of radiation
            - Modification of plant-surface appearance
            - Reduction of solar heating
            - Changes in insect behaviour
            - Possible reduction in transpiration
            - Protection of fruit and leaves from some environmental stresses

            The exact performance depends on the kaolin quality, formulation,
            crop, weather and application conditions.
            """)

        # =====================================================
        # PRODUCTS
        # =====================================================

        with tabs[1]:

            st.subheader("🧴 Potential Kaolin Agricultural Products")

            st.markdown("""
            These are **Pan Ideate Africa product-development concepts**.
            They are not being presented as already-commercialized Pan Ideate
            products.
            """)

            products = [

                (
                    "⚪ Kaolin Agricultural Powder",
                    "Processed agricultural-grade kaolin intended as the raw material for particle-film products.",
                    "Core product"
                ),

                (
                    "💦 Kaolin Particle-Film Suspension",
                    "A liquid product concept designed to be diluted and applied to crop surfaces.",
                    "Product development"
                ),

                (
                    "☀️ Orchard Heat & Sun Protection",
                    "A crop-specific particle-film product for fruit trees exposed to high solar radiation.",
                    "Product development"
                ),

                (
                    "🍅 Vegetable Heat-Stress Protection",
                    "A research product concept for crops such as tomato, pepper and eggplant.",
                    "Field trials required"
                ),

                (
                    "🐛 Kaolin Pest-Management Product",
                    "A particle-film product intended to reduce pressure from selected insect pests.",
                    "Integrated pest management"
                ),

                (
                    "💧 Kaolin Water-Stress Support",
                    "A research product for crops experiencing heat and water stress.",
                    "Field trials required"
                ),

                (
                    "🌱 Nursery & Transplant Product",
                    "A research formulation for supporting young plants during establishment.",
                    "R&D"
                ),

                (
                    "🌾 Kaolin Seed-Coating Research Product",
                    "A research concept for investigating mineral-based seed treatment.",
                    "R&D only"
                ),

                (
                    "🔥 Kaolin + Biochar Research Product",
                    "A research concept combining mineral technology with biochar-based soil improvement.",
                    "R&D only"
                ),

                (
                    "🌱 Kaolin + Fertilizer Research Formulation",
                    "A research concept for combining kaolin with selected agricultural inputs.",
                    "R&D only"
                )
            ]

            for name, description, status in products:

                st.markdown(f"### {name}")

                st.write(description)

                st.caption(f"Development status: {status}")

                st.divider()

            st.info("""
            💡 This product list can later become a full **Pan Ideate Africa
            Agricultural Product Catalogue**, with formulations, packaging,
            costing, testing and business plans added after scientific validation.
            """)

        # =====================================================
        # CHEMISTRY
        # =====================================================

        with tabs[2]:

            st.subheader("🧪 Kaolin Chemistry")

            st.markdown("### Chemical Formula")

            st.latex(r"Al_2Si_2O_5(OH)_4")

            st.write("""
            Kaolin is a hydrated aluminosilicate clay mineral.
            """)

            st.markdown("""
            ### Main Elements

            - Aluminium (Al)
            - Silicon (Si)
            - Oxygen (O)
            - Hydrogen (H)

            ### Agricultural Technology Depends On

            - Mineral purity
            - Particle-size distribution
            - Surface characteristics
            - Water dispersibility
            - Film-forming behaviour
            - Reflective properties
            - Low undesirable contamination
            """)

            st.divider()

            st.subheader("🔬 Why Processing Matters")

            st.markdown("""
            Raw kaolin is not automatically a finished agricultural product.

            The mineral may need beneficiation and particle-size control
            before it can become a consistent agricultural-grade material.

            Therefore our project links:

            **Geology → Mineral Processing → Chemistry → Formulation → Agriculture**
            """)

        # =====================================================
        # PROCESSING
        # =====================================================

        with tabs[3]:

            st.subheader("🏭 From Ugandan Kaolin to Agricultural Product")

            st.markdown("""
            The long-term Pan Ideate Africa production concept is:
            """)

            processing_steps = [

                "1️⃣ Identify and characterize suitable kaolin deposits",

                "2️⃣ Mine and transport selected raw material",

                "3️⃣ Crush and disperse the raw kaolin",

                "4️⃣ Wash and beneficiate the mineral",

                "5️⃣ Remove unwanted coarse particles and impurities",

                "6️⃣ Classify and concentrate the useful kaolin fraction",

                "7️⃣ Dry the processed material",

                "8️⃣ Control particle size through appropriate milling/classification",

                "9️⃣ Test water dispersion and film-forming behaviour",

                "🔟 Develop the selected agricultural formulation",

                "1️⃣1️⃣ Conduct laboratory and greenhouse testing",

                "1️⃣2️⃣ Conduct controlled field trials",

                "1️⃣3️⃣ Analyse crop response and economics",

                "1️⃣4️⃣ Package and label the validated product",

                "1️⃣5️⃣ Move to pilot production and commercialization"
            ]

            for step in processing_steps:
                st.write(step)

            st.divider()

            st.subheader("⚙️ Possible Processing Equipment")

            equipment = [
                "Jaw crusher or suitable primary size-reduction equipment",
                "Clay dispersing/mixing equipment",
                "Washing and classification equipment",
                "Settling or separation systems",
                "Hydrocyclone or equivalent classification technology",
                "Filter or dewatering system",
                "Drying equipment",
                "Fine grinding / micronization equipment",
                "Mixing and formulation equipment",
                "Packaging equipment",
                "Laboratory particle-size and quality-control equipment"
            ]

            for item in equipment:
                st.write("🔹", item)

        # =====================================================
        # CROPS
        # =====================================================

        with tabs[4]:

            st.subheader("🌾 Potential Crop Research Programme")

            st.write("""
            Kaolin should be evaluated crop-by-crop. Results from one crop
            should not automatically be assumed to apply to another.
            """)

            crop_data = [

                {
                    "Crop group": "Fruit trees",
                    "Examples": "Mango, citrus, avocado",
                    "Research focus": "Heat, sunburn, pests, fruit quality"
                },

                {
                    "Crop group": "Vegetables",
                    "Examples": "Tomato, pepper, eggplant",
                    "Research focus": "Heat, water stress, insect pressure"
                },

                {
                    "Crop group": "Legumes",
                    "Examples": "Beans, soybean",
                    "Research focus": "Heat, water stress, pest pressure"
                },

                {
                    "Crop group": "Other crops",
                    "Examples": "Selected cereals and cash crops",
                    "Research focus": "Crop-specific trials"
                }
            ]

            st.dataframe(
                crop_data,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.subheader("🇺🇬 Proposed Uganda Trial Programme")

            trials = [
                "Tomato heat-stress trial",
                "Mango sunburn and fruit-quality trial",
                "Citrus heat-stress trial",
                "Bean water-stress trial",
                "Soybean pest-management trial",
                "Pepper heat-stress trial",
                "Nursery/transplant establishment trial"
            ]

            for trial in trials:
                st.write("🧪", trial)

            st.warning("""
            All field trials should use appropriate controls, record weather
            and crop conditions, and compare results scientifically before
            making commercial claims.
            """)

        # =====================================================
        # BUSINESS
        # =====================================================

        with tabs[5]:

            st.subheader("💼 Kaolin Business Opportunities in Uganda")

            business_opportunities = [

                "⛏️ Kaolin mining and raw-material supply",

                "🏭 Kaolin beneficiation",

                "🧪 Agricultural-grade kaolin processing",

                "🧴 Manufacture of particle-film products",

                "🌾 Crop-protection product distribution",

                "🥭 Orchard protection services",

                "🍅 Vegetable farmer support services",

                "🧪 Agricultural field-testing services",

                "🎓 Kaolin agricultural training",

                "🔬 Laboratory testing and quality-control services",

                "📦 Product packaging and distribution",

                "🌍 East African market development",

                "🚢 Future export opportunities"
            ]

            for opportunity in business_opportunities:
                st.success(opportunity)

            st.divider()

            st.subheader("💰 Youth Enterprise Model")

            st.markdown("""
            A young entrepreneur could eventually participate at different
            levels of the value chain:

            **Level 1:** Mineral collection and supply

            **Level 2:** Mineral processing

            **Level 3:** Product formulation

            **Level 4:** Packaging

            **Level 5:** Farmer distribution

            **Level 6:** Crop application services

            **Level 7:** Field research and data collection

            **Level 8:** Regional commercialization
            """)

            st.warning("""
            Agricultural products must be scientifically validated and comply
            with applicable Ugandan agricultural-product, safety and labelling
            requirements before commercial sale.
            """)

        # =====================================================
        # LEARNING
        # =====================================================

        with tabs[6]:

            st.subheader("🎓 Kaolin Learning Programme")

            lessons = [

                "Mineral identification",

                "Kaolin geology",

                "Kaolin chemistry",

                "Clay mineral structure",

                "Kaolin beneficiation",

                "Particle-size control",

                "Particle-film science",

                "Crop physiology",

                "Heat stress in plants",

                "Water stress in plants",

                "Integrated pest management",

                "Agricultural product formulation",

                "Laboratory quality control",

                "Field trials",

                "Data collection and analysis",

                "Product packaging",

                "Agricultural entrepreneurship"
            ]

            for i, lesson in enumerate(lessons, start=1):
                st.write(f"**Module {i}:** {lesson}")

            st.divider()

            st.success("""
            🎓 The final goal is not simply to teach Kaolin.

            The goal is to teach young people how to take a local mineral,
            understand its chemistry, process it, test it, create a product,
            build a business and solve an agricultural problem.
            """)

        # =====================================================
        # KAOLIN RESEARCH PIPELINE
        # =====================================================

        st.divider()

        st.header("🔬 Pan Ideate Africa Kaolin Research Pipeline")

        pipeline = [

            "Stage 1 — Deposit identification",

            "Stage 2 — Geological and mineral characterization",

            "Stage 3 — Laboratory characterization",

            "Stage 4 — Beneficiation research",

            "Stage 5 — Particle-size optimization",

            "Stage 6 — Dispersion testing",

            "Stage 7 — Particle-film testing",

            "Stage 8 — Greenhouse experiments",

            "Stage 9 — Small field trials",

            "Stage 10 — Crop performance analysis",

            "Stage 11 — Product formulation",

            "Stage 12 — Cost analysis",

            "Stage 13 — Packaging and quality control",

            "Stage 14 — Pilot production",

            "Stage 15 — Commercialization"
        ]

        for stage in pipeline:
            st.write(stage)

        st.divider()

        st.header("🌍 The Pan Ideate Africa Opportunity")

        st.markdown("""
        Kaolin gives us an excellent example of how the Knowledge Hub can
        connect several disciplines:

        **🪨 Minerals**

        ↓

        **🧪 Chemistry**

        ↓

        **🏭 Mineral Processing**

        ↓

        **🌱 Agriculture**

        ↓

        **🔬 Research**

        ↓

        **🧴 Product Development**

        ↓

        **💼 Business**

        ↓

        **👨🏾‍🎓 Youth Skills**

        ↓

        **🌍 African Industry**
        """)

        st.success(
            "🚀 Pan Ideate Africa: Learn → Practice → Produce → Earn → Innovate"
        )

    # =========================================================
    # OTHER AGRICULTURE PROJECTS
    # =========================================================

    else:

        st.header(selected)

        project_descriptions = {

            "🔥 Biochar Technologies":
                """
                Biochar converts biomass into a carbon-rich material that can
                be investigated for soil improvement, moisture management,
                nutrient management and other agricultural applications.
                """,

            "💧 Water Retention":
                """
                This project will investigate practical ways of improving
                soil moisture storage using biochar, clay minerals, soil
                management and water-management technologies.
                """,

            "🧱 Bentonite Solutions":
                """
                Bentonite can be investigated for water-retention applications,
                soil improvement and selected agricultural and industrial uses.
                """,

            "🌱 Soil Improvement":
                """
                This project connects soil chemistry, organic matter, minerals,
                biochar, clay materials and sustainable nutrient management.
                """,

            "🐄 Livestock Innovation":
                """
                This area will investigate mineral-based and circular
                agricultural technologies for livestock systems.
                """,

            "🚜 Agribusiness":
                """
                This area converts agricultural science into practical
                youth enterprise and value-chain opportunities.
                """,

            "🌾 Crop Production":
                """
                This project will connect crop science with modern technologies,
                local materials, water management and climate-smart production.
                """,

            "🎓 Agricultural Education":
                """
                This area will develop practical agricultural learning modules,
                demonstrations, school projects and youth training.
                """
        }

        st.info(project_descriptions.get(
            selected,
            "This project area is part of the Pan Ideate Africa Agriculture Innovation Centre."
        ))

        st.divider()

        st.subheader("🚀 Development Roadmap")

        st.write("1️⃣ Establish the science")

        st.write("2️⃣ Establish the chemistry")

        st.write("3️⃣ Design practical experiments")

        st.write("4️⃣ Develop products")

        st.write("5️⃣ Test performance")

        st.write("6️⃣ Calculate production costs")

        st.write("7️⃣ Develop business models")

        st.write("8️⃣ Train youth")

    
        # ============================================================
    # BENTONITE SOLUTIONS
    # ============================================================

        # ============================================================
   
        # FINAL AGRICULTURE MODEL
        # =========================================================

        st.divider()

        st.header("🇺🇬 Pan Ideate Africa Agricultural Model")

        st.markdown("""
        ### Learn → Practice → Produce → Earn → Innovate

        We will develop each agricultural project from its **science and
        chemistry**, through **practical demonstrations and research**, into
        **validated products and viable Ugandan/East African businesses**.
        """)

        st.info(
            "🌍 Pan Ideate Africa is building agricultural knowledge around "
            "local resources, practical science, innovation and youth entrepreneurship."
        )
        
            # ============================================================
      