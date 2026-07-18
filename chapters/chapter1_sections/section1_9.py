import streamlit as st


def show_section_1_9():

    st.header("1.9 Introduction to Mineral Exploration")

    st.markdown("---")

    st.markdown("""
### 🎯 Learning Objectives

By the end of this section learners should be able to:

- Define mineral exploration.
- Explain why mineral exploration is important.
- Describe the major stages of mineral exploration.
- Identify simple exploration methods used in Uganda.
- Understand how exploration supports mining, industry and national development.
""")

    st.markdown("---")

    st.subheader("Introduction")

    st.write("""
Mineral exploration is the scientific process of searching for valuable mineral
resources beneath or on the Earth's surface.

Before any mine is developed, geologists and exploration teams must first locate,
study and evaluate the mineral deposit.

Exploration reduces uncertainty and helps determine whether a mineral deposit can
be mined economically and responsibly.
""")

    st.markdown("---")

    st.subheader("Why Mineral Exploration is Important")

    st.success("""
Mineral exploration helps to:

• Discover new mineral deposits.

• Estimate the size and quality of mineral resources.

• Support industrial development.

• Create employment opportunities.

• Attract investment.

• Promote responsible use of natural resources.
""")

    st.markdown("---")

    st.subheader("Stages of Mineral Exploration")

    st.table({
        "Stage": [
            "Desktop Study",
            "Reconnaissance",
            "Detailed Survey",
            "Sampling",
            "Laboratory Analysis",
            "Resource Evaluation"
        ],
        "Purpose": [
            "Study maps and existing information",
            "Visit the area",
            "Collect detailed field information",
            "Collect rock, soil and stream samples",
            "Determine mineral composition",
            "Estimate economic potential"
        ]
    })

    st.markdown("---")

    st.subheader("Common Exploration Methods")

    st.write("""
Examples include:

🗺 Geological Mapping

🪨 Rock Sampling

🌱 Soil Sampling

💧 Stream Sediment Sampling

🛰 Remote Sensing

📡 Geophysical Surveys

🧪 Laboratory Analysis
""")

    st.markdown("---")

    st.subheader("Mineral Exploration in Uganda")

    st.info("""
Uganda possesses significant mineral potential including:

• Gold

• Iron Ore

• Limestone

• Kaolin

• Bentonite

• Copper

• Phosphate

• Rock Salt

Exploration continues to improve knowledge of these resources and identify new opportunities.
""")

    st.markdown("---")

    st.subheader("Connection to Pan Ideate Africa")

    st.success("""
The Pan Ideate Africa Knowledge Hub encourages responsible exploration through:

🔍 Scientific observation

🧪 Practical learning

📚 Mineral education

🌍 Environmental responsibility

💼 Value addition and entrepreneurship

The goal is to help learners transform knowledge into innovation and sustainable businesses.
""")

    st.markdown("---")

    st.subheader("Responsible Exploration")

    st.write("""
Responsible exploration includes:

✔ Respecting landowners and communities.

✔ Protecting the environment.

✔ Following national laws and regulations.

✔ Recording accurate field observations.

✔ Promoting safe working practices.
""")

    st.markdown("---")

    st.subheader("Summary")

    st.success("""
✔ Mineral exploration is the search for valuable mineral resources.

✔ Exploration follows a systematic scientific process.

✔ Good exploration reduces risk before mining begins.

✔ Uganda has excellent mineral exploration opportunities.

✔ Knowledge is the foundation of responsible resource development.
""")

    st.markdown("---")

    st.subheader("📝 Self-Assessment")

    questions = [
        "1. What is mineral exploration?",
        "2. Why is mineral exploration important?",
        "3. Name four exploration methods.",
        "4. Why are samples collected?",
        "5. Why should exploration be carried out responsibly?"
    ]

    for q in questions:
        st.checkbox(q)

    st.success("Excellent! You have completed Section 1.9.")