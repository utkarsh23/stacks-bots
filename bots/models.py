import uuid

from django.db import models

class StacksInfo(models.Model):
    bns_sync_height = models.BigIntegerField()

class Leaderboard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    twitter_id = models.CharField(max_length=100, null=True, blank=True)
    twitter_name = models.CharField(max_length=100, null=True, blank=True)
    twitter_username = models.CharField(max_length=100, null=True, blank=True)
    twitter_follower_acount = models.BigIntegerField(null=True, blank=True)
    is_updated = models.BooleanField(default=False)

    def __str__(self):
        return self.twitter_username if self.twitter_username else str(self.id)

class Mentions(models.Model):
    updated_at = models.DateTimeField(editable=True)

    class Meta:
        verbose_name_plural = "Mentions"
