from django.conf.urls import url

from .views import homepage, example, map_view, add_map


urlpatterns = [
    url(r'^$', homepage, name='homepage'),
    url(r'^map/(?P<slug>.+)$', map_view, name='map'),
    url(r'^add/map$', add_map, name='add_map'),
    url(r'^example/(?P<example_id>.+)$', example, name='example'),
]
