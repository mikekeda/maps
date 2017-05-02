from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import StaticViewSitemap, MapSitemap

sitemaps = {
    'maps': MapSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    url(r'^', include('core.urls', namespace='core')),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
