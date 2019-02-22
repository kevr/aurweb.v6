#!/usr/bin/env python3
''' Migration script used to migrate databases from PHP to Django.abs '''
import sys, os
import click
import pytz
import string
import random

BASE_DIR = os.path.abspath(os.path.dirname(os.path.abspath(sys.argv[0])))
AURWEB_DJANGO_DIR = os.path.join(BASE_DIR, "../../../web/aurwebdj")
AURWEB_DJANGO_DIR = os.path.abspath(AURWEB_DJANGO_DIR)

sys.path.insert(0, os.path.join(BASE_DIR, "../.."))

import aurweb.config
import aurweb.db
from collections import OrderedDict

# Prepare django environment so we can access its models.

sys.path.insert(0, AURWEB_DJANGO_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aurwebdj.settings')

from django.apps import apps
from django.conf import settings
from django.core import management
from django.utils import timezone
from django.utils.dateparse import parse_datetime

apps.ready = False
apps.populate(settings.INSTALLED_APPS)

from users.models import *
from packages.models import *

def convert_datetime(orig):
  return timezone.make_aware(
      timezone.datetime.fromtimestamp(orig)).strftime(
        "%Y-%m-%d %H:%M:%S")
'''
Conversion functions, format to_<app>_<table>(row, db): From mysql to django model ORM.

Each function shall take a single row to convert.

@param fr The row from the export database
@param fdb The handle to the export database
'''

users_memo = []

def to_users_auraccounttype(row, db):
  # Insert account type with name column if it doesn't exist
  if not AURAccountType.objects.filter(pk=row[0], name=row[1]).exists():
    AURAccountType.objects.create(pk=row[0], name=row[1])
    print("%s copied" % str(row))

def to_users_auruser(row, db):

  user_id, account_type_id, suspended, username,\
  email, hide_email, passwd, salt, reset_key, \
  realname, lang_preference, tz, homepage, \
  irc_nick, pgp_key, last_login, last_login_ip_address, \
  last_ssh_login, last_ssh_login_ip_address, inactivity_ts, \
  registered_at, comment_notify, update_notify, \
  ownership_notify = row

  if AURUser.objects.filter(username=username).exists():
    return

  user = AURUser.objects.create_user(
      pk=user_id,
      account_type = AURAccountType.objects.get(pk=account_type_id),
      suspended=bool(suspended),
      email=email,
      hide_email=bool(hide_email),
      username=username,
      realname=realname,
      pgp_key=pgp_key,
      lang_preference=lang_preference,
      tz=tz,
      reset_key=reset_key,
      homepage=homepage,
      irc_nick=irc_nick,
      last_login=convert_datetime(last_login),
      last_login_ip_address=last_login_ip_address,
      last_ssh_login=convert_datetime(last_ssh_login),
      last_ssh_login_ip_address=last_ssh_login_ip_address,
      inactivity_ts=inactivity_ts,
      registered_at=timezone.make_aware(registered_at).strftime(
        "%Y-%m-%d %H:%M:%S"),
      comment_notify=comment_notify,
      update_notify=update_notify,
      ownership_notify=ownership_notify)

  user.password = passwd

  user.save()

  print("%s copied" % str(row))

def to_users_term(row, db):
  term_id, desc, url, rev = row
  if not Term.objects.filter(pk=term_id).exists():
    Term.objects.create(pk=term_id, description=desc, url=url, revision=rev)

  print("%s copied" % str(row))

def to_users_acceptedterm(row, db):
  user_id, term_id, rev = row
  auruser = AURUser.objects.get(pk=user_id)
  term = Term.objects.get(pk=term_id)
  if not AcceptedTerm.objects.filter(user=auruser, term=term, revision=rev).exists():
    AcceptedTerm.objects.create(user=auruser, term=term, revision=rev)

  print("%s copied" % str(row))

def to_users_ban(row, db):
  ip_address, ban_ts = row
  if not Ban.objects.filter(ip_address=ip_address).exists():
    Ban.objects.create(ip_address=ip_address,
        banned_at=make_aware(ban_ts).strftime("%Y-%m-%d %H:%M:%S"))

  print("%s copied" % str(row))

def to_users_apiratelimit(row, db):
  ip_address, requests, window_start = row
  if not APIRateLimit.objects.filter(ip_address=ip_address).exists():
    APIRateLimit.objects.create(ip_address=ip_address,
        requests=requests, window_start=window_start)

  print("%s created" % str(row))

def to_packages_dependencytype(row, db):
  print(row)

def to_packages_relationtype(row, db):
  print(row)

def to_packages_requesttype(row, db):
  print(row)

def to_packages_officialprovider(row, db):
  print(row)

def to_packages_license(row, db):
  print(row)

def to_packages_group(row, db):
  print(row)

def to_packages_package(row, db):
  print(row)

def to_packages_packagebase(row, db):
  print(row)

def to_packages_packagedependency(row, db):
  print(row)

def to_packages_packagekeyword(row, db): #todo
  print(row)

def to_packages_packagesource(row, db): #todo
  print(row)

def to_packages_packagerelation(row, db): #todo
  print(row)

def to_packages_packagenotification(row, db):
  print(row)

def to_packages_packagelicense(row, db):
  print(row)

def to_packages_packagecomments(row, db):
  print(row)

def to_packages_packagecomaintainer(row, db):
  print(row)

def to_packages_packageblacklist(row, db):
  print(row)

def to_packages_packagegroup(row, db):
  print(row)

def to_packages_packagevote(row, db):
  print(row)

def to_packages_sshpubkey(row, db):
  print(row)

def to_packages_tuvote(row, db):
  print(row)

def to_packages_tuvoteinfo(row, db):
  print(row)

convert_tables = OrderedDict({
  "AccountTypes": {
    "table": "users_auraccounttype",
    "function": to_users_auraccounttype
  },
  "Users": {
    "table": "users_auruser",
    "function": to_users_auruser
  },
  "Bans": {
    "table": "users_ban",
    "function": to_users_ban
  },
  "ApiRateLimit": {
    "table": "users_apiratelimit",
    "function": to_users_apiratelimit
  },
  "DependencyTypes": {
    "table": "packages_dependencytype",
    "function": to_packages_dependencytype
  },
  "RelationTypes": {
    "table": "packages_relationtype",
    "function": to_packages_relationtype
  },
  "RequestTypes": {
    "table": "packages_requesttypes",
    "function": to_packages_requesttype
  },
  "OfficialProviders": {
    "table": "packages_officialprovider",
    "function": to_packages_officialprovider
  },
  "Licenses": {
    "table": "packages_license",
    "function": to_packages_license
  },
  "Groups": {
    "table": "packages_group",
    "function": to_packages_group
  },
  "Packages": {
    "table": "packages_package",
    "function": to_packages_package
  },
  "PackageBases": {
    "table": "packages_packagebase",
    "function": to_packages_packagebase
  },
  "PackageDepends": {
    "table": "package_packagedependency",
    "function": to_packages_packagedependency
  },
  "PackageGroups": {
    "table": "packages_packagegroup",
    "function": to_packages_packagegroup
  },
  "PackageKeywords": {
    "table": "packages_packagekeyword",
    "function": to_packages_packagekeyword
  },
  "PackageSources": {
    "table": "packages_packagesource",
    "function": to_packages_packagesource
  },
  "PackageRelations": {
    "table": "packages_packagerelation",
    "function": to_packages_packagerelation
  },
  "PackageLicenses": {
    "table": "packages_packagelicense",
    "function": to_packages_packagelicense
  },
  "PackageComments": {
    "table": "packages_packagecomments",
    "function": to_packages_packagecomments
  },
  "PackageComaintainers": {
    "table": "packages_packagecomaintainer",
    "function": to_packages_packagecomaintainer
  },
  "PackageVotes": {
    "table": "packages_packagevote",
    "function": to_packages_packagevote
  },
  "PackageNotifications": {
    "table": "packages_packagenotification",
    "function": to_packages_packagenotification
  },
  "PackageBlacklist": {
    "table": "packages_packageblacklist",
    "function": to_packages_packageblacklist
  },
  "SSHPubKeys": {
    "table": "packages_sshpubkey",
    "function": to_packages_sshpubkey
  },
  "Terms": {
    "table": "users_term",
    "function": to_users_term
  },
  "AcceptedTerms": {
    "table": "users_acceptedterm",
    "function": to_users_acceptedterm
  },
  "TU_Votes": {
    "table": "packages_tuvote",
    "function": to_packages_tuvote
  },
  "TU_VoteInfo": {
    "table": "packages_tuvoteinfo",
    "function": to_packages_tuvoteinfo
  },
})

'''
Main program entry: Django should be configured for it's database
connection before running this script.
'''
@click.command()
@click.option("--setup", is_flag=True, default=False, help="Run migrations for destination django database.")
def main(setup):

  if setup:
    management.call_command("makemigrations")
    management.call_command("migrate")

  db = aurweb.db.Connection()

  for k, v in convert_tables.items():
    print("\n--- TABLE: %s ---\n" % k)
    stmt = "SELECT * FROM %s" % k
    cursor = db.execute(stmt)

    rows = cursor.fetchall()
    for row in rows:
      v["function"](row, db)

  return 0

if __name__ == "__main__":
  e = main()
  exit(e)
