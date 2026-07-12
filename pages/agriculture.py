import streamlit as st
st.error("THIS IS THE 561-LINE AGRICULTURE PAGE")
def show_page():

    st.title("🌱 Agriculture Innovation Centre")

    st.success("Building Africa's Future Through Science, Innovation and Sustainable Agriculture")

    st.markdown("""
### Welcome

The Agriculture Innovation Centre is designed to help farmers, students,
researchers and entrepreneurs discover modern agricultural technologies
that can transform food production across Uganda and Africa.
""")

    st.divider()

    st.header("🌍 Innovation Areas")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🌱 Projects", "25+")

    with col2:
        st.metric("🧪 Technologies", "80+")

    with col3:
        st.metric("🌍 Focus", "Africa")

    st.divider()

    st.header("🚀 Featured Technologies")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🌱 Biochar",
        "⚪ Kaolin",
        "💧 Water",
        "🐄 Livestock"
    ])

    with tab1:

        st.subheader("🌱 Biochar Technology")

        st.write("""
Biochar is one of the world's most exciting agricultural technologies.

Benefits include:

✅ Higher crop yields

✅ Improved soil fertility

✅ Better water retention

✅ Carbon storage

✅ Climate-smart agriculture

✅ Improved microbial activity

✅ Long-term soil improvement

Potential Uganda Products

• Biochar pellets

• Biochar fertilizer

• Biochar compost

• Biochar livestock bedding

• Biochar water filters
""")

    with tab2:

        st.subheader("⚪ Kaolin in Modern Agriculture")

        st.write("""
Kaolin is increasingly used worldwide.

Applications include:

✅ Protects crops from heat

✅ Reduces insect damage

✅ Improves fruit quality

✅ Reduces water loss

✅ Protects leaves from sunburn

✅ Safe mineral technology

Potential businesses

• Kaolin crop spray

• Kaolin seed coating

• Kaolin fertilizer additives

• Premium fruit protection products
""")

    with tab3:

        st.subheader("💧 Water Retention")

        st.write("""
Modern water management includes:

• Bentonite soil conditioners

• Biochar soil improvement

• Clay-based water retention

• Rainwater harvesting

• Smart irrigation

• Drought resilience
""")

    with tab4:

        st.subheader("🐄 Livestock Innovation")

        st.write("""
Emerging opportunities

• Feed binders

• Mineral supplements

• Biochar feed additives

• Animal health products

• Sustainable livestock systems
""")

    st.divider()

    st.header("🇺🇬 Opportunities for Uganda")

    opportunities = [
        "Biochar Production",
        "Kaolin Crop Protection",
        "Water Retention Products",
        "Organic Fertilizers",
        "Livestock Feed Technologies",
        "Climate Smart Agriculture",
        "Youth Agribusiness",
        "Agricultural Research"
    ]

    for item in opportunities:
        st.success(item)

    st.divider()

    st.info("🌍 Pan Ideate Africa is building practical science and innovation solutions for African agriculture.")
    st.divider()

st.header("📈 Agricultural Innovation Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🌱 Biochar Projects", "12")

with col2:
    st.metric("⚪ Kaolin Technologies", "18")

with col3:
    st.metric("💧 Water Solutions", "15")

with col4:
    st.metric("🌍 Sustainability", "100%")

st.divider()

st.header("📚 Learn More")

with st.expander("🌱 Advanced Biochar Technology", expanded=False):

    st.image(
        "https://images.unsplash.com/photo-1464226184884-fa280b87c399",
        use_container_width=True
    )

    st.markdown("""
### Why Biochar is Revolutionary

Biochar is one of the world's fastest-growing agricultural technologies.

### Benefits

✅ Improves soil fertility

✅ Stores carbon for hundreds of years

✅ Increases crop yields

✅ Improves microbial activity

✅ Reduces fertilizer requirements

✅ Improves water retention

### Future Products

• Biochar fertilizer

• Biochar compost

• Biochar pellets

• Biochar growing media

• Carbon credit projects
""")

with st.expander("⚪ Advanced Kaolin Technology"):

    st.image(
        "https://images.unsplash.com/photo-1501004318641-b39e6451bec6",
        use_container_width=True
    )

    st.markdown("""
### Modern Agricultural Kaolin

Kaolin is now used worldwide to protect crops.

### Advanced Uses

✅ Sunburn protection

✅ Heat stress reduction

✅ Fruit quality improvement

✅ Pest management

✅ Water conservation

### Uganda Opportunities

• Kaolin crop spray

• Export products

• Seed coatings

• Organic farming
""")

with st.expander("💧 Smart Water Management"):

    st.markdown("""
Modern agriculture uses:

• Biochar

• Bentonite

• Clay minerals

• Precision irrigation

• Soil moisture monitoring

• Water harvesting

These technologies greatly improve resilience to drought.
""")

with st.expander("🌍 Climate Smart Agriculture"):

    st.markdown("""
Africa can become a world leader through:

🌍 Carbon farming

🌱 Regenerative agriculture

♻️ Circular bioeconomy

🌿 Sustainable fertilizer production

🚜 Modern farm technology

🛰️ AI-assisted agriculture
""")

st.divider()

st.success("🚀 Pan Ideate Africa is creating one of Africa's largest agricultural knowledge platforms.")
st.divider()

