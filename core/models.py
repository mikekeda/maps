from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify
from django.core.cache import cache
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from djgeojson.fields import MultiPolygonField
from mptt.models import MPTTModel, TreeForeignKey

from core.widgets import ColorWidget


def get_unique_slug(cls, title: str) -> str:
    """Helper function to get unique slug."""
    unique_slug = slug = slugify(title)
    num = 1
    while cls.objects.filter(slug=unique_slug).exists():
        unique_slug = f"{slug}-{num}"
        num += 1
    return unique_slug


class ColorField(models.CharField):
    """Color field."""

    def formfield(self, **kwargs):
        kwargs["widget"] = ColorWidget
        return super().formfield(**kwargs)


class Category(models.Model):
    """Category model."""

    title = models.CharField(max_length=60, unique=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(editable=False)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.pk:
            self.slug = slugify(self.title)

        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.title


class Polygon(MPTTModel):
    """Polygon model."""

    title = models.CharField(max_length=256)
    geom = MultiPolygonField()
    parent = TreeForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        db_index=True,
        on_delete=models.CASCADE,
    )

    class MPTTMeta:
        order_insertion_by = ["title"]

    def __str__(self):
        return self.title

    def geojson(self, data: int = 0, path: str = "") -> str:
        return (
            "{{"
            '"type": "Feature", '
            '"id": "{}", '
            '"properties": {{'
            '"name": "{}", "density": {}, "path": "{}"'
            "}}, "
            '"geometry": {}'
            "}}, ".format(self.pk, self.title, data, path, self.geom)
        )


class Map(models.Model):
    """Map model."""

    title = models.CharField(
        max_length=256, verbose_name=_("title"), help_text="Map title."
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("description"),
        help_text="Map description.",
    )
    unit = models.CharField(
        blank=True,
        max_length=64,
        verbose_name=_("unit"),
        help_text="The unit that will be used for the map.",
    )
    date_of_information = models.DateField(
        default=timezone.now,
        blank=True,
        verbose_name=_("date"),
        help_text="An year or date when the information was measured.",
    )
    region = models.ForeignKey(
        Polygon,
        blank=True,
        null=True,
        verbose_name=_("region"),
        related_name="maps",
        on_delete=models.CASCADE,
    )
    categories = models.ManyToManyField(
        Category, blank=True, verbose_name=_("categories"), related_name="maps"
    )
    grades = models.PositiveSmallIntegerField(
        default=8,
        verbose_name=_("grades"),
        help_text="How many grades you would like to have",
    )
    logarithmic_scale = models.BooleanField(
        default=False,
        verbose_name=_("logarithmic scale"),
        help_text="If True - logarithmic scale will be used.",
    )
    end_color = ColorField(
        max_length=6,
        default="ffeda0",
        verbose_name=_("end color"),
        help_text="The color to fill regions with the lowest value.",
    )
    start_color = ColorField(
        max_length=6,
        default="bd0026",
        verbose_name=_("start color"),
        help_text="The color to fill regions with the highest value.",
    )
    opacity = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.7,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        verbose_name=_("opacity"),
        help_text="The opacity for regions.",
    )
    changed = models.DateTimeField(
        auto_now=True,
        verbose_name=_("changed"),
        help_text="Time when map was changed last time.",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="maps",
        verbose_name=_("user"),
        help_text="Map owner.",
        on_delete=models.CASCADE,
    )
    slug = models.SlugField(
        editable=False,
        verbose_name=_("slug"),
        help_text="The slug that will be user for urls.",
    )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.pk:
            self.slug = get_unique_slug(type(self), self.title)

        cache.delete_pattern("*:map_view:" + self.slug)
        cache.delete_pattern("*:maps")
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.title


class MapElement(models.Model):
    """MapElement model."""

    map = models.ForeignKey(Map, related_name="elements", on_delete=models.CASCADE)
    polygon = models.ForeignKey(
        Polygon, related_name="polygon_elements", on_delete=models.CASCADE
    )
    data = models.FloatField()

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        cache.delete_pattern("*:map_view:" + self.map.slug)
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.polygon.title

    def geojson(self) -> str:
        return (
            "{{"
            '"type": "Feature", '
            '"id": "{}", '
            '"properties": {{"name": "{}", "density": {}}}, '
            '"geometry": {}'
            "}}, ".format(self.pk, self.polygon.title, self.data, self.polygon.geom)
        )


class Chart(models.Model):
    """Chart model."""

    title = models.CharField(max_length=256)
    description = models.TextField(
        blank=True, null=True, help_text="Chart description."
    )
    maps = models.ManyToManyField(Map, related_name="charts")
    changed = models.DateTimeField(
        auto_now=True,
        verbose_name=_("changed"),
        help_text="Time when chart was changed last time.",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="charts",
        help_text="Map owner.",
        on_delete=models.CASCADE,
    )
    slug = models.SlugField(
        editable=False, help_text="The slug that will be user for urls."
    )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.pk:
            self.slug = get_unique_slug(type(self), self.title)
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.title


class Plot(models.Model):
    """Plot model."""

    slug = models.CharField(max_length=256)
    data = models.JSONField(default=dict, blank=True)
    added = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="plots",
        verbose_name=_("user"),
        help_text="Plot owner.",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.slug}-{self.added}"
