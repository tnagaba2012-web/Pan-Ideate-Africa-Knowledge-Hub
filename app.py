import streamlit as st

# Import chapters
from chapters.chapter1_sections import show_chapter1

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Pan-ID8 African Knowledge Hub",
    page_icon="🌍",
    layout="wide"
)

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
st.sidebar.title("🌍 Pan-ID8")
st.sidebar.markdown("### African Knowledge Hub")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "📚 Chapter 1",
        "🧪 Chemistry Lab",
        "🌱 Agriculture",
        "🤖 AI Assistant",
        "📊 Progress"
    ]
)

# --------------------------------------------------
# Home Page
# --------------------------------------------------
if page == "🏠 Home":

    st.title("🌍 Pan-ID8 African Knowledge Hub")

    st.subheader("Uganda Minerals Master Project")

    st.success("Welcome to Version 8")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("## 📚 Learning")

        st.write("• Uganda Minerals Master Project")
        st.write("• Chemistry")
        st.write("• Mineral Identification")
        st.write("• Exploration")
        st.write("• Value Addition")

    with col2:

        st.markdown("## 🚀 Future Modules")

        st.write("• Agriculture")
        st.write("• Biochar")
        st.write("• Bentonite")
        st.write("• Kaolin")
        st.write("• Silicon")
        st.write("• AI Learning")

    st.markdown("---")

    st.info(
        "Our mission is to build Africa's most practical knowledge platform "
        "for minerals, chemistry, agriculture, innovation, and entrepreneurship."
    )

# --------------------------------------------------
# Chapter 1
# --------------------------------------------------
elif page == "📚 Chapter 1":

    show_chapter1()

# --------------------------------------------------
# Chemistry
# --------------------------------------------------
elif page == "🧪 Chemistry Lab":

    st.title("🧪 Chemistry Laboratory")

    st.write("Coming soon...")

# --------------------------------------------------
# Agriculture
# --------------------------------------------------
elif page == "🌱 Agriculture":

    st.title("🌱 Agriculture")

    st.write("Coming soon...")

# --------------------------------------------------
# AI Assistant
# --------------------------------------------------
elif page == "🤖 AI Assistant":

    st.title("🤖 AI Assistant")

    st.write("Coming soon...")

# --------------------------------------------------
# Progress
# --------------------------------------------------
elif page == "📊 Progress":

    st.title("📊 Progress")

    st.progress(10)

    st.success("Chapter 1 has been completed and approved.")

    st.write("More progress tracking will be added in future versions.")