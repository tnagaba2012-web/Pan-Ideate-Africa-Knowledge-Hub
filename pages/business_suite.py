import streamlit as st

def show_business_suite():

    # Celebration 🎉
    st.balloons()

    st.title("💼 Pan Ideate Africa Business Suite")

    st.success("""
🎉 Welcome to the Business Suite!

This is where science meets entrepreneurship.

Learn...
Build...
Manage...
Grow...

Whether you produce Biochar, Kaolin, Bentonite, Iron Oxide Pigments,
Agricultural Products or any other innovation,
this platform will help you transform knowledge into successful businesses.
""")

    st.markdown("---")

    st.header("🌍 Our Mission")

    st.info("""
Pan Ideate Africa believes that learning should not stop in the classroom.

Knowledge should become:

✅ Innovation

✅ Products

✅ Businesses

✅ Employment

✅ Prosperity

This Business Suite helps innovators manage every stage of their journey.
""")

    st.markdown("---")

    st.header("🚀 Business Modules")

    col1, col2 = st.columns(2)

    with col1:

        st.success("📦 Inventory Management")
        st.write("Track stock, purchases, production and low-stock alerts.")

        st.success("💰 Sales Management")
        st.write("Monitor daily, weekly, monthly and yearly sales.")

        st.success("👥 Customer Management")
        st.write("Store customer information and purchase history.")

        st.success("🧾 Invoice & Receipt Generator")
        st.write("Generate quotations, invoices and receipts.")

        st.success("💸 Expense Management")
        st.write("Track business expenses and improve profitability.")

    with col2:

        st.success("🛒 Marketplace")
        st.write("Advertise and sell products across Africa.")

        st.success("📊 Reports & Analytics")
        st.write("Generate business reports and performance summaries.")

        st.success("👨‍💼 Employee Management")
        st.write("Manage staff records and attendance.")

        st.success("🤖 AI Business Assistant")
        st.write("Receive intelligent business guidance.")

        st.success("⭐ Premium Business Tools")
        st.write("Advanced business features available through subscription.")

    st.markdown("---")

    st.header("💎 Subscription Plans")

    st.table({

        "Plan":[
            "🟢 Free Explorer",
            "🔵 Student",
            "🟠 Professional",
            "👑 Enterprise"
        ],

        "Ideal For":[
            "Everyone",
            "Schools & Universities",
            "Entrepreneurs",
            "Companies & Organisations"
        ],

        "Features":[
            "Basic Learning",
            "Full Courses + Quizzes",
            "Business Suite + Premium Guides",
            "Complete Platform + AI + Marketplace"
        ]

    })

    st.markdown("---")

    st.success("""
🌱 Learn → Innovate → Produce → Manage → Sell → Prosper

This is the vision of Pan Ideate Africa.
""")

    st.info("""
🇺🇬 Future Features

🗺 Uganda Mineral Atlas

🎓 Certificates

🌍 Community Network

📚 Research Library

📱 Mobile App

🤝 Investor Portal

🌐 African Marketplace

The journey has only just begun...
""")

    st.warning("""
🚧 Coming Soon

Each Business Suite module will be developed individually.

Today's page is the foundation for one of the most powerful features in the Pan Ideate Africa Knowledge Hub.
""")