import os
from dotenv import load_dotenv
from openai import OpenAI
from knowledge.biochar import get_info as get_biochar_info
from knowledge.minerals import get_info as get_minerals_info
from knowledge.iron_oxide import get_info as get_iron_oxide_info

from pigment_preparation.introduction import get_info as get_pigment_intro
from pigment_preparation.pigment_types import get_info as get_pigment_types
from knowledge.agriculture import get_info as get_agriculture_info
from knowledge.business import answer_business

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_ai(question):
    question = question.lower()

    # -----------------------------
    # BIOCHAR
    # -----------------------------
    if "biochar" in question:
        return get_biochar_info()
        # ------------------------------
    # BUSINESS
    # ------------------------------
    if any(keyword in question for keyword in [
        "business",
        "business suite",
        "entrepreneur",
        "entrepreneurship",
        "startup",
        "marketplace",
        "inventory",
        "stock",
        "sales",
        "customer",
        "invoice",
        "receipt",
        "employee",
        "expense",
        "profit",
        "pricing",
        "price",
        "market",
        "investment",
        "investor",
        "business plan",
        "business planning",
        "selling",
        "selling products",
        "agricultural business",
        "mineral business",
        "product business"
    ]):
        return answer_business(question)
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
      # ============================================================
    # AI FALLBACK
    # ============================================================

    try:
        response = client.responses.create(
            model="gpt-5-mini",
            instructions="""
You are Pan Ideate AI, the intelligent assistant of the
Pan Ideate Africa Knowledge Hub.

Your focus is Africa, especially Uganda and East Africa.

Help users with:
- Minerals and geology
- Chemistry
- Agriculture
- Biochar
- Kaolin and bentonite
- Iron oxide pigments
- Manufacturing
- Entrepreneurship and business
- Innovation
- Science education
- African languages and learning

Give clear, practical and educational answers.
When discussing chemistry, minerals, agriculture or production,
include appropriate safety and environmental considerations.

Do not pretend that an answer comes from the Pan Ideate
Knowledge Hub when it does not. Clearly distinguish general
AI knowledge from information contained in the Hub.
""",
            input=question
        )

        return response.output_text

    except Exception as e:
        return f"""
Pan Ideate AI could not connect to the AI service right now.

Please check your internet connection and OpenAI API key.

Technical message:
{e}
"""