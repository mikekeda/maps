from djgeojson.fields import PolygonField
from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify
from django.core.cache import cache
from django.core.validators import MaxValueValidator, MinValueValidator

from .widgets import ColorWidget


class ColorField(models.CharField):
    def __init__(self, *args, **kwargs):
        super(ColorField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['widget'] = ColorWidget
        return super(ColorField, self).formfield(**kwargs)


class Map(models.Model):
    title = models.CharField(
        max_length=256,
        help_text="Map title.")
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Map description.")
    unit = models.CharField(
        max_length=64,
        help_text="The unit that will be used for the map.")
    grades = models.PositiveSmallIntegerField(
        default=8,
        help_text="How many grades you would like to have")
    end_color = ColorField(
        max_length=6,
        default='ffeda0',
        help_text="The color to fill regions with the lowest value.")
    start_color = ColorField(
        max_length=6,
        default='bd0026',
        help_text="The color to fill regions with the highest value.")
    opacity = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.7,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="The opacity for regions.")
    changed = models.DateTimeField(
        auto_now=True,
        help_text="Time when map was changed last time.")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='maps',
        help_text="Map owner.")
    slug = models.SlugField(
        editable=False,
        help_text="The slug that will be user for urls.")

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
