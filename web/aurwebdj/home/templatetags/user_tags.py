#!/usr/bin/env python3
from django.template.defaulttags import register
from django.db.models import Q
from users.models import *

@register.filter
def is_tu(user):
  tu_types = AURAccountType.objects.filter(
      Q(name="Trusted User") | Q(name="Trusted User & Developer"))
  auruser = AURUser.objects.get(user_ptr=user)
  for tu_type in tu_types:
    if auruser.account_type == tu_type:
      return True
  return False

@register.filter
def aur(user):
  auruser = AURUser.objects.get(user_ptr=user)
  return auruser

