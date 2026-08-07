import streamlit as st

def raw_materials():

    st.header("🪨 Raw Materials for Iron Oxide Pigment Production")

    st.markdown("""
The quality of an iron oxide pigment begins with the quality of its raw material.
Careful selection and evaluation of raw materials are essential for producing
high-quality pigments.
""")

    materials = {
        "🔴 Iron-rich Soils": [
            "Common in tropical regions",
            "Used for natural pigment production",
            "Require laboratory evaluation"
        ],

        "🟤 Lateritic Soils": [
            "Rich in iron oxides",
            "Abundant in Uganda",
            "Suitable for pigment investigations"
        ],

        "⚫ Iron Ore": [
            "Hematite",
            "Magnetite",
            "Goethite",
            "Limonite"
        ],

        "🪨 Weathered Rocks": [
            "Sandstone",
            "Basalt",
            "Granite",
            "Shale"
        ],

        "🧱 Clay Deposits": [
            "Red clay",
            "Yellow clay",
            "Brown clay"
        ]
    }

    for title, items in materials.items():
        with st.expander(title):
            for item in items:
                st.write(f"• {item}")

    st.success("💡 Tip: Every raw material should be tested before it is used for pigment production.")