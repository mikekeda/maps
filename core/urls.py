from django.conf.urls import url

from .views import homepage, example, map_view, add_map, get_polygons
from .decorators import simple_cache_page


urlpatterns = [
    url(r'^$', simple_cache_page(60 * 60 * 24, True)(homepage), name='homepage'),
    url(r'^map/(?P<slug>.+)$', simple_cache_page(60 * 60 * 24, True)(map_view), name='map'),
    url(r'^add/map$', add_map, name='add_map'),
    url(r'^api/get-polygons/(?P<region_id>.+)$', get_polygons, name='get_polygons'),
    url(r'^example/(?P<example_id>.+)$', example, name='example'),
]
