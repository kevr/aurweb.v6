from django.shortcuts import render
from django.views import View

from helpers.render import aur_render

class PackagesView(View):
  def get(self, request):
    return aur_render(request, "packages/index.html")


