import streamlit as st

def quality_control():

    st.header("🧪 Quality Control")

    st.markdown("""
Quality control ensures that iron oxide pigments meet the required
standards for colour, purity, particle size and performance.

Careful testing helps produce pigments that are consistent,
safe and suitable for industrial applications.
""")

    tests = {

        "🎨 Colour Evaluation":[
            "Colour consistency",
            "Colour intensity",
            "Visual appearance"
        ],

        "⚖️ Particle Size":[
            "Fine grinding",
            "Uniform particle distribution",
            "Sieving analysis"
        ],

        "🧪 Chemical Analysis":[
            "Iron oxide content",
            "Impurity determination",
            "Moisture content"
        ],

        "🏭 Performance Testing":[
            "Opacity",
            "Tinting strength",
            "Weather resistance",
            "Heat resistance"
        ],

        "📋 Quality Documentation":[
            "Sample identification",
            "Laboratory records",
            "Test reports",
            "Batch records"
        ]
    }

    for title, items in tests.items():

        with st.expander(title):

            for item in items:
                st.write(f"• {item}")

    st.success("✅ Good quality control produces reliable and high-quality pigments.")