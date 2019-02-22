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

# Global list used to track our database creation stack
# we will use this to clean up if we run into any errors
global created_objects
created_objects = []

'''
Conversion functions, format to_<app>_<table>(row, db): From mysql to django model ORM.

Each function shall take a single row to convert.

@param fr The row from the export database
@param fdb The handle to the export database
'''
def convert_datetime(orig):
  if not orig:
    return None
  return timezone.make_aware(
      timezone.datetime.fromtimestamp(orig)).strftime(
        "%Y-%m-%d %H:%M:%S")

# Simple database row creation if:
#   The destination database does not already have a record matching
#   exactly the source row's provided keyword arguments.
def create_if_not(Object, **kwargs):
  global created_objects
  if not Object.objects.filter(**kwargs).exists():
    created_objects.append(Object.objects.create(**kwargs))
    return True

def to_users_auraccounttype(row, db):
  _id, name = row
  if create_if_not(AURAccountType, pk=_id, name=name):
    print("%s copied" % str(row))

def to_users_auruser(row, db):
  user_id, account_type_id, suspended, username,\
  email, hide_email, password, salt, reset_key, \
  realname, lang_preference, tz, homepage, \
  irc_nick, pgp_key, last_login, last_login_ip_address, \
  last_ssh_login, last_ssh_login_ip_address, inactivity_ts, \
  registered_at, comment_notify, update_notify, \
  ownership_notify = row

  if not AURUser.objects.filter(username=username).exists():
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

    # Do this manually since we are copying a hash
    user.password = password
    user.save()
    print("%s copied" % str(row))

def to_users_term(row, db):
  term_id, desc, url, rev = row
  if create_if_not(Term, pk=term_id, description=desc,
      url=url, revision=rev):
    print("%s copied" % str(row))

def to_users_acceptedterm(row, db):
  user_id, term_id, rev = row
  auruser = AURUser.objects.get(pk=user_id)
  term = Term.objects.get(pk=term_id)
  if create_if_not(AcceptedTerm, user=auruser, term=term,
      revision=rev):
    print("%s copied" % str(row))

def to_users_ban(row, db):
  ip_address, ban_ts = row
  if create_if_not(Ban, ip_address=ip_address,
      banned_at=make_aware(ban_ts).strftime("%Y-%m-%d %H:%M:%S")):
    print("%s copied" % str(row))

def to_users_apiratelimit(row, db):
  ip_address, requests, window_start = row
  if create_if_not(APIRateLimit,
      ip_address=ip_address, requests=requests,
      window_start=window_start):
    print("%s copied" % str(row))

def to_packages_dependencytype(row, db):
  _id, name = row
  if create_if_not(DependencyType, pk=_id, name=name):
    print("%s copied" % str(row))

def to_packages_relationtype(row, db):
  _id, name = row
  if create_if_not(RelationType, pk=_id, name=name):
    print("%s copied" % str(row))

def to_packages_requesttype(row, db):
  _id, name = row
  if create_if_not(RequestType, pk=_id, name=name):
    print("%s copied" % str(row))

def to_packages_license(row, db):
  _id, name = row
  if create_if_not(License, pk=_id, name=name):
    print("%s copied" % str(row))

def to_packages_group(row, db):
  _id, name = row
  if create_if_not(Group, pk=_id, name=name):
    print("%s copied" % str(row))

def to_packages_packagebase(row, db):
  _id, name, votes, pop, out_of_date_ts, flagger_comment, \
      submitted_ts, modified_ts, flagger_uid, submitter_uid, \
      maintainer_uid, packager_uid = row

  flagger, submitter = None, None
  maintainer, packager = None, None

  if AURUser.objects.filter(pk=flagger_uid).exists():
    flagger = AURUser.objects.get(pk=flagger_uid)
  if AURUser.objects.filter(pk=submitter_uid).exists():
    submitter = AURUser.objects.get(pk=submitter_uid)
  if AURUser.objects.filter(pk=maintainer_uid).exists():
    maintainer = AURUser.objects.get(pk=maintainer_uid)
  if AURUser.objects.filter(pk=packager_uid).exists():
    packager = AURUser.objects.get(pk=packager_uid)

  if create_if_not(PackageBase, pk=_id,
      name=name,
      num_votes=votes,
      popularity=pop,
      submitted_at=convert_datetime(submitted_ts),
      modified_at=convert_datetime(modified_ts),
      out_of_date_at=convert_datetime(out_of_date_ts),
      flagger=flagger,
      flagger_comment=flagger_comment,
      submitter=submitter,
      maintainer=maintainer,
      packager=packager):
    print("%s copied" % str(row))

