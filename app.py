print("LOADING HOME.PY")
import streamlit as st

st.set_page_config(
    page_title="Pan Ideate Africa Knowledge Hub",
    page_icon="🌍",
    layout="wide"
)

st.sidebar.title("🌍 Pan Ideate Africa")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "🧪 Minerals & Chemistry",
        "🌱 Agriculture",
        "💼 Business Development",
        "🤖 Artificial Intelligence",
        "📚 Learning Centre",
        "🚀 Innovation",
        "📞 Contact"
    ],
    key="main_navigation"
)

if page == "🏠 Home":
    from pages.home import show_page
    show_page()

elif page == "🧪 Minerals & Chemistry":
    from pages.minerals import show_page
    show_page()

elif page == "🌱 Agriculture":
    from pages.agriculture import show_page
    show_page()

elif page == "💼 Business Development":
    from pages.business import show_page
    show_page()

elif page == "🤖 Artificial Intelligence":
    from pages.ai import show_page
    show_page()

elif page == "📚 Learning Centre":
    from pages.learning import show_page
    show_page()

elif page == "🚀 Innovation":
    from pages.innovation import show_page
    show_page()

elif page == "📞 Contact":
    from pages.contact import show_page
    show_page()