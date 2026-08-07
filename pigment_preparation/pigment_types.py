import streamlit as st

def pigment_types():

    st.header("🎨 Types of Iron Oxide Pigments")

    st.markdown("""
Iron oxide pigments are classified according to their colour, chemical
composition and method of production. The major pigment types are shown below.
""")

    with st.expander("🔴 Red Iron Oxide"):
        st.markdown("""
**Chemical Formula:** Fe₂O₃

**Main Mineral:** Hematite

**Colour:** Bright Red to Dark Red

**Common Uses:**
- Roofing tiles
- Bricks
- Concrete blocks
- Pavers
- Paints
- Decorative products
""")

    with st.expander("🟡 Yellow Iron Oxide"):
        st.markdown("""
**Chemical Formula:** FeO(OH)

**Main Mineral:** Goethite

**Colour:** Yellow to Golden Yellow

**Common Uses:**
- Decorative paints
- Plasters
- Concrete
- Ceramics
""")

    with st.expander("⚫ Black Iron Oxide"):
        st.markdown("""
**Chemical Formula:** Fe₃O₄

**Main Mineral:** Magnetite

**Colour:** Black

**Common Uses:**
- Industrial coatings
- Magnetic materials
- Construction products
- Ceramics
""")

    with st.expander("🟤 Brown Iron Oxide"):
        st.markdown("""
Brown pigments are produced naturally or by blending different iron oxide pigments.

**Common Uses:**
- Decorative concrete
- Clay products
- Exterior coatings
- Landscaping products
""")

    with st.expander("🟣 Purple Iron Oxide"):
        st.markdown("""
Purple iron oxide pigments are specialty pigments used in premium decorative finishes.

**Common Uses:**
- Premium paints
- Decorative coatings
- Artistic products
""")