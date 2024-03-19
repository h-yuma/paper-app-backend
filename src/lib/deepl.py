import deepl
import os
from dotenv import load_dotenv

load_dotenv()

DEEPLE_API_KEY = os.environ["DEEPLE_API_KEY"]

language_codes = {
    "English": "EN",
    "Japanese": "JA",
    "Chinese": "ZH",
}

def translate_by_deepl(text, target_lang, auth_key=DEEPLE_API_KEY):
    # initialize the DeepL translator
    translator = deepl.Translator(auth_key)

    result = translator.translate_text(text, target_lang=language_codes[target_lang])

    return result.text