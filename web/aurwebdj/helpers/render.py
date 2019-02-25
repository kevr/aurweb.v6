#!/usr/bin/env python3
from django.shortcuts import render
from django.utils import translation
from django.conf import settings

from helpers.lang import getDict
from users.models import AURUser, AURAccountType

LANGUAGES = getDict()

def aur_render(request, path, ctx={}):
  request_lang = request.session[translation.LANGUAGE_SESSION_KEY]
  set_lang = False

  if request.method.upper() == "POST":
    if "setlang" in request.POST:
      request_lang = request.POST["setlang"]
      set_lang = True

  if AURUser.objects.filter(uid=request.user.id).exists():
    user = AURUser.objects.get(user_ptr=request.user)
    if user.lang_preference != request_lang:
      user.lang_preference = request_lang
      user.save()
    ctx["lang"] = user.lang_preference
  else:
    lang_pref = "en"
    if request_lang:
      lang_pref = request_lang
    ctx["lang"] = lang_pref

  translation.activate(ctx["lang"])
  request.session[translation.LANGUAGE_SESSION_KEY] = ctx["lang"]

  # Give our list or supported languages
  ctx["languages"] = LANGUAGES

  response = render(request, path, ctx)
  if set_lang:
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, ctx["lang"])
  return response

