import streamlit as st


def show():

    st.header("📦 Inventory Management")

    st.info(
        "Monitor raw materials, finished products and production "
        "resources for your projects."
    )

    st.subheader("🏭 Raw Materials")

    st.write("""
• Kaolin

• Bentonite

• Iron Oxide

• Biochar

• Sand

• Clay

• Chemicals

• Packaging Materials
""")

    st.markdown("---")

    st.subheader("📦 Stock Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📥 Raw Materials", "245")

    with col2:
        st.metric("🏭 Products", "126")

    with col3:
        st.metric("⚠️ Low Stock", "8")

    st.markdown("---")

    st.success("""
Future inventory features will include:

✅ Barcode support

✅ QR Code tracking

✅ Automatic stock updates

✅ Supplier management

✅ Warehouse monitoring

✅ Production planning
""")