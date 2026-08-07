import streamlit as st

def student_practical():

    st.header("🧪 Student Practical Activities")

    st.markdown("""
The laboratory provides opportunities for hands-on learning.

Suggested activities include:
""")

    activities = [
        "Collect iron-rich soil samples.",
        "Observe pigment colours.",
        "Wash and sediment samples.",
        "Dry the pigment.",
        "Grind and sieve the pigment.",
        "Compare colour differences.",
        "Record laboratory observations.",
        "Discuss possible industrial applications."
    ]

    for activity in activities:
        st.write(f"🔹 {activity}")

    st.info("📚 Practical learning builds scientific understanding and innovation.")