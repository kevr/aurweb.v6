#!/usr/bin/env python3
from django.template.defaulttags import register
from django.db.models import Q
from users.models import *

@register.filter
def is_tu(user):
  if not user.is_authenticated:
    return False

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

@register.filter
def voted(user, package_base):
  if user.is_authenticated:
    return PackageVote.objects\
        .filter(user=user)\
        .filter(package_base=package_base)\
        .exists()

@register.filter
def notify(user, package_base):
  if user.is_authenticated:
    return PackageNotification.objects\
        .filter(user=user)\
        .filter(package_base=package_base)\
        .exists()

