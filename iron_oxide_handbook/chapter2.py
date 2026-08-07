import streamlit as st
from iron_oxide_handbook.geology_intro import introduction
from iron_oxide_handbook.formation import formation
from iron_oxide_handbook.iron_oxide_minerals import iron_oxide_minerals

def show_chapter2():
    st.title("📘 Chapter 2")

    introduction()
    formation()
    iron_oxide_minerals()

st.header("CHAPTER 2")
st.title("Geology and Occurrence of Iron Oxide Pigments")

st.markdown("""
## Learning Objectives

After studying this chapter, the reader should be able to:

- Explain how iron oxide deposits are formed.
- Identify the major iron oxide minerals.
- Describe the geological environments where iron oxide pigments occur.
- Understand methods used in exploration.
- Recognize Uganda's iron oxide resources.
- Explain the distribution of iron oxide resources.
- Appreciate the economic importance of iron oxide pigments.

""")