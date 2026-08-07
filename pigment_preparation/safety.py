import streamlit as st

def safety():

    st.header("🦺 Laboratory Safety")

    st.warning("""
Always observe laboratory safety during pigment preparation.
""")

    safety_rules = [
        "Wear gloves.",
        "Wear safety glasses.",
        "Wear a dust mask or respirator.",
        "Wear a laboratory coat.",
        "Use good ventilation.",
        "Keep the laboratory clean.",
        "Label all samples correctly.",
        "Dispose of waste responsibly."
    ]

    for rule in safety_rules:
        st.write(f"✅ {rule}")

    st.success("Safety is everyone's responsibility.")