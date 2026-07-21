import streamlit as st


def show_business_suite():

    # --------------------------------------------------
    # PAGE CONFIGURATION
    # --------------------------------------------------

    st.balloons()

    st.title("💼 Pan Ideate Africa Business Suite")

    st.caption("Learn → Innovate → Produce → Manage → Sell → Prosper")

    st.success("""
🎉 Welcome to the Pan Ideate Africa Business Suite!

This is where science meets entrepreneurship.

Whether you produce:

🌱 Biochar

🏺 Kaolin

🟤 Iron Oxide Pigments

🧪 Bentonite Products

🌾 Agricultural Products

or any other innovation,

this platform helps transform knowledge into successful businesses.
""")

    st.markdown("---")

    # --------------------------------------------------
    # BUSINESS DASHBOARD
    # --------------------------------------------------

    st.header("📊 Business Dashboard")

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
            label="💼 Projects",
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

    # --------------------------------------------------
    # QUICK ACTIONS
    # --------------------------------------------------

    st.header("🚀 Quick Actions")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.button("🛒 Marketplace")

        st.button("📦 Inventory")

        st.button("💰 Sales")

    with c2:

        st.button("👥 Customers")

        st.button("🧾 Invoices")

        st.button("📊 Reports")

    with c3:

        st.button("🤖 AI Assistant")

        st.button("🎓 Learning Centre")

        st.button("⚙️ Settings")

    st.markdown("---")

    # --------------------------------------------------
    # OUR MISSION
    # --------------------------------------------------

    st.header("🌍 Our Mission")

    st.info("""
Pan Ideate Africa believes learning should not stop in the classroom.

Knowledge should become:

✅ Innovation

✅ Products

✅ Businesses

✅ Employment

✅ Prosperity

Our mission is to empower Africans with practical scientific knowledge that creates sustainable businesses and improves lives.
""")
        # --------------------------------------------------
    # BUSINESS MODULES
    # --------------------------------------------------

    st.header("💼 Business Modules")

    left, right = st.columns(2)

    with left:

        st.success("🛒 Marketplace")
        st.write("Sell products across Uganda and Africa.")

        st.success("📦 Inventory Management")
        st.write("Monitor stock, production and low-stock alerts.")

        st.success("💰 Sales Management")
        st.write("Track daily, weekly and monthly sales.")

        st.success("👥 Customer Management")
        st.write("Store customer information and purchase history.")

        st.success("🧾 Invoice & Receipt Generator")
        st.write("Create quotations, invoices and receipts.")

    with right:

        st.success("👨‍💼 Employee Management")
        st.write("Manage staff records and attendance.")

        st.success("💸 Expense Management")
        st.write("Track business expenses and profitability.")

        st.success("📊 Reports & Analytics")
        st.write("Generate professional business reports.")

        st.success("🤖 AI Business Assistant")
        st.write("Receive intelligent business guidance.")

        st.success("🌍 African Marketplace")
        st.write("Connect buyers and sellers across Africa.")

    st.markdown("---")

    # --------------------------------------------------
    # SUBSCRIPTION CENTRE
    # --------------------------------------------------

    st.header("💳 Membership & Subscription Plans")

    free, student, pro, enterprise = st.columns(4)

    with free:
        st.success("🟢 FREE")
        st.write("""
✔ Basic Handbook

✔ Community Access

✔ Basic AI

✔ News Updates
""")

    with student:
        st.info("🔵 STUDENT")
        st.write("""
✔ Everything in FREE

✔ Full Courses

✔ Quizzes

✔ Certificates
""")

    with pro:
        st.warning("🟠 PROFESSIONAL")
        st.write("""
✔ Everything in STUDENT

✔ Business Suite

✔ Production Guides

✔ Premium Downloads
""")

    with enterprise:
        st.error("👑 ENTERPRISE")
        st.write("""
✔ Everything Included

✔ AI Business Tools

✔ Marketplace

✔ Team Accounts

✔ Analytics

✔ Priority Support
""")

    st.markdown("---")

    # --------------------------------------------------
    # PREMIUM FEATURES
    # --------------------------------------------------

    st.header("🔒 Premium Features")

    st.info("""
Premium Members will unlock:

⭐ Advanced Production Manuals

⭐ Business Templates

⭐ Equipment Guides

⭐ Market Intelligence

⭐ AI Business Planning

⭐ Downloadable Professional PDFs

⭐ Premium Video Lessons

⭐ Investor Resources
""")
        # --------------------------------------------------
    # AFRICAN INNOVATION SPOTLIGHT
    # --------------------------------------------------

    st.markdown("---")

    st.header("🌍 African Innovation Spotlight")

    st.success("""
## 🇺🇬 Opportunity of the Week

### 🏺 KAOLIN

Transform Uganda's natural kaolin into:

🏺 Ceramic products

🎨 Paint fillers

📄 Paper coating materials

💄 Cosmetic products

🏗️ Construction materials

💼 Every natural resource is an opportunity to create value through science and innovation.
""")

    # --------------------------------------------------
    # PAN IDEATE AFRICA JOURNEY
    # --------------------------------------------------

    st.markdown("---")

    st.header("🏆 Your Pan Ideate Africa Journey")

    st.info("""
🌱 Curious Learner

⬇

🔬 Science Explorer

⬇

🧪 Practical Scientist

⬇

🏭 Product Developer

⬇

💼 Entrepreneur

⬇

🌍 African Innovator

⬇

👑 Pan Ideate Africa Ambassador
""")

    # --------------------------------------------------
    # AI ASSISTANT
    # --------------------------------------------------

    st.markdown("---")

    st.header("🤖 Meet Your AI Business Assistant")

    st.success("""
Hello!

What would you like to build today?

🌱 Biochar

🏺 Kaolin

🧪 Bentonite

🎨 Iron Oxide Pigments

🌾 Agricultural Products

💼 Business Plans

📊 Cost Calculations

📈 Market Opportunities

Your AI Assistant will continue to grow with the Pan Ideate Africa platform.
""")

    # --------------------------------------------------
    # FUTURE FEATURES
    # --------------------------------------------------

    st.markdown("---")

    st.header("🚀 Coming Soon")

    st.warning("""
The Business Suite will continue expanding with:

🗺️ Uganda Mineral Atlas

🌍 African Marketplace

📱 Mobile App

🎓 Professional Certification

🤝 Investor Portal

💳 Online Subscriptions

🧠 Advanced AI Assistant

📊 Live Business Analytics
""")

    # --------------------------------------------------
    # FOOTER
    # --------------------------------------------------

    st.markdown("---")

    st.success("""
## 🌍 Pan Ideate Africa Vision

Learn → Innovate → Produce → Manage → Sell → Prosper

Together, we are building an African platform where science, innovation, entrepreneurship and technology work together to create opportunities for everyone.

Thank you for being part of the journey. 🚀
""")