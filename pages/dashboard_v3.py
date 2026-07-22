import streamlit as st


def show():

    # ==================================================
    # PAN IDEATE AFRICA DASHBOARD VERSION 3.0
    # ==================================================

    st.set_page_config(
        page_title="Pan Ideate Africa Dashboard",
        page_icon="🌍",
        layout="wide"
    )

    st.balloons()

    st.title("🌍 Pan Ideate Africa Knowledge Hub")

    st.caption(
        "Learn → Innovate → Produce → Manage → Sell → Prosper"
    )

    st.success("""
## 👋 Welcome!

Welcome to the Pan Ideate Africa Knowledge Hub.

Our mission is to empower Africa through:

📚 Knowledge

🧪 Science

🌱 Agriculture

💼 Entrepreneurship

🤖 Artificial Intelligence

🌍 Innovation

Together we transform ideas into products, businesses and opportunities.
""")

    st.markdown("---")

    st.header("🎯 Our Vision")

    st.info("""
Pan Ideate Africa is building a platform where learning does not end in the classroom.

Here you will discover:

• Scientific knowledge

• Practical skills

• Product development

• Business opportunities

• Innovation projects

• AI-powered learning

Everything is designed to help learners become innovators and entrepreneurs.
""")
        # ==================================================
    # PLATFORM STATISTICS
    # ==================================================

    st.markdown("---")

    st.header("📊 Platform Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="👥 Members",
            value="1,245",
            delta="+42"
        )

    with col2:
        st.metric(
            label="📚 Courses",
            value="86",
            delta="+4"
        )

    with col3:
        st.metric(
            label="🧪 Projects",
            value="18",
            delta="+2"
        )

    with col4:
        st.metric(
            label="🌍 Countries",
            value="12",
            delta="+1"
        )

    st.markdown("---")

    # ==================================================
    # QUICK ACCESS
    # ==================================================

    st.header("⚡ Quick Access")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.button("📚 Knowledge Hub")

        st.button("🧪 Science")

        st.button("🌱 Agriculture")

    with c2:

        st.button("💼 Business Suite")

        st.button("🤖 AI Assistant")

        st.button("🛒 Marketplace")

    with c3:

        st.button("👥 Community")

        st.button("📊 Reports")

        st.button("⚙️ Settings")
            # ==================================================
    # CONTINUE LEARNING
    # ==================================================

    st.markdown("---")

    st.header("📚 Continue Your Learning")

    col1, col2 = st.columns(2)

    with col1:

        st.success("📖 Knowledge Hub")

        st.write("""
Continue exploring:

• Science Handbook

• Chemistry

• Mineral Processing

• Innovation Guides
""")

        st.button("📚 Continue Learning")

    with col2:

        st.success("🎓 Your Progress")

        st.progress(0.35)

        st.write("You have completed **35%** of your learning journey.")

        st.button("🏆 View Achievements")

    st.markdown("---")

    # ==================================================
    # FEATURED PROJECTS
    # ==================================================

    st.header("🚀 Featured Projects")

    p1, p2, p3 = st.columns(3)

    with p1:

        st.info("🌱 Biochar")

        st.write("""
Climate-smart agriculture

• Soil improvement

• Carbon storage

• Better crop yields
""")

    with p2:

        st.info("🏺 Kaolin")

        st.write("""
Industrial minerals

• Ceramics

• Paints

• Cosmetics
""")

    with p3:

        st.info("🎨 Iron Oxide Pigments")

        st.write("""
Natural colour solutions

• Paints

• Bricks

• Construction
""")

    st.markdown("---")

    # ==================================================
    # INNOVATION SPOTLIGHT
    # ==================================================

    st.header("⭐ Innovation Spotlight")

    st.success("""
🇺🇬 Uganda has enormous potential in science, agriculture and mineral value addition.

Pan Ideate Africa connects knowledge with innovation so that learners can create products, businesses and employment opportunities.

Today's Focus:

🧪 Science

🌱 Agriculture

💼 Entrepreneurship

🤖 Artificial Intelligence
""")
        # ==================================================
    # AI ASSISTANT
    # ==================================================

    st.markdown("---")

    st.header("🤖 Pan Ideate Africa AI Assistant")

    st.info("""
Your intelligent partner for learning, innovation and entrepreneurship.

Choose what you would like to explore today.
""")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.button("🧪 Science AI")

    with col2:
        st.button("🌱 Agriculture AI")

    with col3:
        st.button("💼 Business AI")

    st.markdown("---")

    # ==================================================
    # LATEST NEWS
    # ==================================================

    st.header("📰 Latest Updates")

    st.success("""
🚀 Dashboard Version 3.0 Development has officially begun.

📚 Knowledge Hub continues to expand.

💼 Business Suite Version 2.2 modules completed.

🌍 More exciting features are coming soon.
""")

    st.markdown("---")

    # ==================================================
    # DAILY INSPIRATION
    # ==================================================

    st.header("💡 Today's Inspiration")

    st.warning("""
"Knowledge becomes powerful when it is transformed into innovation.

Innovation becomes meaningful when it improves people's lives."

— Pan Ideate Africa
""")

    st.markdown("---")

    # ==================================================
    # OUR VISION
    # ==================================================

    st.header("🌍 Our Vision")

    st.success("""
Pan Ideate Africa exists to empower Africa through:

📚 Education

🧪 Science

🌱 Agriculture

💼 Entrepreneurship

🤖 Artificial Intelligence

🏭 Manufacturing

🌍 Innovation

Together we are creating knowledge that becomes products...

Products that become businesses...

Businesses that create jobs...

And jobs that transform communities across Africa.

Learn → Innovate → Produce → Manage → Sell → Prosper
""")

    st.balloons()