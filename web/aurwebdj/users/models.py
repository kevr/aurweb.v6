from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django_unixdatetimefield import UnixDateTimeField
User = get_user_model()

class AURAccountType(models.Model):
  name = models.CharField(max_length=32)

class AURUser(User):
  uid = models.IntegerField(default=1, primary_key=False)

  account_type = models.ForeignKey(AURAccountType,
      on_delete=models.CASCADE, related_name="users", primary_key=False)

  realname = models.CharField(max_length=255, default="")
  suspended = models.BooleanField(default=False)
  hide_email = models.BooleanField(default=False)

  reset_key = models.CharField(max_length=32, default="")

  lang_preference = models.CharField(max_length=6, default="en")
  
  tz = models.CharField(max_length=32, default="UTC")
  homepage = models.TextField()
  irc_nick = models.CharField(max_length=32, default="")
  pgp_key = models.CharField(max_length=40, null=True, blank=True)
  
  last_login_ip_address = models.CharField(max_length=45,
      null=True, blank=True)
  last_ssh_login = models.DateTimeField(null=True, blank=True)
  last_ssh_login_ip_address = models.CharField(max_length=45,
      null=True, blank=True)

  inactivity_ts = models.IntegerField(default=0)

  registered_at = models.DateTimeField(null=True, blank=True)

  comment_notify = models.BooleanField(default=True)
  update_notify = models.BooleanField(default=False)
  ownership_notify = models.BooleanField(default=True)

  indexes = [
    models.Index(fields=['uid',])
  ]

  # Custom autoincrement on uid
  def save(self, *args, **kwargs):
    if self._state.adding:
      last_id = AURUser.objects.all().aggregate(largest=models.Max('uid'))['largest']
      if last_id is not None:
        self.uid = last_id + 1
    super().save(*args, **kwargs)

  def voted(self, pkgbase):
    return PackageVote.objects.\
        filter(user=self).\
        filter(package_base=pkgbase).\
        exists()

class Ban(models.Model):
  ip_address = models.CharField(max_length=45, primary_key=True)
  banned_at = models.DateTimeField(default=timezone.now)

class APIRateLimit(models.Model):
  ip_address = models.CharField(max_length=45)
  requests = models.IntegerField(0)
  window_start = models.IntegerField(0)

  indexes = [
    models.Index(fields=['window_start',])
  ]

class Term(models.Model):
  description = models.CharField(max_length=255)
  url = models.CharField(max_length=8000)
  revision = models.IntegerField(default=1)

class AcceptedTerm(models.Model):
  user = models.ForeignKey(AURUser, on_delete=models.CASCADE,
      related_name="accepted_terms")
  term = models.ForeignKey(Term, on_delete=models.CASCADE,
      related_name="accepted")
  revision = models.IntegerField(default=0)

class SSHPubKey(models.Model):
  user = models.ForeignKey(AURUser, on_delete=models.CASCADE,
      related_name="ssh_keys", primary_key=False)
  fingerprint = models.CharField(max_length=44, primary_key=True)
  pub_key = models.CharField(max_length=4096)

# End of users.models
