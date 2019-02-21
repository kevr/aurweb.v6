from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
User = get_user_model()

class AURAccountType(models.Model):
  name = models.CharField(max_length=32)

class AURUser(User):
  account_type = models.ForeignKey(AURAccountType,
      on_delete=models.CASCADE, related_name="users", primary_key=False)

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

  registered_at = models.DateTimeField(default=timezone.now)

  comment_notify = models.BooleanField(default=True)
  update_notify = models.BooleanField(default=False)
  ownership_notify = models.BooleanField(default=True)

class Ban(models.Model):
  ip_address = models.CharField(max_length=45)
  ban_timestamp = models.DateTimeField(default=timezone.now)

# End of users.models
