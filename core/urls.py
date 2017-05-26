from django.conf.urls import url

from .views import maps, example, map_view, polygons_view, add_map, get_polygons, about, charts, chart_view, log_in, log_out
from .decorators import simple_cache_page


urlpatterns = [
    url(r'^$', maps, name='maps'),
    url(r'^charts$', charts, name='charts'),
    url(r'^map/(?P<slug>.+)$', simple_cache_page(60 * 60 * 24, True)(map_view), name='map'),
    url(r'^chart/(?P<slug>.+)$', chart_view, name='chart'),
    url(r'^world/', polygons_view, name='polygons'),
    url(r'^user/(?P<username>\w+)/maps$', maps, name='user_maps'),
    url(r'^user/(?P<username>\w+)/charts$', charts, name='user_charts'),
    url(r'^map/(?P<slug>.+)$', map_view, name='map'),
    url(r'^add/map$', add_map, name='add_map'),
    url(r'^api/get-polygons/(?P<parent_id>.+)$', get_polygons, name='get_polygons'),
    url(r'^example/(?P<example_id>.+)$', example, name='example'),
    url(r'^about$', about, name='about'),
    url(r'^login$', log_in, name='login'),
    url(r'^logout$', log_out, name='logout'),
]
