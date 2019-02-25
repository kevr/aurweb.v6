#!/usr/bin/env python3
from django.template.defaulttags import register
from packages.models import PackageVote, PackageNotification

@register.filter
def get_item(dictionary, key):
  return dictionary.get(key, "")

@register.filter
def voted(user, package_base):
  return PackageVote.objects\
      .filter(user=user)\
      .filter(package_base=package_base)\
      .exists()

@register.filter
def notify(user, package_base):
  return PackageNotification.objects\
      .filter(user=user)\
      .filter(package_base=package_base)\
      .exists()

