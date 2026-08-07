import streamlit as st

def pigment_gallery():

    st.header("🖼️ Iron Oxide Pigment Gallery")

    st.markdown("""
Welcome to the Iron Oxide Pigment Gallery.

Explore the different natural and synthetic iron oxide pigments,
their colours, mineral sources and applications.
""")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔴 Red Iron Oxide")
        st.info("Mineral: Hematite (Fe₂O₃)")
        st.write("Colour: Deep Red")
        st.write("Uses:")
        st.write("• Roofing tiles")
        st.write("• Bricks")
        st.write("• Paints")
        st.write("• Concrete products")
        st.image("https://upload.wikimedia.org/wikipedia/commons/6/6f/Hematite.jpg", width=250)

    with col2:
        st.subheader("🟡 Yellow Iron Oxide")
        st.info("Mineral: Goethite (FeO(OH))")
        st.write("Colour: Golden Yellow")
        st.write("Uses:")
        st.write("• Decorative paints")
        st.write("• Ceramics")
        st.write("• Plasters")
        st.write("• Concrete")
        st.image("https://upload.wikimedia.org/wikipedia/commons/7/7b/Goethite.jpg", width=250)

    st.divider()

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("⚫ Black Iron Oxide")
        st.info("Mineral: Magnetite (Fe₃O₄)")
        st.write("Colour: Black")
        st.write("Industrial pigment")
        st.image("https://upload.wikimedia.org/wikipedia/commons/e/e5/Magnetite.jpg", width=250)

    with col4:
        st.subheader("🟤 Brown Iron Oxide")
        st.info("Mineral: Limonite")
        st.write("Colour: Brown")
        st.write("Natural earth pigment")
        st.image("https://upload.wikimedia.org/wikipedia/commons/0/03/LimoniteUSGOV.jpg", width=250)

    st.success("🎨 More pigment varieties and high-resolution photographs will be added in future updates.")