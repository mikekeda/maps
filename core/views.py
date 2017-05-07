from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Prefetch, F
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.contrib.auth.models import User
import json
from django.views.decorators.http import condition

from .models import Map, MapElement, Polygon
from .forms import MapForm


def map_latest_entry(request, slug):
    return get_object_or_404(Map, slug=slug).changed


def maps(request, username=None):
    """Maps."""
    if username:
        user = get_object_or_404(User, username=username)
        maps = Map.objects.filter(user=user).order_by('-id')
    else:
        maps = Map.objects.all().order_by('-id')

    return render(request, 'homepage.html', dict(maps=maps, active_page='homepage'))


@condition(last_modified_func=map_latest_entry)
def map_view(request, slug):
    """Map."""
    map_obj = get_object_or_404(
        Map.objects.prefetch_related(Prefetch('elements', queryset=MapElement.objects.select_related('polygon'))),
        slug=slug
    )

    data_range = []
    data_min = float('Inf')
    data_max = -float('Inf')

    # Get geojson data.
    geojson_data = '{"type": "FeatureCollection", "features":['
    for element in map_obj.elements.all():
        data_min = element.data if element.data < data_min else data_min
        data_max = element.data if element.data > data_max else data_max
        geojson_data += '{{\
                "type": "Feature", "id": "{}", "properties": {{"name": "{}", "density": {}}}, "geometry": {}\
            }}, '.format(
            element.id, element.polygon.title, element.data, element.polygon.geom
        )
    geojson_data += ']}'

    if data_min < float('Inf') and data_max > -float('Inf'):
        # Get value step
        step = (data_max - data_min) / map_obj.grades

        # Convert colors to int
        start_red = int(map_obj.start_color[:2], 16)
        start_green = int(map_obj.start_color[2:4], 16)
        start_blue = int(map_obj.start_color[4:], 16)

        end_red = int(map_obj.end_color[:2], 16)
        end_green = int(map_obj.end_color[2:4], 16)
        end_blue = int(map_obj.end_color[4:], 16)

        # Get color steps
        red_step = (end_red - start_red) / map_obj.grades
        green_step = (end_green - start_green) / map_obj.grades
        blue_step = (end_blue - start_blue) / map_obj.grades

        for i in reversed(range(map_obj.grades)):
            # Get current colors
            red = hex(start_red + int(red_step * i))[2:]
            green = hex(start_green + int(green_step * i))[2:]
            blue = hex(start_blue + int(blue_step * i))[2:]

            # Fix current colors (we need 2 digits)
            red = red if len(red) == 2 else '0' + red
            green = green if len(green) == 2 else '0' + green
            blue = blue if len(blue) == 2 else '0' + blue

            key = data_max - step * (i + 1)
            data_range.append([key, red + green + blue])

    return render(request, 'map.html', dict(
        map=map_obj,
        geojson_data=geojson_data,
        data_range=data_range,
        active_page='map')
    )


@login_required
def add_map(request):
    """Create Map."""
    if request.method == 'POST':
        form = MapForm(data=request.POST, prefix='map')
        if form.is_valid():
            map_obj = form.save(commit=False)
            map_obj.user = request.user
            map_obj.save()

            # Create map elements.
            polygon_prefix = 'polygon_'
            for key in request.POST:
                if key.startswith(polygon_prefix) and request.POST[key]:
                    MapElement(
                        map=map_obj,
                        polygon_id=key.strip(polygon_prefix),
                        data=request.POST[key]
                    ).save()

            return redirect(reverse('core:map', args=(map_obj.slug,)))
    else:
        form = MapForm(prefix='map')

    regions = Polygon.objects.filter(lft__lte=F('rght')-2).order_by('tree_id', 'level', 'title')

    return render(request, 'map-form.html', {
        'form': form,
        'regions': regions,
    })


@login_required
def get_polygons(request, parent_id):
    """Get array of polygons by region."""
    if parent_id == '0':
        polygons = Polygon.objects.filter(lft=1).order_by('title')
    else:
        polygons = get_object_or_404(Polygon, pk=parent_id).get_children().order_by('title')
    polygons = json.dumps([{'pk': polygon.pk, 'title': polygon.title} for polygon in polygons])

    return JsonResponse({'polygons': polygons})


def example(request, example_id):
    """Example map."""

    return render(request, 'example' + example_id + '.html')


def about(request):
    """About page."""

    return render(request, 'about.html')
