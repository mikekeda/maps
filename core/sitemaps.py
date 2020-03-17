from django.contrib import sitemaps
from django.urls import reverse

from core.models import Map, Chart


class MapSitemap(sitemaps.Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return Map.objects.all().order_by('-id')

    def location(self, obj):
        return reverse('core:map', kwargs={'slug': obj.slug})

    def lastmod(self, obj):
        return obj.changed


class ChartSitemap(sitemaps.Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return Chart.objects.all().order_by('-id')

    def location(self, obj):
        return reverse('core:chart', kwargs={'slug': obj.slug})

    def lastmod(self, obj):
        return obj.changed


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['core:maps', 'core:charts', 'core:about']

    def location(self, obj):
        return reverse(obj)


class CovidViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'hourly'

    def items(self):
        return (
            ('covid_key', 'cases'),
            ('covid_key', 'deaths'),
            ('covid_key', 'total_recovered'),
            ('covid_key', 'new_deaths'),
            ('covid_key', 'new_cases'),
            ('covid_key', 'serious_critical'),
        )

    def location(self, obj):
        return reverse(obj[0], kwargs={'key': obj[1]})
