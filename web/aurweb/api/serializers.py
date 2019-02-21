from packages.models import Package
from rest_framework import serializers
Serializer = serializers.Serializer

class PackageSerializer1(Serializer):
  class Meta:
    model = Package

class PackageSerializer2(Serializer):
  class Meta:
    model = Package

class PackageSerializer4(Serializer):
  class Meta:
    model = Package

def get_package_serializer(version):
  if version < 2:
    return PackageSerializer1
  elif version <= 3:
    return PackageSerializer2
  elif version >= 4:
    return PackageSerializer4
  raise ValueError("get_package_serializer(version) " +
      "given version out of bounds [1, 6]: `%d`." % version)

# End of serializers.py
