#!/usr/bin/env python3
from django.urls import path
from django.views.generic.base import RedirectView
from .views import *

urlpatterns = [

  # Clarify: package requests
  # path("requests/", RequestsView.as_view(), name="requests"),

  # path("pkgbase/<pkgname>/edit/",

  # path("pkgbase/<pkgname>/delete/",
  # path("pkgbase/<pkgname>/request/",
  # path("pkgbase/<pkgname>/merge/",
  # path("pkgbase/<pkgname>/comaintainers/",
  # path("pkgbase/<pkgname>/flag/",
  # path("pkgbase/<pkgname>/",

  path("packages/<pkgname>/", PackageView.as_view(), name="package"),
  path("packages/", PackagesView.as_view(), name="packages"),
]


