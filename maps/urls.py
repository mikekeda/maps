from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from django.utils.translation import ugettext_lazy as _

from core.sitemaps import StaticViewSitemap, MapSitemap, ChartSitemap

sitemaps = {
    'maps': MapSitemap,
    'charts': ChartSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    url(r'^', include('core.urls', namespace='core')),
    url(r'^oauth/', include('social_django.urls', namespace='social')),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'^admin/', admin.site.urls),
]
urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]

admin.site.site_header = _('Maps administration')

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
