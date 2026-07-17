import streamlit as st

def show_section_1_3():
    st.success("✅ SECTION 1.3 FUNCTION IS RUNNING")
    st.header("1.3 Minerals, Rocks and Ores")

    st.markdown("---")

    st.markdown("""
### 🎯 Learning Objectives

By the end of this section learners should be able to:

- Define a mineral.
- Define a rock.
- Define an ore.
- Distinguish between minerals, rocks and ores.
- Explain why understanding these materials is important for mining and industry.
""")

    st.markdown("---")

    st.subheader("Introduction")

    st.write("""
Everything used in modern civilization begins with the Earth's natural materials.
Buildings, roads, electronics, fertilizers, vehicles and machines all depend on minerals
that are extracted from rocks. Some rocks contain valuable minerals in concentrations high
enough to be mined economically. These are called ores.

Understanding the relationship between minerals, rocks and ores is the foundation of
geology, mining and mineral processing.
""")

    st.markdown("---")

    st.subheader("🧪 What is a Mineral?")

    st.info("""
A mineral is a naturally occurring inorganic solid with a definite chemical composition
and an orderly crystalline structure.

Examples include:

• Quartz (SiO₂)

• Calcite (CaCO₃)

• Feldspar

• Mica

• Gypsum
""")

    st.markdown("---")

    st.subheader("🪨 What is a Rock?")

    st.success("""
A rock is a natural solid made of one or more minerals.

Examples:

• Granite

• Basalt

• Sandstone

• Limestone

• Marble
""")

    st.markdown("---")

    st.subheader("⛏ What is an Ore?")

    st.warning("""
An ore is a rock that contains valuable minerals in sufficient quantities
to be mined profitably.

Examples:

• Iron Ore

• Copper Ore

• Gold Ore

• Bauxite

• Tin Ore
""")

    st.markdown("---")

    st.subheader("📊 Comparison")

    st.table({
        "Mineral":[
            "Naturally occurring substance",
            "Specific chemical composition",
            "Building block of rocks"
        ],
        "Rock":[
            "Mixture of minerals",
            "Variable composition",
            "Forms mountains and landscapes"
        ],
        "Ore":[
            "Contains valuable minerals",
            "Economically mined",
            "Source of metals and industrial minerals"
        ]
    })

    st.markdown("---")

    st.subheader("🇺🇬 Uganda Examples")

    st.write("""
Uganda possesses many important rocks, minerals and ores including:

• Gold

• Iron Ore

• Copper

• Cobalt

• Limestone

• Marble

• Kaolin

• Vermiculite

• Phosphate

• Silica Sand

• Rare Earth Elements

These resources have enormous potential to support industrialization,
employment and value addition.
""")

    st.markdown("---")

    st.subheader("💡 Pan Ideate Insight")

    st.info("""
Knowledge of minerals allows communities to transform natural resources
into industries that create jobs, improve agriculture and increase national wealth.
""")

    st.success("✅ Section 1.3 Approved - Version 1.0")