from django.conf.urls import include
from django.contrib import admin
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.utils.translation import gettext_lazy as _

from core.sitemaps import (
    StaticPagesSitemap,
    MapsSitemap,
    ChartsSitemap,
)

sitemaps = {
    "maps": MapsSitemap,
    "charts": ChartsSitemap,
    "static_pages": StaticPagesSitemap,
}

urlpatterns = [
    path("", include("core.urls", namespace="core")),
    path("accounts/", include("allauth.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("admin/", admin.site.urls),
]

admin.site.site_header = _("Maps administration")

if settings.DEBUG:
    from django.conf.urls.static import static
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
