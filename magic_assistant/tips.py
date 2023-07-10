

tips_en = {"welcome": "Nice to meet you, you can tell me what you want to do."
           }

tips = {"en": tips_en}

def get_tip(language_code: str, tip: str):
    return tips.get(language_code, {}).get(tip, "")

