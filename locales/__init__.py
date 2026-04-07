from locales.ar import AR_TEXTS
from locales.en import EN_TEXTS


def get_text(key, language="ar"):
    if language == "en":
        return EN_TEXTS.get(key, AR_TEXTS.get(key, key))
    return AR_TEXTS.get(key, key)
