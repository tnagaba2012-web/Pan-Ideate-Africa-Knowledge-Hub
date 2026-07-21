import streamlit as st

def show_section2_4():

    st.header("2.4 Structure of the Atom")

    st.markdown("""
# 🎯 Learning Objectives

By the end of this section, learners should be able to:

- Describe the structure of an atom.
- Identify the nucleus.
- Explain the difference between protons, neutrons and electrons.
- Describe the electrical charges of atomic particles.
- Understand why the atomic structure is important in science and industry.

---

# ⚛️ The Structure of an Atom

Although atoms are extremely small, scientists have discovered that they have an internal structure.

An atom is made up of two main parts:

1. The **Nucleus**
2. The **Electron Cloud (Electron Shells)**

The nucleus is located at the centre of the atom.

Electrons move around the nucleus in energy levels called shells.

---

# 🔬 Simple Illustration
""")

    st.code("""
                 e⁻

          e⁻             e⁻


              ┌─────────┐
              │P⁺  N⁰   │
              │ N⁰ P⁺   │
              └─────────┘

          e⁻             e⁻

                 e⁻
""", language="text")

    st.info("""
### Diagram Explanation

🟢 **P⁺ = Proton**

🔵 **N⁰ = Neutron**

🟡 **e⁻ = Electron**

The centre box represents the **nucleus**.

The electrons move around the nucleus in shells.
""")

    st.markdown("""
---

# 🟥 Protons

Protons are positively charged particles.

Characteristics:

- Positive (+) charge
- Located in the nucleus
- Relatively heavy

Every element contains protons.

The number of protons determines which element an atom is.

---

# ⬜ Neutrons

Neutrons have no electrical charge.

Characteristics:

- Neutral (0) charge
- Located in the nucleus
- Nearly the same mass as protons

Neutrons help stabilize the nucleus.

---

# 🔵 Electrons

Electrons are negatively charged particles.

Characteristics:

- Negative (-) charge
- Move around the nucleus
- Very light

Electrons are responsible for:

- Electricity
- Chemical reactions
- Bond formation
- Conductivity

---

# 📊 Summary Table
""")

    st.table({
        "Particle":["Proton","Neutron","Electron"],
        "Charge":["Positive (+)","Neutral (0)","Negative (-)"],
        "Location":["Nucleus","Nucleus","Electron Shells"],
        "Relative Mass":["Heavy","Heavy","Very Light"]
    })

    st.success("""
🌍 WHY THIS MATTERS IN PAN IDEATE AFRICA

Understanding atomic structure helps us explain:

✅ Why iron behaves differently from aluminium.

✅ Why bentonite absorbs water.

✅ Why biochar improves soils.

✅ Why kaolin is suitable for ceramics.

✅ Why silicon is used to manufacture solar panels.

✅ Why different minerals have different properties.

💡 Every product we develop begins with understanding the particles inside atoms.
""")

    st.warning("""
⚠️ SAFETY NOTE

Although atoms themselves are incredibly small and safe to learn about, some materials made from atoms can be hazardous.

Always wear appropriate protective equipment when handling chemicals, mineral powders or laboratory materials.
""")

    st.info("""
💡 DID YOU KNOW?

More than 99.9% of the mass of an atom is concentrated in its tiny nucleus!

The electrons occupy most of the space around the nucleus, making atoms much larger than their nuclei.
""")

    st.markdown("""
---

# 🚀 Pan Ideate Africa Innovation Challenge

Imagine you have discovered a new mineral in Uganda.

Ask yourself:

• Which atoms might it contain?

• Would it contain iron?

• Silicon?

• Aluminium?

• Calcium?

• Magnesium?

How could understanding its atomic structure help us create a valuable new product?

---

# 🧠 Knowledge Check

1. What are the two main parts of an atom?

2. Which particles are found inside the nucleus?

3. Which particle has a negative charge?

4. Why are protons important?

5. Explain how understanding atomic structure can help Pan Ideate Africa develop new products.
""")