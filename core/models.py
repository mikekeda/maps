from djgeojson.fields import PolygonField
from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify


class Map(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=64)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='maps')
    slug = models.SlugField(editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)

        super(Map, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Country(models.Model):
    filename = models.CharField(max_length=256)

    def __str__(self):
        return self.filename


class Polygon(models.Model):
    title = models.CharField(max_length=256)
    country = models.ForeignKey(Country, related_name='polygons')
    geom = PolygonField()

    def __str__(self):
        return self.title


class MapElement(models.Model):
    map = models.ForeignKey(Map, related_name='elements')
    polygon = models.ForeignKey(Polygon, related_name='elements')
    data = models.FloatField()

    def __str__(self):
        return u'%s: %s: %s' % (
            self.map.title,
            self.polygon.title,
            self.data,
        )
