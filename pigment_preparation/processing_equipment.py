import streamlit as st

def processing_equipment():

    st.header("⚙️ Processing Equipment")

    st.markdown("""
The preparation of high-quality iron oxide pigments requires suitable
equipment. The equipment used depends on the scale of production,
available resources, and the desired pigment quality.
""")

    equipment = {

        "⛏️ Sampling Equipment":[
            "Geological hammer",
            "Shovel",
            "Sample bags",
            "GPS",
            "Labels"
        ],

        "🪨 Crushing Equipment":[
            "Jaw crusher",
            "Hammer mill",
            "Roll crusher"
        ],

        "💧 Washing & Sedimentation":[
            "Washing tanks",
            "Sedimentation tanks",
            "Water pumps",
            "Mixing tanks"
        ],

        "🌬️ Drying Equipment":[
            "Drying trays",
            "Solar dryer",
            "Drying oven"
        ],

        "⚙️ Grinding Equipment":[
            "Ball mill",
            "Pulverizer",
            "Disc mill"
        ],

        "🧹 Classification Equipment":[
            "Sieves",
            "Vibrating screen",
            "Air classifier"
        ],

        "📦 Packaging Equipment":[
            "Weighing scale",
            "Packaging bags",
            "Sealing machine"
        ]
    }

    for section, items in equipment.items():

        with st.expander(section):

            for item in items:
                st.write(f"• {item}")

    st.success("🏭 Good equipment improves pigment quality, efficiency and consistency.")