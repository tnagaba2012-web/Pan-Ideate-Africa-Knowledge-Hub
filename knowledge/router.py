from knowledge.biochar import get_info as get_biochar_info
from knowledge.minerals import get_info as get_minerals_info


def ask_ai(question):
    question = question.lower()

    # -----------------------------
    # BIOCHAR
    # -----------------------------
    if "biochar" in question:
        return get_biochar_info()

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
        "iron",
        "iron ore",
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
        "formula"
    ]):
        return get_minerals_info()

    # -----------------------------
    # DEFAULT RESPONSE
    # -----------------------------
    return """
Sorry, I don't know that yet.

Pan Ideate AI is still learning.

Available topics:

• Biochar
• Minerals
"""