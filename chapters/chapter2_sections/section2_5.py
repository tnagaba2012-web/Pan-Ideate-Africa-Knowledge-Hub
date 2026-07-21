import streamlit as st

def show_section2_5():

    st.header("2.5 Elements – The Building Blocks of the Universe")

    st.markdown("""
# 🎯 Learning Objectives

By the end of this section, learners should be able to:

- Define an element.
- Explain the difference between an element and an atom.
- Recognize common elements found in nature.
- Understand why elements are important in science, mining, agriculture and manufacturing.
- Appreciate how elements are used in Pan Ideate Africa projects.

---

# 🌍 What is an Element?

An **element** is a pure substance made up of only one type of atom.

Every element has its own unique name, symbol and properties.

Scientists have discovered over 100 different elements, and together they form everything in the universe.

For example:

- Oxygen is made only of oxygen atoms.
- Iron is made only of iron atoms.
- Gold is made only of gold atoms.
- Carbon is made only of carbon atoms.

Each element has its own unique behaviour because its atoms are different.

---

# ⚛️ Examples of Common Elements

Below are some important elements that you will encounter throughout the Pan Ideate Africa Handbook.
""")

    st.table({
        "Element":["Hydrogen","Oxygen","Carbon","Iron","Silicon","Aluminium","Calcium","Sodium"],
        "Symbol":["H","O","C","Fe","Si","Al","Ca","Na"],
        "Common Uses":[
            "Water, fuel",
            "Breathing, water",
            "Biochar, charcoal, life",
            "Construction, machinery",
            "Glass, electronics, solar panels",
            "Cooking utensils, aircraft",
            "Bones, cement, agriculture",
            "Salt, food, industry"
        ]
    })

    st.markdown("""
---

# 🔍 Elements Around Us

Elements are found everywhere.

Examples include:

🪨 Rocks contain iron, silicon and aluminium.

🌱 Plants contain carbon, hydrogen and oxygen.

💧 Water contains hydrogen and oxygen.

🧂 Salt contains sodium and chlorine.

🌬️ Air contains oxygen and nitrogen.

Even your own body is made from many different elements working together.

---

# ⚖️ Elements vs Compounds

An element contains only one kind of atom.

Examples:

✔ Gold (Au)

✔ Iron (Fe)

✔ Oxygen (O)

A compound contains two or more different elements chemically joined together.

Examples:

✔ Water (H₂O)

✔ Salt (NaCl)

✔ Carbon dioxide (CO₂)

We will study compounds in the next section.

---
""")

    st.success("""
🌍 WHY THIS MATTERS IN PAN IDEATE AFRICA

Every project we develop depends on understanding elements.

Knowing the elements present in a mineral helps us:

✅ Identify valuable minerals.

✅ Produce better biochar.

✅ Improve bentonite products.

✅ Process kaolin for ceramics.

✅ Extract natural iron oxide pigments.

✅ Understand silicon for electronics and solar technology.

💡 Pan Ideate Africa Vision

By understanding elements, young innovators can identify local resources, process them into useful products and build sustainable businesses across Africa.
""")

    st.info("""
💡 DID YOU KNOW?

Iron (Fe) is one of the most abundant elements on Earth and is essential for making steel.

Silicon (Si) is the second most abundant element in the Earth's crust and is used to manufacture computer chips and solar panels.

Carbon (C) is the foundation of all known life and is also the main element found in biochar.
""")

    st.warning("""
⚠️ SAFETY NOTE

Although many elements are useful, some can be dangerous if handled incorrectly.

Always follow laboratory and workplace safety procedures when working with chemicals, metals or mineral samples.
""")

    st.markdown("""
---

# 🚀 Pan Ideate Africa Innovation Challenge

Look around your home or school and identify ten objects.

For each object ask yourself:

• Which element is the main material?

• Could that element be recycled?

• Could it be used to create a new product?

• Is this element found naturally in Uganda?

Think like a scientist, an engineer and an entrepreneur.

---

# 🧠 Knowledge Check

1. What is an element?

2. What is the difference between an atom and an element?

3. Name five common elements.

4. What is the chemical symbol for Iron?

5. What is the chemical symbol for Silicon?

6. Why are elements important in Pan Ideate Africa projects?

7. Give three products that depend on understanding different elements.
""")