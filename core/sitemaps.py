from django.contrib import sitemaps
from django.urls import reverse

from core.models import Map, Chart


class MapsSitemap(sitemaps.Sitemap):
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        return Map.objects.all().order_by("-id")

    def location(self, obj):
        return reverse("core:map", kwargs={"slug": obj.slug})

    @staticmethod
    def lastmod(obj):
        return obj.changed


class ChartsSitemap(sitemaps.Sitemap):
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        return Chart.objects.all().order_by("-id")

    def location(self, obj):
        return reverse("core:chart", kwargs={"slug": obj.slug})

    @staticmethod
    def lastmod(obj):
        return obj.changed


class StaticPagesSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return ["core:maps", "core:charts", "core:about"]

    def location(self, obj):
        return reverse(obj)


class CovidMapsSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "hourly"

    def items(self):
        return (
            ("covid_key", "cases"),
            ("covid_key", "deaths"),
            ("covid_key", "total_recovered"),
            ("covid_key", "active_cases"),
            ("covid_key", "new_deaths"),
            ("covid_key", "new_cases"),
            ("covid_key", "serious_critical"),
        )

    def location(self, obj):
        return reverse(obj[0], kwargs={"key": obj[1]})


class CovidChartsSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "hourly"

    def items(self):
        # TODO[Mike] Make it automatic.
        return (
            ("core:plot_key", "covid", "cases"),
            ("core:plot_key", "covid", "deaths"),
            ("core:plot_key", "covid", "total_recovered"),
            ("core:plot_key", "covid", "active_cases"),
            ("core:plot_key", "covid", "new_deaths"),
            ("core:plot_key", "covid", "new_cases"),
            ("core:plot_key", "covid", "serious_critical"),
        )

    def location(self, obj):
        return reverse(obj[0], kwargs={"slug": obj[1], "key": obj[2]})
