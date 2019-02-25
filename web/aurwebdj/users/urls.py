#!/usr/bin/env python3
from django.urls import path
from .views import *

urlpatterns = [
  path("login/", LoginView.as_view(), name="user_login"),
  path("logout/", LogoutView.as_view(), name="user_logout"),
  path("accounts/", AccountsView.as_view(), name="user_search"),
  path("update/", UpdateView.as_view(), name="update"),
  # path("account/<user>/comments/", UserCommentsView.as_view(), name="user_comments"),
  # account/<user>/update/ may be removed in favor of GET+POST account/<user>/edit/
  # path("account/<user>/update/" UserUpdateView.as_view(), name="user_update"),
  path("account/<username>/delete/", DeleteAccountView.as_view(), name="user_delete"),
  path("account/<username>/edit/", EditAccountView.as_view(), name="user_edit"),
  path("account/<username>/", AccountView.as_view(), name="user"),
  # path("tu/", TrustedUserView.as_view(), name="tu"),
]


