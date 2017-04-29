from django.conf.urls import url

from .views import homepage, example, map_view


urlpatterns = [
    url(r'^$', homepage, name='homepage'),
    url(r'^map/(?P<slug>.+)$', map_view, name='map'),
    url(r'^example/(?P<example_id>.+)$', example, name='example'),
]
