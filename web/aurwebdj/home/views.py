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

# Force load of aurweb
if not aurweb.config._parser:
  try: aurweb.config.get('', '')
  except: pass

def sum_packages_from_base(bases):
  return sum([base.packages.all().count() for base in bases])

class HomeView(View):
  def get(self, request, **kwargs):
    if request.user.is_authenticated:
      user = AURUser.objects.get(user_ptr=request.user)
      lang = user.lang_preference

    pkgs = PackageBase.objects.all()
    orphaned = pkgs.filter(maintainer=None)

    now = timezone.now()
    pkgs_added_past_7 = pkgs.filter(submitted_at__gte=(now - timedelta(days=7)))
    pkgs_mod_past_7 = pkgs.filter(modified_at__gte=(now - timedelta(days=7)))
    pkgs_mod_past_year = pkgs.filter(modified_at__gte=(now - timedelta(days=365)))
    pkgs_mod_never = pkgs.filter(modified_at=F("submitted_at"))

    registered_users = AURUser.objects.all()
    
    tu_type = AURAccountType.objects.get(name="Trusted User")
    tu_dev_type = AURAccountType.objects.get(name="Trusted User & Developer")

    tu_users = registered_users.filter(
        Q(account_type=tu_type) | Q(account_type=tu_dev_type))

    recent_updates = pkgs.order_by("-modified_at")[:15]

    updates = []
    for pkgbase in recent_updates:
      for pkg in pkgbase.packages.all():
        updates.append({
          "name": pkg.name,
          "version": pkg.version,
          "updated_at": pkgbase.modified_at.strftime("%Y-%m-%d %H:%M")
        })
    # Truncate, we only need 15 for home page
    updates = updates[15:]

    pkgs = sum_packages_from_base(pkgs)

    stats = OrderedDict({
      "Packages": pkgs,
      "Orphan Packages":
        sum_packages_from_base(orphaned),
      "Packages added in the past 7 days":
        sum_packages_from_base(pkgs_added_past_7),
      "Packages updated in the past 7 days":
        sum_packages_from_base(pkgs_mod_past_7),
      "Packages updated in the past year":
        sum_packages_from_base(pkgs_mod_past_year),
      "Packages never updated":
        sum_packages_from_base(pkgs_mod_never),
      "Registered Users": len(registered_users),
      "Trusted Users": len(tu_users)
    })

    fingerprints = {
      k.upper() : aurweb.config.get("fingerprints", k)
      for k in aurweb.config._parser["fingerprints"]
    }

    return aur_render(request, "home/index.html", {
      "recent_updates": updates,
      "stats": stats,
      "has_fingerprints": len(fingerprints) > 0,
      "fingerprints": fingerprints
    })

  def post(self, request):
    setlang = None
    if "setlang" in request.POST:
      setlang = request.POST["setlang"]

    return self.get(request)

# Create your views here.
