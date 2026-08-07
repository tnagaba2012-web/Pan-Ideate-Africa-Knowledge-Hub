import streamlit as st

from pigment_preparation.introduction import introduction
from pigment_preparation.pigment_types import pigment_types
from pigment_preparation.pigment_colours import pigment_colours
from pigment_preparation.preparation_methods import preparation_methods
from pigment_preparation.raw_materials import raw_materials
from pigment_preparation.processing_equipment import processing_equipment
from pigment_preparation.quality_control import quality_control
from pigment_preparation.industrial_uses import industrial_uses
from pigment_preparation.safety import safety
from pigment_preparation.student_practical import student_practical
from pigment_preparation.pigment_gallery import pigment_gallery
from pigment_preparation.uganda_resource_map import uganda_resource_map


def show_pigment_preparation():
    st.title("🧪 Iron Oxide Pigment Preparation Laboratory")

    st.info("""
Welcome to the Iron Oxide Pigment Preparation Laboratory.

This laboratory provides practical guidance on the preparation,
processing, properties and industrial applications of natural and
synthetic iron oxide pigments.
""")

    introduction()
    pigment_types()
    pigment_colours()
    preparation_methods()
    raw_materials()
    processing_equipment()
    quality_control()
    industrial_uses()
    safety()
    student_practical()
    pigment_gallery()
    uganda_resource_map()