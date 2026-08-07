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
def get_info():
    return """
Iron oxide pigments are available in several major types.

Main pigment types:

• Red Iron Oxide (Fe₂O₃)
  - Most widely used
  - Used in bricks, paints, concrete and ceramics

• Yellow Iron Oxide (FeOOH)
  - Bright yellow colour
  - Used in decorative coatings and plastics

• Black Iron Oxide (Fe₃O₄)
  - Deep black pigment
  - Used in inks, coatings and magnetic materials

• Brown Iron Oxide
  - Blend of red, yellow and black oxides
  - Used in tiles and construction materials

Each pigment type has different colour properties, particle size, stability and industrial applications.
"""