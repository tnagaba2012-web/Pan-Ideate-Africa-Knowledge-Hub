from knowledge.biochar import get_info as get_biochar_info
from knowledge.minerals import get_info as get_minerals_info
from knowledge.iron_oxide import get_info as get_iron_oxide_info

from pigment_preparation.introduction import get_info as get_pigment_intro
from pigment_preparation.pigment_types import get_info as get_pigment_types
from knowledge.agriculture import get_info as get_agriculture_info


def ask_ai(question):
    question = question.lower()

    # -----------------------------
    # BIOCHAR
    # -----------------------------
    if "biochar" in question:
        return get_biochar_info()
          # AGRICULTURE
    if any(keyword in question for keyword in [
        "agriculture",
        "agricultural",
        "farming",
        "farmer",
        "sustainable agriculture",
        "water retention",
        "drought",
        "irrigation",
        "livestock",
        "animal nutrition",
        "climate smart",
        "climate-smart",
        "mineral technologies in agriculture",
        "agricultural opportunities",
        "agricultural knowledge",
        "agricultural project",
        "agriculture project",
        "interactive learning"
    ]):
        return get_agriculture_info()
    # -----------------------------
    # PIGMENT TYPES
    # -----------------------------
    if any(keyword in question for keyword in [
        "pigment types",
        "types of pigments",
        "red iron oxide",
        "yellow iron oxide",
        "black iron oxide",
        "brown iron oxide",
    ]):
        return get_pigment_types()

    # -----------------------------
    # PIGMENT INTRODUCTION
    # -----------------------------
    if any(keyword in question for keyword in [
        "pigment",
        "pigments",
        "iron oxide",
        "pigment preparation",
        "pigment laboratory",
    ]):
        return get_pigment_intro()

    # -----------------------------
    # IRON OXIDE
    # -----------------------------
    if any(keyword in question for keyword in [
        "hematite",
        "iron ore",
        "iron oxide mineral",
    ]):
        return get_iron_oxide_info()

    # -----------------------------
    # MINERALS
    # -----------------------------
    if any(keyword in question for keyword in [
        "mineral",
        "minerals",
        "uganda minerals",
        "kaolin",
        "bentonite",
        "quartz",
        "silica",
        "silicon",
        "rock salt",
        "salt",
        "limestone",
        "gold",
        "copper",
        "graphite",
        "phosphate",
        "vermiculite",
        "tungsten",
        "tin",
        "cement",
        "glass",
        "paint",
        "ceramic",
        "fertilizer",
        "construction",
        "chemistry",
        "chemical",
        "formula",
    ]):
        return get_minerals_info()

    # -----------------------------
    # DEFAULT
    # -----------------------------
    return """
Sorry, I don't know that yet.

Pan Ideate AI is still learning.

Currently I can answer questions about:

• Biochar
• Minerals
• Iron Oxide Pigments
• Pigment Types
"""