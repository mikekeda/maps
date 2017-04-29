from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch

from .models import Map, MapElement


def homepage(request):
    """Homepage."""
    if request.user.is_authenticated:
        maps = Map.objects.filter(user=request.user).order_by('-id')
    else:
        maps = Map.objects.all()

    return render(request, 'homepage.html', dict(maps=maps, active_page='homepage'))


def map_view(request, slug):
    """Map."""
    map_obj = get_object_or_404(
        Map.objects.prefetch_related(Prefetch('elements', queryset=MapElement.objects.select_related('polygon'))),
        slug=slug
    )

    data_range = {'min': float('Inf'), 'max': -float('Inf'), 'step': 0}

    # Get geojson data.
    geojson_data = '{"type": "FeatureCollection", "features":['
    for element in map_obj.elements.all():
        data_range['min'] = element.data if element.data < data_range['min'] else data_range['min']
        data_range['max'] = element.data if element.data > data_range['max'] else data_range['max']
        geojson_data += '{{\
                "type": "Feature", "id": "{}", "properties": {{"name": "{}", "density": {}}}, "geometry": {}\
            }}, '.format(
            element.id, element.polygon.title, element.data, element.polygon.geom
        )
    geojson_data += ']}'

    data_range['step'] = (data_range['max'] - data_range['min']) / 8

    return render(request, 'map.html', dict(
        map=map_obj,
        geojson_data=geojson_data,
        data_range=data_range,
        active_page='map')
    )


def example(request, example_id):
    """Example map."""

    return render(request, 'example' + example_id + '.html')