def to_packages_package(row, db):
  pkg_id, pkgbase_id, name, version, desc, url = row
  pkgbase = PackageBase.objects.get(pk=pkgbase_id)
  if create_if_not(Package, pk=pkg_id,
      package_base=pkgbase,
      name=name,
      version=version,
      description=desc,
      url=url):
    print("%s copied" % str(row))

def to_packages_officialprovider(row, db):
  _id, pkgname, repo, provides = row
  pkg = Package.objects.get(name=name)
  if create_if_not(OfficialProvider, pk=_id,
      package=pkg, repo=repo, provides=provides):
    print("%s copied" % str(row))

def to_packages_packagedependency(row, db):
  pkg_id, dep_type_id, name, desc, cond, arch = row
  pkg = Package.objects.get(pk=pkg_id)
  dep_type = DependencyType.objects.get(pk=dep_type_id)
  if create_if_not(PackageDependency,
      package=pkg,
      dep_type=dep_type,
      name=name,
      desc=desc,
      condition=cond,
      arch=arch):
    print("%s copied" % str(row))

def to_packages_packagekeyword(row, db):
  pkgbase_id, keyword = row
  pkgbase = PackageBase.objects.get(pk=pkgbase_id)
  if create_if_not(PackageKeyword, package_base=pkgbase, keyword=keyword):
    print("%s copied" % str(row))

def to_packages_packagesource(row, db):
  pkg_id, source, arch = row
  pkg = Package.objects.get(pk=pkg_id)
  if create_if_not(PackageSource, package=pkg, source=source, arch=arch):
    print("%s copied" % str(row))

def to_packages_packagerelation(row, db):
  pkg_id, rel_type_id, name, condition, arch = row
  pkg = Package.objects.get(pk=pkg_id)
  rel_type = RelationType.objects.get(pk=rel_type_id)
  if create_if_not(PackageRelation, package=pkg,
     rel_type=rel_type, name=name, condition=condition, arch=arch):
    print("%s copied" % str(row))

def to_packages_packagenotification(row, db):
  pkgbase_id, user_id = row
  pkgbase = PackageBase.objects.get(pk=pkgbase_id)
  user = AURUser.objects.get(pk=user_id)
  if create_if_not(PackageNotification, package_base=pkgbase, user=user):
    print("%s copied" % str(row))

def to_packages_packagelicense(row, db):
  pkg_id, lic_id = row
  pkg = Package.objects.get(pk=pkg_id)
  lic = License.objects.get(pk=lic_id)
  if create_if_not(PackageLicense, package=pkg, license=lic):
    print("%s copied" % str(row))

def to_packages_packagecomments(row, db):
  _id, pkgbase_id, user_id, comments, rendered_comment, \
      comment_ts, edited_ts, edited_user_id, del_ts, \
      del_user_id, pinned_ts = row

  pkgbase = PackageBase.objects.get(pk=pkgbase_id)
  user = AURUser.objects.get(pk=user_id)
  edited_user = None if not edited_user_id else \
      AURUser.objects.get(pk=edited_user_id)
  del_user = None if not del_user_id else \
      AURUser.objects.get(pk=del_user_id)

  if create_if_not(PackageComments, package_base=pkgbase,
      user=user,
      edited_user=user,
      deleted_user=del_user,
      comment=comments,
      rendered_comment=rendered_comment,
      commented_at=convert_datetime(comment_ts),
      edited_at=convert_datetime(edited_ts),
      deleted_at=convert_datetime(del_ts),
      pinned_at=convert_datetime(pinned_ts)):
    print("%s copied" % str(row))

