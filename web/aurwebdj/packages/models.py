from django.db import models
from datetime import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
from users.models import AURUser, Ban

class PackageBase(models.Model):
  num_votes = models.IntegerField(default=0)
  name = models.CharField(max_length=255)
  popularity = models.FloatField(default=0.0)

  submitted_at = models.DateTimeField(default=timezone.now)
  modified_at = models.DateTimeField(default=timezone.now)

  out_of_date_at = models.DateTimeField(null=True, blank=True)
  flagger = models.ForeignKey(AURUser, on_delete=models.DO_NOTHING,
      primary_key=False, null=True, blank=True, related_name="flagged")
  flagger_comment = models.CharField(max_length=255, default="")

  maintainer = models.ForeignKey(AURUser, on_delete=models.DO_NOTHING,
      primary_key=False, null=True, blank=True, related_name="maintained")
  packager = models.ForeignKey(AURUser, on_delete=models.DO_NOTHING,
      primary_key=False, null=True, blank=True, related_name="pkgbases")
  submitter = models.ForeignKey(AURUser, on_delete=models.DO_NOTHING,
      primary_key=False, null=True, blank=True, related_name="submitted")

# An AUR package
class Package(models.Model):
  package_base = models.ForeignKey(PackageBase, on_delete=models.CASCADE,
      primary_key=False, unique=False, related_name="packages")

  name = models.CharField(max_length=255)
  version = models.CharField(max_length=255)
  description = models.CharField(max_length=255, default="")
  url = models.CharField(max_length=255, null=True, blank=True)

class License(models.Model):
  name = models.CharField(max_length=255, unique=True)

class PackageLicense(models.Model):
  license = models.ForeignKey(License, on_delete=models.DO_NOTHING,
      related_name="package_licenses")
  package = models.ForeignKey(Package, on_delete=models.CASCADE,
      related_name="package_license", primary_key=False)

class DependencyType(models.Model):
  name = models.CharField(max_length=32)

class PackageDependency(models.Model):
  package = models.ForeignKey(Package, on_delete=models.CASCADE,
      related_name="deps")
  dep_type = models.ForeignKey(DependencyType, on_delete=models.DO_NOTHING,
      primary_key=False,
      related_name="package_deps")

  name = models.CharField(max_length=255)
  desc = models.CharField(max_length=255, default="")
  condition = models.CharField(max_length=255, default="")
  arch = models.CharField(max_length=255, null=True, blank=True)

class PackageSource(models.Model):
  package = models.ForeignKey(Package, on_delete=models.CASCADE,
      related_name="sources")
  source = models.CharField(max_length=8000, default="/dev/null")
  arch = models.CharField(max_length=255, null=True, blank=True)

class PackageVote(models.Model):
  user = models.ForeignKey(AURUser, on_delete=models.CASCADE,
      related_name="votes")
  package_base = models.ForeignKey(PackageBase, on_delete=models.CASCADE,
      related_name="votes", primary_key=False)
  created_at = models.DateTimeField(default=timezone.now)

class PackageComments(models.Model):
  package_base = models.ForeignKey(PackageBase, on_delete=models.CASCADE,
      related_name="comments", primary_key=False)
  user = models.ForeignKey(AURUser, on_delete=models.CASCADE,
      related_name="comments", primary_key=False)
  comment = models.TextField()
  rendered_comment = models.TextField()
  commented_at = models.DateTimeField(default=timezone.now)
  edited_at = models.DateTimeField(null=True, blank=True)
  edited_user = models.ForeignKey(AURUser, on_delete=models.DO_NOTHING,
      null=True, blank=True, primary_key=False,
      related_name="edited_comments")

  deleted_at = models.DateTimeField(null=True, blank=True)
  deleted_user = models.ForeignKey(AURUser, on_delete=models.DO_NOTHING,
      null=True, blank=True, primary_key=False,
      related_name="deleted_comments")

  pinned_at = models.DateTimeField(null=True, blank=True)

class Group(models.Model):
  name = models.CharField(max_length=255)

class PackageGroup(models.Model):
  package = models.ForeignKey(Package, on_delete=models.CASCADE,
      related_name="package_groups")
  group = models.ForeignKey(Group, on_delete=models.CASCADE,
      related_name="package_groups", primary_key=False)

class PackageBlacklist(models.Model):
  name = models.CharField(max_length=64)

class PackageComaintainer(models.Model):
  user = models.ForeignKey(AURUser, on_delete=models.CASCADE,
      related_name="comaintained")
  package_base = models.ForeignKey(PackageBase, on_delete=models.CASCADE,
      related_name="comaintainers", primary_key=False)
  priority = models.IntegerField(null=True, blank=True)

class PackageKeyword(models.Model):
  package_base = models.ForeignKey(PackageBase, on_delete=models.CASCADE,
      related_name="keywords")
  keyword = models.CharField(max_length=255)

class PackageNotification(models.Model):
  package_base = models.ForeignKey(PackageBase, on_delete=models.CASCADE,
      related_name="notifications")
  user = models.ForeignKey(AURUser, on_delete=models.CASCADE,
      related_name="package_notifications")

class RequestType(models.Model):
  name = models.CharField(max_length=32)

class PackageRequest(models.Model):
  req_type = models.ForeignKey(RequestType, on_delete=models.CASCADE,
      related_name="package_requests", primary_key=False)
  package_base = models.ForeignKey(PackageBase, on_delete=models.CASCADE,
      related_name="requests", primary_key=False)

  package_name = models.CharField(max_length=255)
  merged_name = models.CharField(max_length=255)

  user = models.ForeignKey(AURUser, on_delete=models.CASCADE,
      related_name="package_requests", primary_key=False)

  comments = models.TextField()
  closure_comment = models.TextField()

  requested_at = models.DateTimeField(default=timezone.now)
  status = models.IntegerField(default=0)

class RelationType(models.Model):
  name = models.CharField(max_length=32)

class PackageRelation(models.Model):
  package = models.ForeignKey(Package, on_delete=models.CASCADE,
      related_name="relations")
  rel_type = models.ForeignKey(RelationType, on_delete=models.CASCADE,
      related_name="package_relations", primary_key=False)

  name = models.CharField(max_length=255)
  condition = models.CharField(max_length=255, null=True, blank=True)
  arch = models.CharField(max_length=255, null=True, blank=True)

class OfficialProvider(models.Model):
  package = models.ForeignKey(Package, on_delete=models.CASCADE,
      related_name="official_providers", primary_key=False)

  @property
  def name(self):
    return self.package.name

  repo = models.CharField(max_length=64)
  provides = models.CharField(max_length=64)

'''
Receive a list of tu_votes related to this VoteInfo:
  self.tu_votes.get(pk=self).user.id  
'''
class TUVoteInfo(models.Model):
  agenda = models.TextField()
  user = models.CharField(max_length=32)
  submitted_at = models.DateTimeField()
  end_at = models.DateTimeField()

  quorum = models.DecimalField(max_digits=2, decimal_places=2, default=0)

  yes = models.IntegerField(default=0)
  no = models.IntegerField(default=0)
  abstrain = models.IntegerField(default=0)
  active_tus = models.IntegerField(default=0)

  submitter = models.ForeignKey(AURUser, on_delete=models.CASCADE,
      related_name="tu_voteinfos", null=True)

class TUVote(models.Model):
  info = models.ForeignKey(TUVoteInfo, on_delete=models.CASCADE,
      related_name="tu_votes")
  user = models.ForeignKey(AURUser, on_delete=models.CASCADE,
      related_name="tu_votes")


