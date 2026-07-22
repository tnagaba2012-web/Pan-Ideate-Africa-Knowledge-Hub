import streamlit as st


def show():

    st.header("🛒 Pan Ideate Africa Marketplace")

    st.info(
        "Buy, sell and promote innovations, products and services "
        "developed through the Pan Ideate Africa Knowledge Hub."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.success("🌱 Agriculture")
        st.write("""
• Biochar

• Organic Fertilizers

• Water Retention Products

• Livestock Solutions
""")

        st.success("🧪 Science & Minerals")
        st.write("""
• Kaolin

• Bentonite

• Iron Oxide Pigments

• Silica Products
""")

    with col2:
        st.success("🏭 Manufacturing")
        st.write("""
• Paints

• Ceramics

• Bricks

• Construction Materials
""")

        st.success("📚 Knowledge Products")
        st.write("""
• Training Manuals

• Professional Courses

• Business Templates

• Research Publications
""")

    st.markdown("---")

    st.subheader("🌍 Vision")

    st.success(
        "Our long-term goal is to create Africa's leading marketplace "
        "for science, innovation, agriculture and entrepreneurship."
    )