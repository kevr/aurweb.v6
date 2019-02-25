from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import HttpResponseRedirect
from django.contrib.auth import login, logout, get_user_model
from django.conf import settings
from django.utils import translation

from helpers.render import aur_render
from users.models import AURUser, AURAccountType

User = get_user_model()

class AccountView(View):
  def get(self, request, username):
    auruser = get_object_or_404(AURUser, username=username)
    return aur_render(request, "users/account.html", {
      "user": auruser
    })

class EditAccountView(View):
  def get(self, request, username):
    auruser = get_object_or_404(AURUser, username=username)
    current_auruser = get_object_or_404(AURUser, user_ptr=request.user)
    return aur_render(request, "users/edit.html", {
      "user": auruser,
      "current_user": current_auruser
    })

class DeleteAccountView(View):
  def get(self, request, username):
    return aur_render(request, "users/delete.html")

class UpdateView(View):
  def post(self, request):
    _next = None
    if "next" in request.POST:
      _next = request.POST["next"]

    if "setlang" in request.POST:
      if request.user.is_authenticated:
        auruser = AURUser.objects.get(user_ptr=request.user)
        auruser.lang_preference = request.POST["setlang"]
        auruser.save()
      response = HttpResponseRedirect(_next if _next else "/")
      request.session[translation.LANGUAGE_SESSION_KEY] = request.POST["setlang"]
      response.set_cookie(settings.LANGUAGE_COOKIE_NAME, request.POST["setlang"])
      return response

    return HttpResponseRedirect(_next if _next else "/")

class LoginView(View):
  def get(self, request):
    return aur_render(request, "users/login.html")

  def post(self, request):
    username = request.POST.get("user", None)
    passwd = request.POST.get("passwd", None)
    
    errors = []

    if not username or not passwd:
      return self.render(request)

    if not AURUser.objects.filter(username=username).exists():
      errors.append("Bad username or password.")
      return self.render(request, errors)

    auruser = AURUser.objects.get(username=username)

    if not auruser.check_password(passwd):
      errors.append("Bad username or password.")
      return self.render(request, errors)

    login(request, auruser)

    return HttpResponseRedirect("/")

  def render(self, request, errors=None):
    if errors:
      return aur_render(request, "users/login.html", { "errors": errors })
    return aur_render(request, "users/login.html")

class LogoutView(View):
  def get(self, request):
    if request.user.is_authenticated:
      logout(request)
    return HttpResponseRedirect("/")

# Create your views here.
class UserSearchView(View):
  def get(self, request):
    return render(request, "users/index.html")

