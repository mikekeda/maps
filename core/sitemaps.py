from django.contrib import sitemaps
from django.urls import reverse

from .models import Map


class MapSitemap(sitemaps.Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return  Map.objects.all()

    def location(self, obj):
        return reverse('core:map', kwargs={'slug': obj.slug})

    def lastmod(self, obj):
        return obj.changed


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['core:maps', 'core:about']

    def location(self, item):
        return reverse(item)