st.header("🔬 African Agricultural Research Centre")

research = {
    "🌱 Biochar Research": [
        "Carbon sequestration",
        "Soil microbial enhancement",
        "Organic fertilizer carrier",
        "Waste biomass conversion",
        "Climate-smart agriculture"
    ],

    "⚪ Kaolin Research": [
        "Crop protection films",
        "Leaf temperature reduction",
        "Fruit quality improvement",
        "Water conservation",
        "Organic farming support"
    ],

    "💧 Water Technologies": [
        "Bentonite water retention",
        "Biochar moisture storage",
        "Clay soil improvement",
        "Rainwater harvesting",
        "Precision irrigation"
    ],

    "🌍 Future Agriculture": [
        "AI-powered farming",
        "Drone crop monitoring",
        "Smart irrigation",
        "Satellite agriculture",
        "Digital soil mapping"
    ]
}

for title, items in research.items():

    with st.expander(title):

        for item in items:
            st.write("✅", item)

st.divider()

st.header("📊 Technology Readiness")

biochar = st.progress(95)
kaolin = st.progress(90)
water = st.progress(88)
livestock = st.progress(82)

st.caption("🌱 Biochar Technologies")
st.caption("⚪ Kaolin Technologies")
st.caption("💧 Water Technologies")
st.caption("🐄 Livestock Technologies")

st.divider()

st.header("🏆 Pan Ideate Africa Innovation Scorecard")

left, right = st.columns(2)

with left:

    st.success("✅ Youth Training")

    st.success("✅ School Demonstrations")

    st.success("✅ Research Projects")

    st.success("✅ Community Innovation")

    st.success("✅ Entrepreneurship")

with right:

    st.success("✅ Climate Solutions")

    st.success("✅ Food Security")

    st.success("✅ Mineral Technologies")

    st.success("✅ Green Manufacturing")

    st.success("✅ Sustainable Development")

st.divider()

st.header("💡 Innovation Challenge")

st.info("""
Imagine every secondary school, university and youth group in Uganda learning:

• Biochar production

• Kaolin technologies

• Water retention science

• Soil chemistry

• Climate-smart agriculture

The result would be thousands of innovators creating businesses from local resources.
""")

st.divider()

st.header("🌍 Vision 2035")

st.markdown("""
### Pan Ideate Africa Vision

Our goal is to become Africa's leading knowledge platform for:

🌱 Agriculture

🧪 Minerals

🏭 Manufacturing

🤖 Artificial Intelligence

📚 Scientific Education

🚀 Innovation

Together we are building practical knowledge that creates jobs, businesses and opportunities across Africa.
""")

st.balloons()
st.divider()

st.header("🖼️ Agriculture Innovation Gallery")

gallery = [
    ("🌱 Biochar Production", "Converting agricultural waste into valuable soil improvement products."),
    ("⚪ Kaolin Crop Protection", "Protecting crops from heat stress and improving fruit quality."),
    ("💧 Water Retention", "Helping soils store moisture for longer periods."),
    ("🌾 Healthy Soils", "Building fertile soils using science and natural minerals."),
    ("🚜 Smart Farming", "Combining technology, innovation and sustainable agriculture."),
    ("🌍 Climate-Smart Agriculture", "Reducing environmental impact while increasing food production.")
]

cols = st.columns(2)

for i, (title, description) in enumerate(gallery):

    with cols[i % 2]:

        st.subheader(title)

        st.info(description)

        st.progress(min(55 + (i * 8), 100))

st.divider()

st.header("🧪 Chemistry Behind Agricultural Innovation")

chem1, chem2 = st.columns(2)

with chem1:

    st.success("🌱 Biochar Chemistry")

    st.markdown("""
**Main Components**

• Carbon (C)

• Hydrogen (H)

• Oxygen (O)

• Mineral Ash

**Benefits**

✅ Improves nutrient retention

✅ Encourages beneficial microbes

✅ Improves soil structure

✅ Stores carbon for decades
""")

with chem2:

    st.success("⚪ Kaolin Chemistry")

    st.markdown("""
**Chemical Formula**

Al₂Si₂O₅(OH)₄

**Main Elements**

• Aluminium

• Silicon

• Oxygen

• Hydrogen

**Agricultural Uses**

✅ Crop protection

✅ Heat reduction

✅ Water conservation

✅ Improved fruit quality
""")

st.divider()

st.header("🎓 Learn → Practice → Produce → Earn")

steps = [
    "📚 Learn the science",
    "🧪 Perform school demonstrations",
    "🏭 Build small production units",
    "🌍 Supply local farmers",
    "📈 Expand into commercial production",
    "🚀 Export African innovations"
]

for number, step in enumerate(steps, start=1):
    st.write(f"**Step {number}:** {step}")

st.divider()

st.header("🇺🇬 Uganda Innovation Opportunities")

left, center, right = st.columns(3)

with left:
    st.metric("Youth Enterprises", "10,000+")

with center:
    st.metric("Potential Jobs", "100,000+")

with right:
    st.metric("Farmer Impact", "Millions")

st.success("""
🌍 Pan Ideate Africa believes Uganda can become a continental leader in sustainable agriculture, mineral innovation and youth-led scientific entrepreneurship.
""")
st.error("END OF 561-LINE PAGE")