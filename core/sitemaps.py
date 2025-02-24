from django.contrib import sitemaps
from django.urls import reverse

from core.models import Map, Chart


class MapsSitemap(sitemaps.Sitemap):
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        return Map.objects.all().order_by("-id")

    def location(self, item):
        return reverse("core:map", kwargs={"slug": item.slug})

    @staticmethod
    def lastmod(item):
        return item.changed


class ChartsSitemap(sitemaps.Sitemap):
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        return Chart.objects.all().order_by("-id")

    def location(self, item):
        return reverse("core:chart", kwargs={"slug": item.slug})

    @staticmethod
    def lastmod(item):
        return item.changed


class StaticPagesSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return ["core:maps", "core:charts", "core:about"]

    def location(self, item):
        return reverse(item)
