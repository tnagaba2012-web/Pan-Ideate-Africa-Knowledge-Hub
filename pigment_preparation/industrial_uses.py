import streamlit as st

def industrial_uses():

    st.header("🏭 Industrial Uses of Iron Oxide Pigments")

    st.markdown("""
Iron oxide pigments are widely used in many industries because of their
excellent colour stability, durability and resistance to weathering.
""")

    uses = {
        "🏗️ Construction": [
            "Concrete blocks",
            "Roofing tiles",
            "Bricks",
            "Paving stones",
            "Floor tiles"
        ],

        "🎨 Paint Industry": [
            "Decorative paints",
            "Protective coatings",
            "Industrial paints",
            "Road marking paints"
        ],

        "🏺 Ceramics": [
            "Ceramic tiles",
            "Pottery",
            "Porcelain",
            "Decorative ceramics"
        ],

        "🧱 Building Materials": [
            "Cement products",
            "Wall panels",
            "Decorative stone",
            "Precast products"
        ],

        "🧴 Other Industries": [
            "Plastics",
            "Rubber",
            "Printing inks",
            "Cosmetics",
            "Art materials"
        ]
    }

    for title, items in uses.items():
        with st.expander(title):
            for item in items:
                st.write(f"• {item}")

    st.success("🌍 Iron oxide pigments are among the world's most widely used inorganic pigments.")