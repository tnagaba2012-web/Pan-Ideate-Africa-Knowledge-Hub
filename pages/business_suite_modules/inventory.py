import streamlit as st
if "inventory" not in st.session_state:
    st.session_state.inventory = []

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
    st.markdown("---")

st.header("➕ Add Product")

product = st.text_input("Product Name")

category = st.selectbox(
    "Category",
    [
        "Raw Material",
        "Finished Product",
        "Chemical",
        "Equipment"
    ]
)

quantity = st.number_input(
    "Quantity",
    min_value=0,
    value=0
)

price = st.number_input(
    "Unit Price (UGX)",
    min_value=0
)

supplier = st.text_input("Supplier")

if st.button("Save Product"):

    st.session_state.inventory.append(
        {
            "Product": product,
            "Category": category,
            "Quantity": quantity,
            "Price": price,
            "Supplier": supplier
        }
    )

    st.success("✅ Product saved successfully!")
    st.markdown("---")

st.header("📋 Inventory")

if st.session_state.inventory:

    st.table(st.session_state.inventory)

else:

    st.info("No products have been added yet.")st.markdown("---")

st.header("📋 Inventory")

if st.session_state.inventory:

    st.table(st.session_state.inventory)

else:

    st.info("No products have been added yet.")