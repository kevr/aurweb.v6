#!/usr/bin/env python3
from datetime import datetime
import pytz
import re

def get_timezones():
  timezones = pytz.all_timezones
  output = []
  for ctz in timezones:
    if ctz == "UTC" or re.match("^\w+/\w+$", ctz):
      zone = pytz.timezone(ctz)
      offset = zone.utcoffset(datetime.now())
      hours, remaining = divmod(offset.seconds, 3600)
      minutes, seconds = divmod(remaining, 60)
      output.append(("(UTC%s%02d:%02d)" % ('-' if offset.days < 0 else '+', hours, minutes), ctz))

  return sorted(output, key=lambda x: (x[0], x[1]))

