#!/usr/bin/env python3
from django.shortcuts import render
from django.utils import translation, timezone
from django.conf import settings
import calendar

import helpers.lang
from users.models import AURUser, AURAccountType

make_aware = timezone.make_aware

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
  ctx["languages"] = helpers.lang.LANGUAGES

  dt = timezone.now()
  ctx["ts"] = calendar.timegm(dt.timetuple())

  return render(request, path, ctx)


