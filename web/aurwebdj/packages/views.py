from django.shortcuts import render
from django.views import View
from django.db.models import Q, F

from helpers.render import aur_render
from packages.models import *

class PackagesView(View):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.search_by = {
      "n": self.search_by_name,
      "N": self.search_by_exact_name,
      "nd": self.search_by_name_desc,
      "m": self.search_by_maintainer,
      "b": self.search_by_base,
      "B": self.search_by_exact_base,
      "k": self.search_by_keywords,
      "c": self.search_by_comaintainer,
      "M": self.search_by_maintainer_comaintainer,
      "s": self.search_by_submitter
    }

    self.search_by_string = {
      "n": "Name only",
      "N": "Exact name",
      "nd": "Name, Description",
      "m": "Maintainer",
      "b": "Package Base",
      "B": "Exact Package Base",
      "k": "Keyword",
      "c": "Co-maintainer",
      "s": "Submitter"
    }

    self.sort_by = {
      "n": lambda e: e.name,
      "v": lambda e: e.votes,
      "p": lambda e: e.popularity,
      "m": lambda e: e.package_base.maintainer.username,
      "l": lambda e: e.modified_at,
    }

    self.sort_by_string = {
      "n": "Name",
      "v": "Votes",
      "p": "Popularity",
      "w": "Voted",
      "o": "Notify",
      "m": "Maintainer",
      "l": "Last Modified"
    }

  def search_by_name(self, keywords):
    pkgs = []
    for kwd in keywords:
      for pkg in Package.objects.filter(name__contains=kwd):
        pkgs.append(pkg)
    return pkgs

  def search_by_exact_name(self, keywords):
    pkgs = []
    for kwd in keywords:
      for pkg in Package.objects.filter(name=kwd):
        pkgs.append(pkg)
    return pkgs

  def search_by_name_desc(self, keywords):
    pkgs = []
    for kwd in keywords:
      for pkg in Package.objects.filter(
          Q(name__contains=kwd) | Q(description__contains=kwd)):
        pkgs.append(pkg)
    return pkgs

  def search_by_base(self, keywords):
    bases = []
    for kwd in keywords:
      for base in PackageBase.objects.filter(name__contains=kwd):
        bases.append(base)
    pkgs = []
    for base in bases:
      for pkg in base.packages.all():
        pkgs.append(pkg)
    return pkgs

  def search_by_exact_base(self, keywords):
    bases = []
    for kwd in keywords:
      for base in PackageBase.objects.filter(name=kwd):
        bases.append(base)
    pkgs = []
    for base in bases:
      for pkg in base.packages.all():
        pkgs.append(pkg)
    return pkgs

  def search_by_maintainer(self, keywords):
    bases = []
    for kwd in keywords:
      try: maintainer = AURUser.objects.get(username=kwd)
      except: continue
      for base in PackageBase.objects.filter(maintainer=maintainer):
        bases.append(base)
    pkgs = []
    for base in bases:
      for pkg in base.packages.all():
        pkgs.append(pkg)
    return pkgs

  def search_by_keywords(self, keywords):
    bases = []
    for kwd in keywords:
      try: pkg_keyword = PackageKeyword.objects.filter(keyword=kwd)
      except: continue
      bases.append(pkg_keyword.package_base)
    pkgs = []
    for base in bases:
      for pkg in base.packages.all():
        pkgs.append(pkg)
    return pkgs

  def search_by_comaintainer(self, keywords):
    bases = []
    for kwd in keywords:
      try: comaintainer = AURUser.objects.get(username=kwd)
      except: continue
      for base in comaintainer.comaintained.all():
        bases.append(base)
    pkgs = []
    for base in bases:
      for pkg in base.packages.all():
        pkgs.append(pkg)
    return pkgs

  def search_by_maintainer_comaintainer(self, keywords):
    bases = []
    for kwd in keywords:
      try: maintainer = AURUser.objects.get(username=kwd)
      except: continue
      for base in PackageBase.objects.filter(maintainer=maintainer):
        bases.append(base)
      try: comaintainer = AURUser.objects.get(username=kwd)
      except: continue
      for base in comaintainer.comaintained.all():
        bases.append(base)
    pkgs = []
    for base in bases:
      for pkg in base.packages.all():
        pkgs.append(base)
    return pkgs

  def search_by_submitter(self, keywords):
    bases = []
    for kwd in keywords:
      try: submitter = AURUser.objects.get(username=kwd)
      except: continue
      for base in PackageBase.objects.filter(submitter=submitter):
        bases.append(base)
    pkgs = []
    for base in bases:
      for pkg in base.packages.all():
        pkgs.append(pkg)
    return pkgs

  def get(self, request):

    # Keywords
    K = request.GET.get("K", None)
    results = []
    if not K:
      pkgbases = PackageBase.objects.all().order_by("-modified_at")
      for pkgbase in pkgbases:
        for pkg in pkgbase.packages.all():
          results.append(pkg)
    else:
      # Search By: default nd (name-desc)
      SeB = request.GET.get("SeB", "nd")
      ''' SeB values can be one of the following...
      n: Name only
      N: Exact name
      nd: Name or Desc
      m: Maintainer
      b: PackageBase
      B: Exact PackageBase
      k: Keywords (search by Keywords)
      c: Co-maintainer
      M: Maintainer OR Co-maintainer
      s: Submitter
      '''
      terms = []
      if ' ' in K:
        terms = K.split(' ')
      else:
        terms = [K]
      if SeB in self.search_by: 
        results = self.search_by[SeB](terms)

    sb = request.GET.get("SB", "n")
    if sb in self.sort_by:
      print("sort_by: %s" % str(self.sort_by[sb]))
      results = sorted(results, key=self.sort_by[sb])
    elif sb == "w": # Voted?
      if request.user.is_authenticated:
        user = AURUser.objects.get(user_ptr=request.user)
        results = sorted(results, key=lambda e: PackageVote.objects\
            .filter(package_base=e.package_base).filter(user=user).exists())
    elif sb == "o": # Notify?
      if request.user.is_authenticated:
        user = AURUser.objects.get(user_ptr=request.user)
        results = sorted(results, key=lambda e: PackageNotification.objects\
            .filter(package_base=e.package_base).filter(user=user).exists())

    so = request.GET.get("SO", "a")
    if so == "d":
      results.reverse()

    try:
      o = int(request.GET.get("O", 0))
    except ValueError as exc:
      o = 0

    try:
      pp = int(request.GET.get("PP", 50))
    except ValueError as exc:
      pp = 50

    n = len(results)
    pages = int(n / pp) + 1

    # Cut from o (o = start) until o + pp (o = start, pp = pagination)
    results = results[o:o + pp]

    current_page = int(pp / o) if o != 0 else 1

    pkg_count = Package.objects.count()
    return aur_render(request, "packages/index.html", {
      "sort_by_options": self.sort_by_string,
      "search_by_options": self.search_by_string,
      "results": results,
      "resultcount": n,
      "pages": pages,
      "current_page": current_page,
      "package_count": pkg_count,
    })


