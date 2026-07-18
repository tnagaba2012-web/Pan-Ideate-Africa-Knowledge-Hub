import streamlit as st


def show_section_1_6():

    st.header("1.6 Mineral Classification")

    st.markdown("---")

    st.markdown("""
### 🎯 Learning Objectives

By the end of this section learners should be able to:

- Explain what mineral classification means.
- Identify the major groups of minerals.
- Distinguish between silicate and non-silicate minerals.
- Understand why mineral classification is important in geology, mining and industry.
- Relate Uganda's mineral resources to their mineral groups.
""")

    st.markdown("---")

    st.subheader("Introduction")

    st.write("""
Minerals are not studied as one large group. Scientists classify them into groups according to
their chemical composition and crystal structure.

Mineral classification makes it easier to identify minerals, understand how they formed,
predict their properties and determine their industrial uses.

Although thousands of different minerals exist worldwide, most belong to only a few major
mineral groups.
""")

    st.markdown("---")

    st.subheader("Why Minerals Are Classified")

    st.info("""
Minerals are classified because minerals with similar chemical compositions usually have
similar physical properties, methods of formation and industrial applications.
""")

    st.markdown("""
Classification helps geologists to:

- Identify unknown minerals.
- Locate mineral deposits.
- Understand Earth's history.
- Select minerals for industry.
- Teach mineral science more effectively.
""")

    st.markdown("---")

    st.subheader("Major Mineral Groups")

    st.table({
        "Mineral Group": [
            "Silicates",
            "Carbonates",
            "Oxides",
            "Sulfides",
            "Sulfates",
            "Halides",
            "Phosphates",
            "Native Elements"
        ],
        "Main Element(s)": [
            "Silicon + Oxygen",
            "Carbon + Oxygen",
            "Oxygen + Metals",
            "Sulfur + Metals",
            "Sulfur + Oxygen",
            "Halogen Elements",
            "Phosphorus",
            "Single Element"
        ],
        "Example": [
            "Quartz, Feldspar",
            "Calcite",
            "Hematite",
            "Pyrite",
            "Gypsum",
            "Halite",
            "Apatite",
            "Gold, Copper"
        ]
    })

    st.markdown("---")

    st.subheader("Silicate Minerals")

    st.success("""
Silicate minerals are the largest mineral family on Earth.

They make up about 90% of the Earth's crust and contain silicon (Si) and oxygen (O).
""")

    st.write("""
Examples include:

• Quartz

• Feldspar

• Mica

• Olivine

• Pyroxene
""")

    st.markdown("---")

    st.subheader("Non-Silicate Minerals")

    st.write("""
The remaining mineral groups are called non-silicate minerals.

These include:

• Carbonates

• Oxides

• Sulfides

• Sulfates

• Halides

• Phosphates

• Native elements
""")

    st.markdown("---")

    st.subheader("Uganda Examples")

    st.success("""
Examples found in Uganda include:

🟤 Iron oxides (Hematite)

⚪ Limestone (Calcite)

🧂 Rock Salt (Halite)

⚪ Gypsum

🟢 Copper minerals

🟣 Gold (Native Element)

⚪ Quartz
""")

    st.markdown("---")

    st.subheader("Importance to Pan Ideate Africa Projects")

    st.info("""
Understanding mineral classification helps learners understand why:

• Iron oxides are used to produce natural pigments.

• Quartz provides silica used in glass and future silicon technologies.

• Limestone improves agriculture.

• Rock salt supports chemical industries.

• Clay minerals such as kaolin and bentonite have different industrial applications.
""")

    st.markdown("---")

    st.subheader("Summary")

    st.success("""
✔ Minerals are classified according to chemistry and crystal structure.

✔ Silicates are the largest mineral group.

✔ Non-silicates include carbonates, oxides, sulfides, sulfates, halides, phosphates and native elements.

✔ Mineral classification is essential in geology, mining, manufacturing and environmental science.

✔ Uganda possesses important minerals belonging to many of these groups.
""")

    st.markdown("---")

    st.subheader("📝 Self-Assessment")

    questions = [
        "1. What is mineral classification?",
        "2. Which mineral group is the largest on Earth?",
        "3. What elements make up silicate minerals?",
        "4. Name three non-silicate mineral groups.",
        "5. Why is mineral classification important in mining?"
    ]

    for q in questions:
        st.checkbox(q)

    st.success("Excellent! You have completed Section 1.6.")