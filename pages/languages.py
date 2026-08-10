import streamlit as st
from utils.translations import translate

def show_page():

    st.title("🌍 Choose Your Language")

    st.success("Choose your preferred language below.")
    
        # -----------------------------------------
    # LANGUAGE SELECTOR
    # -----------------------------------------

    languages = {
        "UG Runyankore": "Runyankore",
        "UG Luganda": "Luganda",
        "UG Runyoro/Rutoro": "Runyoro/Rutoro",
        "RW Kinyarwanda": "Kinyarwanda",
        "UG Ateso": "Ateso",
        "UG Luo": "Luo",
        "UG Lugisu": "Lugisu",
        "FR French": "French",
        "SA Arabic": "Arabic",
    }

    selected_language = st.selectbox(
        "🌍 Select your preferred language:",
        list(languages.keys())
    )
# Save the selected language for use across the app
    st.session_state["language"] = selected_language
    st.session_state["selected_language"] = languages[selected_language]

    st.success(
        f"Selected language: **{languages[selected_language]}**"
    )
        # -----------------------------------------
    # BASIC TRANSLATION DICTIONARY - STEP 2
    # -----------------------------------------

    translations = {
        "Choose Your Language": {
            "English": "Choose Your Language",
            "Luganda": "Londa Olulimi Lwo",
            "Swahili": "Chagua Lugha Yako",
            "Runyankore": "Ronda Orurimi Rwawe",
            "Ateso": "Kijar Olum",
            "Luo": "Yier Uwol",
            "Lugisu": "Londa Olulimi Lwo",
            "French": "Choisissez votre langue",
            "Kinyarwanda": "Hitamo Ururimi",
            "Runyoro/Rutoro": "Londa Orurimi",
            "Arabic": "اختر لغتك",
        },

        "Welcome to the African Languages Centre": {
            "English": "Welcome to the African Languages Centre",
            "Luganda": "Tukwanirizza ku African Languages Centre",
            "Swahili": "Karibu kwenye Kituo cha Lugha za Afrika",
            "Runyankore": "Ronda Orurimi Rwawe",
            "Ateso": "Kijar Olum",
            "Luo": "Yier Uwol",
            "Lugisu": "Londa Olulimi Lwo",
            "French": "Bienvenue au Centre des Langues Africaines",
            "Kinyarwanda": "Murakaza neza mu Kigo cy'Indimi Nyafurika",
            "Runyoro/Rutoro": "Mwayanza omu Kicweka ky'Enimi za Africa",
            "Arabic": "مرحباً بكم في مركز اللغات الأفريقية",
        },

        "Agriculture": {
            "English": "Agriculture",
            "Luganda": "Obulimi",
            "Swahili": "Kilimo",
            "Runyankore": "Obuhingi",
            "Ateso": "Akiparang",
            "Luo": "Pur",
            "Lugisu": "Bulimi",
            "French": "Agriculture",
            "Kinyarwanda": "Ubuhinzi",
            "Runyoro/Rutoro": "Obulimi",
            "Arabic": "الزراعة",
        },

        "Business": {
            "English": "Business",
            "Luganda": "Obusuubuzi",
            "Swahili": "Biashara",
            "Runyankore": "Obushuubuzi",
            "Ateso": "Akiwaran",
            "Luo": "Tijiri",
            "Lugisu": "Bubusi",
            "French": "Entreprise",
            "Kinyarwanda": "Ubucuruzi",
            "Runyoro/Rutoro": "Obusuubuzi",
            "Arabic": "الأعمال",
        },

        "Learning Centre": {
            "English": "Learning Centre",
            "Luganda": "Ekifo ky'Okuyiga",
            "Swahili": "Kituo cha Kujifunza",
            "Runyankore": "Omwanya rwokwegyeramu",
            "Ateso": "Eitwe ng'ale",
            "Luo": "Kar kwanjo",
            "Lugisu": "Esika y'okusoma",
            "French": "Centre d'apprentissage",
            "Kinyarwanda": "Ikigo Cyigisha",
            "Runyoro/Rutoro": "Kicweka ky'Okwega",
            "Arabic": "مركز التعلم",
        },
    }

    # -----------------------------------------
     # --------------------------------------------------
    # AFRICAN LANGUAGES CENTRE
    # --------------------------------------------------

    current_language = languages[selected_language]

    st.divider()

    st.header(
        f"🌍 {translations['Welcome to the African Languages Centre'].get(
            current_language,
            'Welcome to the African Languages Centre'
        )}"
    )

    st.success(
        "🌍 African Languages Centre"
    )

    st.write(
        f"🌱 {translations['Agriculture'].get(current_language, 'Agriculture')}"
    )

    st.write(
        f"💼 {translations['Business'].get(current_language, 'Business')}"
    )

    st.write(
        f"📚 {translations['Learning Centre'].get(current_language, 'Learning Centre')}"
    )
  