from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from django.contrib.auth import login, logout, get_user_model
from helpers.render import aur_render
from users.models import AURUser, AURAccountType

User = get_user_model()

class LoginView(View):
  def get(self, request):
    return aur_render(request, "users/login.html")

  def post(self, request):
    username = request.POST.get("user", None)
    passwd = request.POST.get("passwd", None)
    
    errors = []

    if not username or not passwd:
      errors.append("Bad username or password.")
      return self.render(request, errors)

    auruser = AURUser.objects.get(username=username)

    if not auruser.check_password(passwd):
      errors.append("Bad username or password.")
      return self.render(request, errors)

    login(request, auruser)

    return HttpResponseRedirect('/')

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