def to_packages_packagecomaintainer(row, db):
  user_id, pkgbase_id, pri = row
  user = AURUser.objects.get(pk=user_id)
  pkgbase = PackageBase.objects.get(pk=pkgbase_id)
  if not create_if_not(PackageComaintainer, user=user,
      package_base=pkgbase, priority=pri):
    print("%s copied" % str(row))

def to_packages_packageblacklist(row, db):
  _id, name = row
  if not create_if_not(PackageBlacklist, pk=_id, name=name):
    print("%s copied" % str(row))

def to_packages_packagegroup(row, db):
  pkg_id, group_id = row
  pkg = Package.objects.get(pk=pkg_id)
  group = Group.objects.get(pk=group_id)
  if create_if_not(PackageGroup, package=pkg, group=group):
    print("%s copied" % str(row))

def to_packages_packagevote(row, db):
  user_id, pkgbase_id, vote_ts = row
  user = AURUser.objects.get(pk=user_id)
  pkgbase = PackageBase.objects.get(pk=pkgbase_id)
  if create_if_not(PackageVote, user=user,
      package_base=pkgbase, voted_at=convert_datetime(vote_ts)):
    print("%s copied" % str(row))

def to_packages_sshpubkey(row, db):
  user_id, fp, pk = row
  user = AURUser.objects.get(pk=user_id)
  if create_if_not(SSHPubKey, user=user, fingerprint=fp, pub_key=pk):
    print("%s copied" % str(row))

def to_packages_tuvoteinfo(row, db):
  _id, agenda, username, submitted_ts, end_ts, quorum, \
      submitter_id, yes, no, abstain, active_tus = row

  submitter = AURUser.objects.get(pk=submitter_id)

  if create_if_not(TUVoteInfo, submitter=submitter,
      pk=_id,
      agenda=agenda,
      submitted_at=convert_datetime(submitted_ts),
      end_at=convert_datetime(end_ts),
      quorum=quorum,
      yes=yes, no=no, abstain=abstain,
      active_tus=active_tus,
      user=username):
    print("%s copied" % str(row))

def to_packages_tuvote(row, db):
  vote_id, user_id = row
  vote = TUVoteInfo.objects.get(pk=vote_id)
  user = AURUser.objects.get(pk=user_id)
  if create_if_not(TUVote, vote=vote, user=user):
    print("%s copied" % str(row))

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
  "Licenses": {
    "table": "packages_license",
    "function": to_packages_license
  },
  "Groups": {
    "table": "packages_group",
    "function": to_packages_group
  },
  "PackageBases": {
    "table": "packages_packagebase",
    "function": to_packages_packagebase
  },
  "Packages": {
    "table": "packages_package",
    "function": to_packages_package
  },
  "OfficialProviders": {
    "table": "packages_officialprovider",
    "function": to_packages_officialprovider
  },
  "PackageDepends": {
    "table": "packages_packagedependency",
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
  "TU_VoteInfo": {
    "table": "packages_tuvoteinfo",
    "function": to_packages_tuvoteinfo
  },
  "TU_Votes": {
    "table": "packages_tuvote",
    "function": to_packages_tuvote
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

  try:
    for k, v in convert_tables.items():
      print("\n--- processing table conversion: %s ---\n" % k)
      stmt = "SELECT * FROM %s" % k
      cursor = db.execute(stmt)

      rows = cursor.fetchall()
      for row in rows:
        v["function"](row, db)
  except Exception as exc:
    print("Caught fatal exception while running migration; rerolling stack...")
    created_objects.reverse()
    for obj in created_objects:
      print("Deleting %s" % str(obj))
      obj.delete()
    print("Exception occurred: %s" % str(exc))

  return 0

if __name__ == "__main__":
  e = main()
  exit(e)
