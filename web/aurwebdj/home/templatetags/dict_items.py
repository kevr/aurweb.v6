#!/usr/bin/env python3
from django.template.defaulttags import register
from packages.models import PackageVote, PackageNotification

@register.filter
def sub(a, b):
  return a - b

@register.filter
def mul(a, b):
  return a * b

@register.filter
def div(a, b):
  return a / b

@register.filter
def get_item(dictionary, key):
  return dictionary.get(key, "")

