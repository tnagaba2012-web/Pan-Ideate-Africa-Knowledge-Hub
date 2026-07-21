import streamlit as st

def show_section2_9():

    st.header("2.9 The Periodic Table – The Map of All Elements")

    st.markdown("""
# 🎯 Learning Objectives

By the end of this section, learners should be able to:

- Explain what the Periodic Table is.
- Understand why scientists use the Periodic Table.
- Identify the information shown for each element.
- Recognize some important elements used in Pan Ideate Africa projects.

---

# 🌍 Introduction

The **Periodic Table** is a scientific chart that organizes all known chemical elements.

It helps scientists understand how elements are related and predict their properties.

Today, the Periodic Table contains over **100 confirmed elements**, arranged in rows (periods) and columns (groups).

---

# 🧪 A Simple Illustration

Imagine a giant library.

Instead of books, every shelf contains chemical elements.

Elements with similar characteristics are placed together, making them easier to study and use.

The Periodic Table is like a map that helps scientists find the right "building block" for a particular purpose.

---

# 🔍 What Information Does Each Element Show?

Each element has:

• Name

• Chemical Symbol

• Atomic Number

• Atomic Mass

For example:

Iron

Symbol: Fe

Atomic Number: 26

Atomic Mass: 55.85

---

# 🌱 Why is the Periodic Table Important?

The Periodic Table helps us:

✅ Identify elements.

✅ Predict how elements behave.

✅ Understand mineral composition.

✅ Design new materials.

✅ Improve agriculture.

✅ Develop medicines.

✅ Manufacture industrial products.

It is one of the most important tools in science.
""")

    st.table({
        "Element": [
            "Hydrogen",
            "Carbon",
            "Oxygen",
            "Silicon",
            "Iron",
            "Aluminium",
            "Calcium",
            "Sodium"
        ],
        "Symbol": [
            "H",
            "C",
            "O",
            "Si",
            "Fe",
            "Al",
            "Ca",
            "Na"
        ],
        "Main Use": [
            "Fuel & Water",
            "Life & Biochar",
            "Breathing",
            "Glass & Solar Panels",
            "Steel",
            "Aircraft & Utensils",
            "Bones & Cement",
            "Salt & Industry"
        ]
    })

    st.success("""
🌍 WHY THIS MATTERS IN PAN IDEATE AFRICA

The Periodic Table is our guide to understanding Uganda's natural resources.

When we discover a mineral, the first question is:

**Which elements does it contain?**

That answer determines:

✅ How the mineral can be processed.

✅ Which products can be made.

✅ Its value.

✅ Its industrial applications.

Learning the Periodic Table helps us transform raw materials into valuable products.
""")

    st.info("""
💡 DID YOU KNOW?

The symbols of some elements come from Latin names.

Examples:

Fe = Ferrum (Iron)

Na = Natrium (Sodium)

K = Kalium (Potassium)

That is why their symbols do not always match their English names.
""")

    st.warning("""
⚠️ SAFETY NOTE

The Periodic Table contains both safe and hazardous elements.

Always learn the properties of an element before handling it in a laboratory or workshop.
""")

    st.markdown("""
---

# 💼 Pan Ideate Africa Opportunity Box

Knowing the elements present in a mineral helps us identify business opportunities.

Examples:

🟤 Iron (Fe)

Possible products:

• Steel products

• Construction materials

• Farm tools

• Machinery parts

---

🟡 Silicon (Si)

Possible products:

• Glass

• Solar panels

• Electronics

• Ceramics

---

⚪ Aluminium (Al)

Possible products:

• Cooking utensils

• Window frames

• Roofing materials

• Packaging

---

⚫ Carbon (C)

Possible products:

• Biochar

• Activated carbon

• Water filters

• Soil improvement products

Science creates opportunities for innovation and entrepreneurship.

---

# 🇺🇬 Uganda Focus

As we continue through the handbook, we will build a **Uganda Mineral Atlas** showing:

• Where important minerals are found.

• Their chemical composition.

• Industrial uses.

• Agricultural applications.

• Business opportunities.

This will help learners connect science with Uganda's natural resources.

---

# 🧠 Knowledge Check

1. What is the Periodic Table?

2. Why do scientists use the Periodic Table?

3. What information is shown for each element?

4. What is the chemical symbol for Iron?

5. What is the chemical symbol for Silicon?

6. Explain how the Periodic Table supports mineral processing and manufacturing.

7. Name three business opportunities linked to elements found in the Periodic Table.
""")