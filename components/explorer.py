import streamlit as st


def show_explorer():

    st.divider()
    st.header("📚 Explore Knowledge")

    col1, col2 = st.columns(2)

    with col1:

        with st.expander("🧪 Minerals & Chemistry", expanded=True):

            if st.button("Iron Oxide Pigments"):
                st.session_state.quick = "Tell me about Iron Oxide Pigments."

            if st.button("Kaolin"):
                st.session_state.quick = "Explain Kaolin."

            if st.button("Bentonite"):
                st.session_state.quick = "Explain Bentonite."

            if st.button("Silicon"):
                st.session_state.quick = "Explain Silicon."

            if st.button("Rock Salt"):
                st.session_state.quick = "Explain Rock Salt."

        with st.expander("🌱 Agriculture"):

            if st.button("Biochar"):
                st.session_state.quick = "Explain Biochar."

            if st.button("Water Retention"):
                st.session_state.quick = "Explain Water Retention."

            if st.button("Soil Fertility"):
                st.session_state.quick = "Explain Soil Fertility."

            if st.button("Organic Fertilizers"):
                st.session_state.quick = "Explain Organic Fertilizers."

            if st.button("Livestock Feed"):
                st.session_state.quick = "Explain Livestock Feed."

    with col2:

        with st.expander("🏭 Manufacturing"):

            if st.button("Paints"):
                st.session_state.quick = "Explain Paint Manufacturing."

            if st.button("Roofing Tiles"):
                st.session_state.quick = "Explain Roofing Tile Manufacturing."

            if st.button("Bricks"):
                st.session_state.quick = "Explain Brick Manufacturing."

            if st.button("Ceramics"):
                st.session_state.quick = "Explain Ceramics."

        with st.expander("💼 Business Development"):

            if st.button("Business Ideas"):
                st.session_state.quick = "Give me business ideas."

            if st.button("Business Plans"):
                st.session_state.quick = "Help me write a business plan."

            if st.button("Marketing"):
                st.session_state.quick = "Explain marketing."

            if st.button("Funding"):
                st.session_state.quick = "How can I get funding?"

        with st.expander("🤖 Artificial Intelligence"):

            st.write("Coming soon...")

        with st.expander("📖 Learning Centre"):

            st.write("Coming soon...")

        with st.expander("🌍 Uganda Minerals Database"):

            st.write("Coming soon...")