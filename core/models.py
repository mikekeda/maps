from djgeojson.fields import PolygonField
from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify
from django.core.cache import cache


class Map(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=64)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='maps')
    slug = models.SlugField(editable=False)

    def _get_unique_slug(self):
        unique_slug = slug = slugify(self.title)
        num = 1
        while Map.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = self._get_unique_slug()

        cache.delete_pattern('*:map_view:' + self.slug)
        cache.delete_pattern('*:homepage')
        super(Map, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Region(models.Model):
    filename = models.CharField(max_length=256)

    def __str__(self):
        return self.filename


class Polygon(models.Model):
    title = models.CharField(max_length=256)
    region = models.ForeignKey(Region, related_name='polygons')
    geom = PolygonField()

    def __str__(self):
        return self.title


class MapElement(models.Model):
    map = models.ForeignKey(Map, related_name='elements')
    polygon = models.ForeignKey(Polygon, related_name='elements')
    data = models.FloatField()

    def save(self, *args, **kwargs):
        cache.delete_pattern('*:map_view:' + self.map.slug)
        super(MapElement, self).save(*args, **kwargs)

    def __str__(self):
        return u'%s: %s: %s' % (
            self.map.title,
            self.polygon.title,
            self.data,
        )
