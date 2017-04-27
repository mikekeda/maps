from djgeojson.fields import PolygonField
from django.db import models


class Polygon(models.Model):
    title = models.CharField(max_length=256)
    geom = PolygonField()

    def __unicode__(self):
        return self.title
