import streamlit as st

st.set_page_config(page_title="Pan Ideate Africa Knowledge Hub",page_icon="🌍",layout="wide")
st.sidebar.image("https://img.icons8.com/color/96/africa.png",width=80)
st.sidebar.title("Pan Ideate Africa")
page=st.sidebar.radio("Navigation",["🏠 Home","🧪 Minerals & Chemistry","🌱 Agriculture","💼 Business Development","🤖 Artificial Intelligence","📚 Learning Centre","🚀 Innovation","📞 Contact"])

if page=="🏠 Home":
    st.title("🌍 Pan Ideate Africa Knowledge Hub")
    st.markdown("""# Building Africa Through Science, Innovation & Practical Education

Welcome to the Pan Ideate Africa Knowledge Hub.

Our mission is to empower African youth through science, technology, innovation, entrepreneurship and practical education.

Together we can transform ideas into industries.
""")
    st.info("🚀 Welcome to Version 2 of the Pan Ideate Africa Knowledge Hub!")
    c1,c2,c3=st.columns(3)
    with c1: st.metric("📚 Learning Articles","250+")
    with c2: st.metric("🧪 Science Projects","40+")
    with c3: st.metric("🌱 Innovation Goal","100+")
    st.divider()
    p1,p2=st.columns(2)
    with p1:
        st.success("🌱 Biochar Project")
        st.write("Transform agricultural waste into valuable biochar.")
        st.success("🟤 Bentonite Project")
        st.write("Develop water-retention and industrial products.")
    with p2:
        st.success("🧪 Iron Oxide Pigments")
        st.write("Natural pigments for paints and construction.")
        st.success("⚪ Kaolin & Silicon")
        st.write("Advanced materials for industry.")
elif page=="🧪 Minerals & Chemistry":
    st.title("🧪 Minerals & Chemistry")
    st.write("Explore Uganda's minerals and chemistry.")
else:
    st.title(page)
    st.info("This section is under development.")
