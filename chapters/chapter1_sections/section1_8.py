import streamlit as st


def show_section_1_8():

    st.header("1.8 Minerals in Everyday Life")

    st.markdown("---")

    st.markdown("""
### 🎯 Learning Objectives

By the end of this section learners should be able to:

- Explain how minerals improve everyday life.
- Identify common products made from minerals.
- Appreciate the importance of Uganda's mineral resources.
- Relate minerals to agriculture, construction, health and technology.
- Understand why responsible mineral utilization supports national development.
""")

    st.markdown("---")

    st.subheader("Introduction")

    st.write("""
Minerals are part of almost everything we use every day. Although many people only associate
minerals with mining, they are found in our homes, schools, hospitals, farms, industries,
roads, mobile phones and even the food we eat.

Without minerals, modern civilization would not exist.
""")

    st.markdown("---")

    st.subheader("🏠 Minerals in Our Homes")

    st.write("""
Many household products come directly from minerals.

Examples include:

• Glass (Quartz)

• Ceramic tiles (Kaolin)

• Cement (Limestone)

• Paints (Iron Oxides)

• Cooking salt (Halite)

• Electrical wiring (Copper)

• Roofing sheets (Iron)

• Aluminum utensils (Bauxite)
""")

    st.markdown("---")

    st.subheader("🌱 Minerals in Agriculture")

    st.success("""
Agriculture depends heavily on minerals.

Examples:

• Limestone neutralizes acidic soils.

• Rock phosphate supplies phosphorus.

• Bentonite improves water retention.

• Kaolin protects crops.

• Biochar and clay improve soil fertility.

Healthy soils produce healthier crops.
""")

    st.markdown("---")

    st.subheader("🏥 Minerals in Health")

    st.write("""
Many minerals support healthcare.

Examples:

• Gypsum for medical casts.

• Calcium minerals for strong bones.

• Iron supplements.

• Salt containing iodine.

• Medical equipment manufactured from mineral-based materials.
""")

    st.markdown("---")

    st.subheader("📱 Minerals in Technology")

    st.info("""
Modern technology depends on minerals.

Examples include:

• Silicon for computer chips.

• Copper for electricity.

• Gold in electronic circuits.

• Lithium in batteries.

• Rare earth elements in smartphones and renewable energy technologies.
""")

    st.markdown("---")

    st.subheader("🇺🇬 Uganda's Opportunity")

    st.write("""
Uganda possesses many valuable minerals that can support industrialization,
employment and innovation.

Instead of exporting only raw materials, value addition can create jobs,
support local industries and improve the economy.

This is one of the core visions of Pan Ideate Africa.
""")

    st.markdown("---")

    st.subheader("🚀 Connection to Pan Ideate Africa Projects")

    st.success("""
Examples include:

🎨 Iron Oxide Pigments

🤍 Kaolin Technologies

🟢 Bentonite Products

🌱 Biochar Innovations

💧 Water Retention Technologies

🧂 Rock Salt Processing

💎 Future Silicon Technologies

Together these projects demonstrate how mineral knowledge can improve everyday life.
""")

    st.markdown("---")

    st.subheader("Summary")

    st.success("""
✔ Minerals are essential to modern life.

✔ Minerals support agriculture, construction, medicine, technology and manufacturing.

✔ Uganda has abundant mineral resources with enormous development potential.

✔ Responsible utilization and value addition create employment and economic growth.
""")

    st.markdown("---")

    st.subheader("📝 Self-Assessment")

    questions = [
        "1. Name five products made from minerals.",
        "2. Which mineral is used to manufacture glass?",
        "3. How does limestone help agriculture?",
        "4. Why is silicon important in technology?",
        "5. Why is value addition important for Uganda?"
    ]

    for q in questions:
        st.checkbox(q)

    st.success("Excellent! You have completed Section 1.8.")