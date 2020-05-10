from django.conf.urls import include
from django.contrib import admin
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.utils.translation import ugettext_lazy as _

from core.sitemaps import (StaticPagesSitemap, MapsSitemap, ChartsSitemap,
                           CovidMapsSitemap, CovidChartsSitemap)

from covid.views import covid_19_view, covid_19_country_view

sitemaps = {
    'maps': MapsSitemap,
    'charts': ChartsSitemap,
    'static_pages': StaticPagesSitemap,
    'covid_maps': CovidMapsSitemap,
    'covid_charts': CovidChartsSitemap,
}

urlpatterns = [
    path('', include('core.urls', namespace='core')),
    path('covid', covid_19_view, name='covid'),
    path('covid/<str:key>', covid_19_view, name='covid_key'),
    path('covid-country/<str:country>', covid_19_country_view, name='covid_country'),
    path('covid-country/<str:country>/<str:key>', covid_19_country_view, name='covid_country_key'),
    path('accounts/', include('allauth.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('admin/', admin.site.urls),
]

admin.site.site_header = _('Maps administration')

if settings.DEBUG:
    from django.conf.urls.static import static
    import debug_toolbar

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
