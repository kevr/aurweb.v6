from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import json
from .serializers import get_package_serializer
from packages.models import *

''' Helpers '''
def json_response(data):
  return Response(data, content_type='application/json')

def json_error(message):
  return json_response({ "error": message })

''' API Views '''

'''
  Route: /rpc
  Query parameters:
    `v`: Version number (1-6)
    `type`: Type of query (see self.exposed_methods)
    `by`: v5 single by search type (see self.exposed_fields)
    `by[]`: v6 multiple by[] search
    `arg`: single argument search/info criteria
    `arg[]`: array of arguments for search/info criteria
'''
class RPCView(APIView):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.exposed_methods = {
      "search": self.search,
      "info": self.info,
      "multiinfo": self.multiinfo,
      "msearch": self.msearch,
      "suggest": self.suggest,
      "suggest-pkgbase": self.suggest_pkgbase,
      "get-comment-form": self.get_comment_form,
    }

    self.exposed_fields = {
      "name", "name-desc", "maintainer", "provides",
      "depends", "makedepends", "checkdepends", "optdepends",
    }

    self.serializer = get_package_serializer(1)

  def search(self, by_types, args):
    pkgs = Package.objects.all()
    Serializer = get_package_serializer(6)
    data = []
    for pkg in pkgs:
      data.append(Serializer(pkg).data)
    return data

  def info(self, by_types, args):
    return []

  def multiinfo(self, by_types, args):
    return []

  def msearch(self, by_types, args):
    return []

  def suggest(self, by_types, args):
    return []

  def suggest_pkgbase(self, by_types, args):
    return []

  def get_comment_form(self, by_types, args):
    return []

  def process(self, data):
    response_data = dict() # Dict used for json output on success

    v = data.get("v", None)
    if not v:
      return json_error("No `v` version argument provided.")

    v = int(v)

    if v < 1 or v > 6:
      return json_error("Invalid version provided: `%d`" % v)

    response_data['version'] = v
    self.serializer = get_package_serializer(v)

    stype = data.get("type", None)
    if not stype:
      return json_error("No `type` argument provided.")
    if not stype in self.exposed_methods:
      return json_error("Invalid type provided: `%s`." % stype)

    response_data['type'] = stype

    by = data.getlist("by[]")
    if not by:
      # We default to name-desc if no by is provided
      by = [data.get("by", "name-desc")]

    for term in by:
      if not term in self.exposed_fields:
        return json_error("Invalid `by` field value: `%s`." % term)

    args = data.getlist("arg[]")
    if not args:
      args = data.get("arg", None)
      if args: args = [args]

    if not args:
      return json_error("No `arg` argument provided.")

    response_data['resultcount'] = 0
    response_data['results'] = self.exposed_methods[stype](by, args)

    if response_data['results'] is not None:
      response_data['resultcount'] = len(response_data['results'])

    return json_response(response_data)

  ''' /rpc/ HTTP methods '''
  def get(self, request):
    return self.process(request.GET)

  def post(self, request):
    return self.process(request.POST)

# Create your views here.
