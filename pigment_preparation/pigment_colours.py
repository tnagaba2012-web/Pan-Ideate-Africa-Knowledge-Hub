import streamlit as st

def pigment_colours():

    st.header("🌈 Iron Oxide Pigment Colours")

    st.markdown("""
Iron oxide pigments are available in several beautiful natural colours.
Each colour has its own mineral source, chemical composition and industrial
applications.
""")

    colours = [
        ("🔴 Red", "Fe₂O₃ (Hematite)", "Roofing tiles, bricks, pavers, concrete, paints"),
        ("🟡 Yellow", "FeO(OH) (Goethite)", "Decorative paints, plasters, ceramics"),
        ("⚫ Black", "Fe₃O₄ (Magnetite)", "Industrial coatings, ceramics, magnetic products"),
        ("🟤 Brown", "Mixed iron oxides", "Exterior coatings, decorative concrete"),
        ("🟣 Purple", "Modified iron oxide", "Premium decorative coatings"),
        ("🟠 Orange", "Heat-treated iron oxides", "Architectural finishes"),
    ]

    for colour, formula, uses in colours:
        st.markdown(f"""
### {colour}

**Chemical Composition:** {formula}

**Common Uses:** {uses}

---
""")

    st.info("🎨 Different colours can also be produced by blending pigments or controlling processing conditions.")