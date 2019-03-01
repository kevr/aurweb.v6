from django.shortcuts import render
from django.views import View
from django.utils import timezone
from datetime import timedelta
from django.db.models import F, Q
from collections import OrderedDict
from django.utils import translation

# aurweb stuff
import aurweb.config

from helpers.render import aur_render
from packages.models import Package, PackageBase
from users.models import AURUser, AURAccountType
import configparser

# Force load of aurweb
if not aurweb.config._parser:
  try:
    aurweb.config.get('', '')
  except configparser.NoSectionError:
    pass

class HomeView(View):
  def get(self, request, **kwargs):
    if request.user.is_authenticated:
      user = AURUser.objects.get(user_ptr=request.user)
      lang = user.lang_preference

    orphaned = Package.objects.filter(package_base__maintainer=None)

    now = timezone.now()

    pkgs_added_past_7 = Package.objects.filter(
        package_base__submitted_at__gte=(now - timedelta(days=7)))
    pkgs_mod_past_7 = Package.objects.filter(
        package_base__modified_at__gte=(now - timedelta(days=7)))
    pkgs_mod_past_year = Package.objects.filter(
        package_base__modified_at__gte=(now - timedelta(days=365)))
    pkgs_mod_never = Package.objects.filter(
        package_base__modified_at=F("package_base__submitted_at"))

    registered_users = AURUser.objects.count()
    
    tu_types = AURAccountType.objects.filter(
        Q(name="Trusted User") | Q(name="Trusted User & Developer"))

    tu_users = AURUser.objects.filter(account_type__in=tu_types).count()

    recent_updates = Package.objects.all()\
        .order_by("name", "-package_base__modified_at")[:15]

    stats = OrderedDict({
      "Packages": Package.objects.count(),
      "Orphan Packages": 0, 
      "Packages added in the past 7 days":
        pkgs_added_past_7.count(),
      "Packages updated in the past 7 days":
        pkgs_mod_past_7.count(),
      "Packages updated in the past year":
        pkgs_mod_past_year.count(),
      "Packages never updated":
        pkgs_mod_never.count(),
      "Registered Users": registered_users,
      "Trusted Users": tu_users
    })

    fingerprints = dict()
    if not request.user.is_authenticated:
      fingerprints = {
        k.upper() : aurweb.config.get("fingerprints", k)
        for k in aurweb.config._parser["fingerprints"]
      }

    flagged_pkgs = Package.objects.none()
    my_pkgs = Package.objects.none()
    co_pkgs = Package.objects.none()
    if request.user.is_authenticated:
      auruser = AURUser.objects.get(user_ptr=request.user)
      # Some sorting through our user's packages for pretty output
      for pkgbase in auruser.flagged.all().order_by("-modified_at"):
        flagged_pkgs |= pkgbase.packages.all()
      for pkgbase in auruser.maintained.all().order_by("-modified_at"):
        my_pkgs |= pkgbase.packages.all()
      for pkgbase in auruser.comaintained.all().order_by("-modified_at"):
        co_pkgs |= pkgbase.packages.all()

    return aur_render(request, "home/index.html", {
      "recent_updates": recent_updates,
      "stats": stats,
      "has_fingerprints": len(fingerprints) > 0,
      "fingerprints": fingerprints,
      "flagged_pkgs": flagged_pkgs,
      "maintained_pkgs": my_pkgs,
      "comaintained_pkgs": co_pkgs,
    })

  def post(self, request):
    return self.get(request)

# Create your views here.
