# ============================================================
# PAN IDEATE AFRICA
# CENTRAL TRANSLATION SYSTEM
# ============================================================

TRANSLATIONS = {

    "English": {
        "choose_language": "Choose Your Language",
        "select_language": "Select your preferred language:",
        "welcome": "Welcome to the African Languages Centre.",
        "agriculture": "Agriculture",
        "business": "Business",
        "learning_centre": "Learning Centre",
        "minerals_chemistry": "Minerals & Chemistry",
        "innovation": "Innovation",
        "contact": "Contact",
        "home": "Home",
    },

    "Luganda": {
        "choose_language": "Londa Olulimi Lwo",
        "select_language": "Londa olulimi lw'oyagala:",
        "welcome": "Tukwanirizza ku African Languages Centre.",
        "agriculture": "Obulimi",
        "business": "Obusuubuzi",
        "learning_centre": "Ekifo ky'Okuyiga",
        "minerals_chemistry": "Eby'obugagga eby'omu ttaka ne Kemisiti",
        "innovation": "Obuyiiya",
        "contact": "Tukwatagane",
        "home": "Awaka",
    },

    "Swahili": {
        "choose_language": "Chagua Lugha Yako",
        "select_language": "Chagua lugha unayopendelea:",
        "welcome": "Karibu katika Kituo cha Lugha za Kiafrika.",
        "agriculture": "Kilimo",
        "business": "Biashara",
        "learning_centre": "Kituo cha Kujifunza",
        "minerals_chemistry": "Madini na Kemia",
        "innovation": "Ubunifu",
        "contact": "Wasiliana Nasi",
        "home": "Nyumbani",
    },

    "Runyankore": {
        "choose_language": "Toorana Orurimi Rwawe",
        "select_language": "Toorana orurimi orw'oyenda:",
        "welcome": "Murakaza neza aha African Languages Centre.",
        "agriculture": "Obuhingi",
        "business": "Obushuubuzi",
        "learning_centre": "Ekifo ky'Okwega",
        "minerals_chemistry": "Amacwe n'Ekemiya",
        "innovation": "Obuhangiro",
        "contact": "Tukwatagane",
        "home": "Eka",
    },

    "Ateso": {
        "choose_language": "Kigoro Ekegono Kon",
        "select_language": "Kigoro ekegono kon:",
        "welcome": "Eyalama noi ku African Languages Centre.",
        "agriculture": "Akiima",
        "business": "Akiro",
        "learning_centre": "Ekokoro n'Eiyalam",
        "minerals_chemistry": "Minerals ka Chemistry",
        "innovation": "Inovation",
        "contact": "Kiporu",
        "home": "Ekar",
    },

    "Luo": {
        "choose_language": "Yer Dhok Mabor",
        "select_language": "Yer dhok ma idwaro:",
        "welcome": "Wabiro e African Languages Centre.",
        "agriculture": "Pur",
        "business": "Tijari",
        "learning_centre": "Kar Puonj",
        "minerals_chemistry": "Minerals gi Chemistry",
        "innovation": "Yub",
        "contact": "Wach Kod Wa",
        "home": "Odera",
    },

    "Lugisu": {
        "choose_language": "Londa Olulimi Lwo",
        "select_language": "Londa olulimi lwoyagala:",
        "welcome": "Tukwanirizza ku African Languages Centre.",
        "agriculture": "Obulimi",
        "business": "Obusuubuzi",
        "learning_centre": "Ekifo ky'Okuyiga",
        "minerals_chemistry": "Minerals ne Chemistry",
        "innovation": "Obuyiiya",
        "contact": "Tukwatagane",
        "home": "Awaka",
    },

    "French": {
        "choose_language": "Choisissez votre langue",
        "select_language": "Sélectionnez votre langue préférée :",
        "welcome": "Bienvenue au Centre des langues africaines.",
        "agriculture": "Agriculture",
        "business": "Affaires",
        "learning_centre": "Centre d'apprentissage",
        "minerals_chemistry": "Minéraux et chimie",
        "innovation": "Innovation",
        "contact": "Contact",
        "home": "Accueil",
    },

    "Arabic": {
        "choose_language": "اختر لغتك",
        "select_language": "اختر لغتك المفضلة:",
        "welcome": "مرحباً بكم في مركز اللغات الأفريقية.",
        "agriculture": "الزراعة",
        "business": "الأعمال",
        "learning_centre": "مركز التعلم",
        "minerals_chemistry": "المعادن والكيمياء",
        "innovation": "الابتكار",
        "contact": "اتصل بنا",
        "home": "الرئيسية",
    },
}


def translate(key, language="English"):
    """
    Return the translation for a given key and language.
    Falls back to English if the translation is unavailable.
    """

    if language not in TRANSLATIONS:
        language = "English"

    return TRANSLATIONS[language].get(
        key,
        TRANSLATIONS["English"].get(key, key)
    )