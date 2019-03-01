from django.shortcuts import render
from django.views import View
from django.db.models import Q, F
from django.core.paginator import Paginator
from collections import OrderedDict

from helpers.render import aur_render
from packages.models import *

'''
@class PackagesView
@brief Main search page at /packages/.
'''
class PackagesView(View):
  search_by_string = {
    "nd": "Name, Description",
    "n": "Name only",
    "N": "Exact name",
    "m": "Maintainer",
    "M": "Maintainer, Co-Maintainer",
    "b": "Package Base",
    "B": "Exact Package Base",
    "k": "Keyword",
    "c": "Co-maintainer",
    "s": "Submitter"
  }

  sort_by_string = {
    "n": "Name",
    "v": "Votes",
    "p": "Popularity",
    "w": "Voted",
    "o": "Notify",
    "m": "Maintainer",
    "l": "Last Modified"
  }

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

    # key values for sorted(...); we also support 'w' and 'o',
    # however, they require further model introspection later.
    self.sort_by = {
      "n": lambda e: e.name,
      "v": lambda e: e.package_base.num_votes,
      "p": lambda e: e.package_base.popularity,
      "m": lambda e: e.package_base.maintainer.username if e.package_base.maintainer else '',
      "l": lambda e: e.package_base.modified_at,
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
      bases = list(PackageKeyword.objects.filter(keyword=kwd))
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
      bases = list(comaintainer.comaintained.all())
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
      bases = list(PackageBase.objects.filter(maintainer=maintainer))
      try: comaintainer = AURUser.objects.get(username=kwd)
      except: continue
      bases += list(comaintainer.comaintained.all())
    pkgs = []
    for base in bases:
      for pkg in base.packages.all():
        pkgs.append(pkg)
    return pkgs

  def search_by_submitter(self, keywords):
    bases = []
    for kwd in keywords:
      try: submitter = AURUser.objects.get(username=kwd)
      except: continue
      bases = PackageBase.objects.filter(submitter=submitter)
    pkgs = []
    for base in bases:
      for pkg in base.packages.all():
        pkgs.append(pkg)
    return pkgs

  def get(self, request):

    try:
      o = int(request.GET.get("O", 0))
    except ValueError as exc:
      o = 0

    try:
      pp = int(request.GET.get("PP", 50))
    except ValueError as exc:
      pp = 50

    # Sane defaults
    SeB = "nd"
    SB = "n"
    SO = "a"

    # Keywords
    K = request.GET.get("K", None)
    results = []
    if not K:
      # 50 -> default PP
      results = sorted(Package.objects.all(),
          key=lambda k: k.package_base.modified_at, reverse=True)
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

    SB = request.GET.get("SB", "n")
    if SB in self.sort_by:
      results = sorted(results, key=self.sort_by[SB])
    elif SB == "w": # Voted?
      if request.user.is_authenticated:
        user = AURUser.objects.get(user_ptr=request.user)
        results = sorted(results, key=lambda e: int(PackageVote.objects\
            .filter(package_base=e.package_base).filter(user=user).exists()),
          reverse=True)
    elif SB == "o": # Notify?
      if request.user.is_authenticated:
        user = AURUser.objects.get(user_ptr=request.user)
        results = sorted(results, key=lambda e: int(PackageNotification.objects\
            .filter(package_base=e.package_base).filter(user=user).exists()),
            reverse=True)

    SO = request.GET.get("SO", "a")
    if SO == "d":
      results.reverse()

    n = len(results)

    paginator = Paginator(results, pp)

    x = int(o / pp) # current page number
    if x == 0:
      x = 1
    print("Page: %d" % x)
    page = paginator.get_page(x)
    print("Page #: %d" % page.number)

    results = results[o:o + pp]

    cp, nav_lhs = page, []
    for i in range(min(5, max(5, paginator.num_pages - page.number - 1))):
      if cp.number == 1:
        break
      print("cp.previous_page_number: %d" % cp.previous_page_number())
      cp = paginator.get_page(cp.previous_page_number())
      print("Appending %d to lhs" % cp.number)
      nav_lhs.append(cp.number)
    nav_lhs.reverse()

    cp, nav_rhs = page, []
    for i in range(page.number + 1, min(page.number + 6, paginator.num_pages + 1)):
      if cp.number == paginator.num_pages:
        break
      print("cp.next_page_number: %d" % cp.next_page_number())
      cp = paginator.get_page(cp.next_page_number())
      print("Appending %d to rhs" % cp.number)
      nav_rhs.append(cp.number)

    qs = "?O=%s&SeB=%s&K=%s&SB=%s&SO=%s&PP=%s" % (
      o, SeB, K if K else '', SB, SO, pp
    )

    return aur_render(request, "packages/index.html", {
      "sort_by_options": self.sort_by_string,
      "search_by_options": self.search_by_string,
      "page": page,
      "package_count": n,
      "pp": pp,
      "nav_lhs": nav_lhs,
      "nav_rhs": nav_rhs,
      "qs": qs
    })

'''
@class PackageView
@brief View a single package's details.
'''
class PackageView(View):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def get(self, request, pkgname):
    pkg = Package.objects.filter(name=pkgname)
    if not pkg.exists():
      return aur_render(request, "404.html")
    return aur_render(request, "packages/package.html", {
      "pkg": pkg[0],
      "search_by_options": PackagesView.search_by_string,
      "sort_by_options": PackagesView.sort_by_string,
    })

