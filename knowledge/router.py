from knowledge.biochar import get_info as get_biochar_info
from knowledge.minerals import get_info as get_minerals_info

def ask_ai(question):
    question = question.lower()

    # Biochar
    if "biochar" in question:
        return get_biochar_info()

    # Minerals
    if (
        "mineral" in question
        or "kaolin" in question
        or "bentonite" in question
        or "quartz" in question
        or "silica" in question
        or "rock salt" in question
        or "limestone" in question
        or "iron ore" in question
    ):
        return get_minerals_info()

    return """
Sorry, I don't know that yet.

Pan Ideate AI is still learning.

Available topics:

• Biochar
• Minerals
"""