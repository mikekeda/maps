from django.contrib.postgres.fields import JSONField
from django.db import models


class Data(models.Model):
    """ Data model. """
    slug = models.CharField(max_length=256)
    data = JSONField(default=dict, blank=True)
    added = models.DateTimeField(auto_now=True)
