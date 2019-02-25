#!/usr/bin/env python3
from django.utils.translation import ugettext as _
from django.template import Library
from django.utils.safestring import mark_safe
register = Library()

@register.simple_tag
def trans_args(tr):
  cols = tr.split('|')
  tr = cols[0]
  args = None
  if len(cols) > 1:
    args = list(cols[1:])

  trans = _(tr)
  trans_str = None
  if args:
    trans_str = trans.format(*args)
  return mark_safe(trans_str)

@register.filter
def args(tr, args):
  if args is None:
    return False
  arg_list = [arg.strip() for arg in args.split(',')]
  print(tr)
  return mark_safe(tr.format(*arg_list))

@register.simple_tag
def trans_strip(text):
  return _(text.rstrip().strip())

