from django.conf.urls import url

from .views import maps, example, map_view, add_map, get_polygons, about
from .decorators import simple_cache_page


urlpatterns = [
    url(r'^$', simple_cache_page(60 * 60 * 24, True)(maps), name='maps'),
    url(r'^map/(?P<slug>.+)$', simple_cache_page(60 * 60 * 24, True)(map_view), name='map'),
    url(r'^user/(?P<username>\w+)/maps$', maps, name='user_maps'),
    url(r'^map/(?P<slug>.+)$', map_view, name='map'),
    url(r'^add/map$', add_map, name='add_map'),
    url(r'^api/get-polygons/(?P<parent_id>.+)$', get_polygons, name='get_polygons'),
    url(r'^example/(?P<example_id>.+)$', example, name='example'),
    url(r'^about$', about, name='about'),
]
