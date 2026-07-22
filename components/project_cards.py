import streamlit as st


def show_project_cards():

    st.header("⭐ Featured Projects")

    col1, col2 = st.columns(2)

    with col1:

        with st.container(border=True):
            st.subheader("🌱 Biochar")
            st.write(
                "Climate-smart agriculture through sustainable biochar production."
            )
            st.button("Learn More", key="biochar_button")
        with st.container(border=True):
            st.subheader("🟤 Bentonite")
            st.write(
                "Water retention, livestock feed binders and industrial applications."
            )
            st.button("Learn More", key="bentonite_button")
        with st.container(border=True):
            st.subheader("🧪 Iron Oxide Pigments")
            st.write(
                "Natural pigments for paints, construction and manufacturing."
            )
            st.button("Learn More", key="iron_oxide_button")
    with col2:

        with st.container(border=True):
            st.subheader("⚪ Kaolin & Silicon")
            st.write(
                "Advanced materials for ceramics, electronics and future technology."
            )
            st.button("Learn More", key="kaolin_button")
        with st.container(border=True):
            st.subheader("🧂 Rock Salt")
            st.write(
                "Industrial minerals for chemical, agricultural and food industries."
            )
            st.button("Learn More", key="rock_salt_button")

        with st.container(border=True):
            st.subheader("🤖 AI for Innovation")
            st.write(
                "Artificial Intelligence supporting education, research and entrepreneurship."
            )

    st.divider()