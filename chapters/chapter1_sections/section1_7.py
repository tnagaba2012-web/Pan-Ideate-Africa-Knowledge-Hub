import streamlit as st


def show_section_1_7():

    st.header("1.7 How Minerals Form")

    st.markdown("---")

    st.markdown("""
### 🎯 Learning Objectives

By the end of this section learners should be able to:

- Explain how minerals form naturally.
- Describe the major processes of mineral formation.
- Understand the relationship between rocks and minerals.
- Identify examples of minerals formed by different geological processes.
- Relate mineral formation to Uganda's mineral resources.
""")

    st.markdown("---")

    st.subheader("Introduction")

    st.write("""
Minerals are not manufactured by people. They form naturally over thousands or even millions of
years through geological processes occurring inside and on the surface of the Earth.

Temperature, pressure, water and chemical reactions all play important roles in mineral formation.
""")

    st.markdown("---")

    st.subheader("Major Ways Minerals Form")

    st.success("""
Scientists recognize several major processes through which minerals are formed.
""")

    st.markdown("""
### 1️⃣ Crystallization from Magma

When molten rock (magma or lava) cools, minerals begin to crystallize.

Examples:

• Quartz

• Feldspar

• Mica

• Olivine
""")

    st.markdown("---")

    st.markdown("""
### 2️⃣ Precipitation from Water

Minerals may form when water containing dissolved substances evaporates or cools.

Examples:

• Rock Salt (Halite)

• Gypsum

• Calcite
""")

    st.markdown("---")

    st.markdown("""
### 3️⃣ Metamorphism

Heat and pressure acting deep underground change existing minerals into new minerals.

Examples:

• Garnet

• Graphite

• Talc
""")

    st.markdown("---")

    st.markdown("""
### 4️⃣ Hydrothermal Activity

Hot underground water carries dissolved minerals through cracks in rocks.

As the water cools, valuable minerals are deposited.

Examples:

• Gold

• Copper

• Quartz veins
""")

    st.markdown("---")

    st.subheader("Factors Affecting Mineral Formation")

    st.table({
        "Factor": [
            "Temperature",
            "Pressure",
            "Water",
            "Chemical Composition",
            "Time"
        ],
        "Importance": [
            "Controls crystal growth",
            "Forms new minerals",
            "Carries dissolved minerals",
            "Determines mineral type",
            "Allows crystal development"
        ]
    })

    st.markdown("---")

    st.subheader("Examples in Uganda")

    st.info("""
Examples of minerals formed through these processes include:

🟤 Iron ores

⚪ Limestone

⚪ Quartz

🟢 Copper minerals

🟣 Gold

⚪ Kaolin

🟢 Bentonite
""")

    st.markdown("---")

    st.subheader("Connection to Pan Ideate Africa Projects")

    st.success("""
Understanding how minerals form helps us understand:

• Why kaolin occurs in certain regions.

• How bentonite deposits developed.

• Why silica-rich rocks produce quartz.

• Where iron oxide pigments can be found.

• How geological processes influence agriculture and industry.
""")

    st.markdown("---")

    st.subheader("Summary")

    st.success("""
✔ Minerals form naturally.

✔ Four major formation processes are:
- Crystallization from magma
- Precipitation from water
- Metamorphism
- Hydrothermal activity

✔ Temperature, pressure, water and chemistry all influence mineral formation.

✔ Understanding mineral formation helps explorers discover new mineral deposits.
""")

    st.markdown("---")

    st.subheader("📝 Self-Assessment")

    questions = [
        "1. Name four ways minerals form.",
        "2. Which minerals form from cooling magma?",
        "3. What is hydrothermal activity?",
        "4. Why is water important in mineral formation?",
        "5. Why is understanding mineral formation important in exploration?"
    ]

    for q in questions:
        st.checkbox(q)

    st.success("Excellent! You have completed Section 1.7.")