import streamlit as st


def show_section_1_10():

    st.header("1.10 Chapter Summary")

    st.markdown("---")

    st.subheader("🎉 Congratulations!")

    st.success("""
You have successfully completed Chapter 1 of the Uganda Minerals Handbook.

This chapter introduced the fundamental concepts of mineral science and laid the
foundation for the exciting topics that follow in later chapters.
""")

    st.markdown("---")

    st.subheader("📚 What You Have Learned")

    st.write("""
Throughout this chapter you have explored:

✅ Why this handbook exists

✅ The structure of the Earth

✅ Minerals, rocks and ores

✅ The Rock Cycle

✅ Physical properties of minerals

✅ Mineral classification

✅ How minerals form

✅ Minerals in everyday life

✅ Introduction to mineral exploration
""")

    st.markdown("---")

    st.subheader("🌍 Why This Knowledge Matters")

    st.info("""
Minerals are the foundation of civilization.

They support agriculture, construction, manufacturing, medicine,
transportation, technology and national development.

Understanding minerals enables responsible exploration, value addition,
innovation and sustainable economic growth.
""")

    st.markdown("---")

    st.subheader("🇺🇬 Uganda's Opportunity")

    st.write("""
Uganda is richly blessed with valuable mineral resources.

By investing in education, research and responsible utilization,
young people can become scientists, innovators, entrepreneurs
and future industry leaders.

Knowledge is the first step toward transforming natural resources
into sustainable prosperity.
""")

    st.markdown("---")

    st.subheader("🚀 The Pan Ideate Africa Vision")

    st.success("""
The Pan Ideate Africa Knowledge Hub is more than a digital handbook.

It is a learning platform designed to:

📚 Build scientific knowledge.

🧪 Promote practical learning.

🌱 Support agriculture and environmental sustainability.

🏭 Encourage value addition.

💼 Create employment opportunities.

🌍 Inspire innovation across Africa.
""")

    st.markdown("---")

    st.subheader("📝 Chapter Review Quiz")

    questions = [
        "1. What is the difference between a mineral and a rock?",
        "2. Name the three major rock types.",
        "3. Which mineral group is the largest on Earth?",
        "4. Name four physical properties used to identify minerals.",
        "5. List four ways minerals form.",
        "6. Give five examples of minerals used in everyday life.",
        "7. What is mineral exploration?",
        "8. Why is responsible exploration important?",
        "9. Name three important mineral resources found in Uganda.",
        "10. How can mineral knowledge contribute to Uganda's development?"
    ]

    for q in questions:
        st.checkbox(q)

    st.markdown("---")

    st.subheader("🏆 Chapter Achievement")

    st.balloons()

    st.success("""
🏅 Congratulations!

You have completed Chapter 1:
'Introduction to Minerals, Rocks and the Earth.'

You are now ready to begin Chapter 2.

Keep learning.
Keep exploring.
Keep innovating.
""")

    st.markdown("---")

    st.subheader("➡️ Next Chapter Preview")

    st.write("""
Chapter 2 will introduce learners to:

🔬 Mineral Identification Techniques

🧪 Field Equipment

🪨 Rock and Mineral Sampling

🗺 Geological Mapping

🧭 Practical Field Investigations

These skills will prepare learners for real-world mineral exploration
and responsible resource development.
""")