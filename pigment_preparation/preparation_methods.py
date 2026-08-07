import streamlit as st

def preparation_methods():

    st.header("🧪 Preparation Methods")

    st.markdown("""
Iron oxide pigments can be prepared from naturally occurring iron-rich
materials or by synthetic chemical processes.

Select a preparation method below to learn more.
""")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🌍 Natural",
        "⚗️ Synthetic",
        "🏭 Industrial",
        "🔬 Laboratory"
    ])

    with tab1:
        st.subheader("Natural Preparation")

        st.markdown("""
Typical steps include:

1. Site selection
2. Sampling
3. Crushing
4. Washing
5. Sedimentation
6. Drying
7. Grinding
8. Sieving
9. Packaging
""")

    with tab2:
        st.subheader("Synthetic Preparation")

        st.markdown("""
Synthetic pigments are manufactured using carefully controlled chemical
processes to obtain high purity, consistent colour and uniform particle size.
""")

    with tab3:
        st.subheader("Industrial Production")

        st.markdown("""
Industrial production uses specialized equipment for:

• Crushing

• Milling

• Classification

• Drying

• Calcination (where applicable)

• Packaging

• Quality control
""")

    with tab4:
        st.subheader("Laboratory Preparation")

        st.markdown("""
Laboratory preparation is used for:

• Research

• Product development

• Quality testing

• Student practicals

• Pilot production
""")