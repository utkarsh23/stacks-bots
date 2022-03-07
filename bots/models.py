from django.db import models

class StacksInfo(models.Model):
    bns_sync_height = models.BigIntegerField()
