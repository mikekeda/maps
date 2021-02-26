from django.urls import path, re_path

from core.views import (
    maps_view,
    map_view,
    polygons_view,
    add_map,
    get_polygons,
    polygon_export,
    about,
    charts_view,
    chart_view,
    plots_view,
    plot_view,
    log_in,
    log_out,
    new_style_map_view,
)

app_name = "Maps"

urlpatterns = [
    path("", maps_view, name="maps"),
    path("charts", charts_view, name="charts"),
    path("plots", plots_view, name="plots"),
    path("map/<str:slug>", map_view, name="map"),
    path("new-style-map/<str:slug>", new_style_map_view, name="new_style_map"),
    path("chart/<str:slug>", chart_view, name="chart"),
    path("plot/<str:slug>", plot_view, name="plot"),
    path("plot/<str:slug>/<str:key>", plot_view, name="plot_key"),
    re_path("world/", polygons_view, name="polygons"),
    path("polygon/<int:pk>/geojson", polygon_export, name="polygon_export"),
    path("user/<str:username>/maps", maps_view, name="user_maps"),
    path("user/<str:username>/charts", charts_view, name="user_charts"),
    path("add/map", add_map, name="add_map"),
    path("api/get-polygons/<str:parent_id>", get_polygons, name="get_polygons"),
    path("about", about, name="about"),
    path("login", log_in, name="login"),
    path("logout", log_out, name="logout"),
]
