#!/usr/bin/env python3
from django.shortcuts import render
from django.utils import translation, timezone
from django.conf import settings
import calendar

from helpers.lang import get_languages
from users.models import AURUser, AURAccountType

make_aware = timezone.make_aware

# Constants
languages = get_languages()

'''
Main render function for HTML-based AUR pages. This function
provides a somewhat middleware for responses which injects the
following into the template context:

  user: Provided if the current user is logged in and is an AUR user
  is_authenticated: Boolean that helps templates see if we are authed as AUR
  lang: Current language
  languages: A mapping of all supported translation languages
  ts: Current timestamp

These fields are part of aurbase.html and thus are required in all views.

'''
def aur_render(request, path, ctx={}):
  if request.user.is_authenticated \
  and AURUser.objects.filter(user_ptr=request.user).exists():
    auruser = AURUser.objects.get(user_ptr=request.user)
    if "user" not in ctx:
      ctx["user"] = auruser
    ctx["is_authenticated"] = True
    ctx["lang"] = auruser.lang_preference
  else:
    # When unauthenticated, we try to get "lang" from the session
    # with a default of "en"
    ctx["is_authenticated"] = False
    ctx["lang"] = request.session.get(translation.LANGUAGE_SESSION_KEY, "en")

  translation.activate(ctx["lang"])
  ctx["languages"] = languages

  dt = timezone.now()
  ctx["ts"] = calendar.timegm(dt.timetuple())

  return render(request, path, ctx)


