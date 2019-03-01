#!/usr/bin/env python3
from django.template.defaulttags import register
from packages.models import *

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
def modified_at(package):
  if isinstance(package, Package):
    return package.package_base.modified_at.strftime("%Y-%m-%d %H:%M")
  else:
    return package.modified_at.strftime("%Y-%m-%d %H:%M")

@register.filter
def name(package):
  return package.name

@register.filter
def version(package):
  return package.version

@register.filter
def get_item(dictionary, key):
  return dictionary.get(key, "")

