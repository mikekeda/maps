from django.conf.urls import url
from django.conf import settings

from .views import homepage, example, map_view


urlpatterns = [
    url(r'^$', homepage, name='homepage'),
    url(r'^map/(?P<slug>.+)$', map_view, name='map'),
    url(r'^example/(?P<example_id>.+)$', example, name='example'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
