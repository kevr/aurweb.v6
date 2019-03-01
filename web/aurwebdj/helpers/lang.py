#!/usr/bin/env python3
from collections import OrderedDict

LANGUAGES = {
  "ar": "Arabic",
  "ast": "Asturianu",
  "ca": "Català",
  "cs": "Český",
  "da": "Dansk",
  "de": "Deutsch",
  "en": "English",
  "el": "Ελληνικά",
  "es": "Español",
  "es_419": "Español (Latinoamérica)",
  "fi": "Finnish",
  "fr": "Français",
  "he": "עברית",
  "hr": "Hrvatski",
  "hu": "Magyar",
  "it": "Italiano",
  "ja": "日本語",
  "nb": "Norsk",
  "nl": "Nederlands",
  "pl": "Polski",
  "pt_BR": "Português (Brasil)",
  "pt_PT": "Português (Portugal)",
  "ro": "Română",
  "ru": "Русский",
  "sk": "Slovenčina",
  "sr": "Srpski",
  "tr": "Türkçe",
  "uk": "Українська",
  "zh_CN": "简体中文",
  "zh_TW": "正體中文",
}

def get_list():
  return LANGUAGES.keys()

def get_languages():
  return LANGUAGES

