import streamlit as st


def show():

    st.header("🤖 Pan Ideate Africa AI Business Assistant")

    st.info(
        "Your intelligent assistant for science, innovation, "
        "business and agriculture."
    )

    st.success("""
Welcome!

I can help you with:

🌱 Biochar Production

🏺 Kaolin Processing

🧪 Bentonite Applications

🎨 Iron Oxide Pigments

🌾 Agriculture

💼 Business Planning

📊 Cost Calculations

📈 Market Opportunities

🧬 Scientific Explanations

📚 Learning Support
""")

    st.markdown("---")

    st.subheader("⚡ Quick Questions")

    col1, col2 = st.columns(2)

    with col1:
        st.button("💼 Start a Business")
        st.button("🌱 Improve Agriculture")
        st.button("🧪 Learn Chemistry")

    with col2:
        st.button("📊 Calculate Costs")
        st.button("🏺 Explore Kaolin")
        st.button("🎨 Pigment Production")

    st.markdown("---")

    st.warning(
        "🚀 Future versions will include a live conversational AI "
        "assistant connected to the Pan Ideate Africa Knowledge Hub."
    )