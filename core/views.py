import math
import operator
import json

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Prefetch, F
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
# from django.views.decorators.http import condition
from django.utils.translation import ugettext_lazy as _

from .models import Map, MapElement, Polygon, Chart
from .forms import MapForm


def map_latest_entry(request, slug):
    return get_object_or_404(Map, slug=slug).changed


def maps_view(request, username=None):
    """Maps."""
    if username:
        user = get_object_or_404(User, username=username)
        maps = Map.objects.filter(user=user)
    else:
        maps = Map.objects.all()

    params = request.GET.copy()
    params.pop('p', None)
    if 'category' in params:
        maps = maps.filter(categories__slug=params['category'])
    if 'year' in params:
        maps = maps.filter(date_of_information__year=params['year'])
    if 'region' in params:
        region = None if params['region'] == '0' else params['region']
        maps = maps.filter(region=region)

    maps = maps.order_by('-id').prefetch_related('categories')\
        .select_related('region')
    paginator = Paginator(maps, 10)
    page = request.GET.get('p')
    try:
        maps = paginator.page(page)
    except PageNotAnInteger:
        maps = paginator.page(1)
    except EmptyPage:
        maps = paginator.page(paginator.num_pages)

    return render(request, 'list-page.html', dict(
        item_name='map',
        title=_('Maps'),
        items=maps,
        params=params
    ))


# @condition(last_modified_func=map_latest_entry)
def map_view(request, slug):
    """Map."""
    map_obj = get_object_or_404(
        Map.objects.prefetch_related(
            Prefetch(
                'elements',
                queryset=MapElement.objects.select_related('polygon')
            )
        ),
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
        geojson_data += '{{' \
                        '"type": "Feature", ' \
                        '"id": "{}", ' \
                        '"properties": {{"name": "{}", "density": {}}}, ' \
                        '"geometry": {}' \
                        '}}, '.format(
                            element.id,
                            element.polygon.title,
                            element.data,
                            element.polygon.geom
                        )
    geojson_data += ']}'

    if data_min < float('Inf') and data_max > -float('Inf'):
        # Get value step
        if map_obj.logarithmic_scale:
            addition = 1 - data_min
            step = math.log(data_max + addition)
            step -= math.log(data_min + addition)
            step /= map_obj.grades
        else:
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

            if map_obj.logarithmic_scale:
                key = math.log(data_max + addition) - step * (i + 1)
                key = math.pow(math.e, key)
                key -= addition
            else:
                key = data_max - step * (i + 1)
            data_range.append([key, red + green + blue])

    return render(request, 'map.html', dict(
        map=map_obj,
        geojson_data=geojson_data,
        data_range=data_range
    ))


def polygons_view(request):
    """Polygons."""
    args = request.path.split('/')[2:]
    level = len(args) - 1
    title = args[-1]

    map_obj = {
        'title': args[-1] if args[-1] else 'World',
        'grades': 8,
        'end_color': 'BD0026',
        'start_color': 'FFEDA0',
        'opacity': '0.7',
        'unit': 'polygons',
        'logarithmic_scale': True,
    }

    if level == 0:
        if title:
            elements = get_object_or_404(
                Polygon,
                level=level,
                title=title
            ).get_children()
        else:
            elements = Polygon.objects.filter(level=level)
    else:
        parent_title = args[-2]
        elements = get_object_or_404(
            Polygon,
            level=level,
            title=title,
            parent__title=parent_title
        ).get_children()

    data_range = []
    data_min = float('Inf')
    data_max = -float('Inf')

    # Get geojson data.
    geojson_data = '{"type": "FeatureCollection", "features":['
    for element in elements:
        data = (element.rght - element.lft - 1) / 2
        data_min = data if data < data_min else data_min
        data_max = data if data > data_max else data_max

        path = request.path
        if path[-1] != '/':
            path += '/'
        path += element.title

        geojson_data += '{{' \
                        '"type": "Feature", ' \
                        '"id": "{}", ' \
                        '"properties": {{' \
                        '"name": "{}", "density": {}, "path": "{}"' \
                        '}}, ' \
                        '"geometry": {}' \
                        '}}, '.format(
                            element.id, element.title, data, path, element.geom
                        )
    geojson_data += ']}'

    if data_min < float('Inf') and data_max > -float('Inf'):
        # Get value step
        if map_obj['logarithmic_scale']:
            addition = 1 - data_min
            step = math.log(data_max + addition)
            step -= math.log(data_min + addition)
            step /= map_obj['grades']
        else:
            step = (data_max - data_min) / map_obj['grades']

        # Convert colors to int
        start_red = int(map_obj['start_color'][:2], 16)
        start_green = int(map_obj['start_color'][2:4], 16)
        start_blue = int(map_obj['start_color'][4:], 16)

        end_red = int(map_obj['end_color'][:2], 16)
        end_green = int(map_obj['end_color'][2:4], 16)
        end_blue = int(map_obj['end_color'][4:], 16)

        # Get color steps
        red_step = (end_red - start_red) / map_obj['grades']
        green_step = (end_green - start_green) / map_obj['grades']
        blue_step = (end_blue - start_blue) / map_obj['grades']

        for i in reversed(range(map_obj['grades'])):
            # Get current colors
            red = hex(start_red + int(red_step * i))[2:]
            green = hex(start_green + int(green_step * i))[2:]
            blue = hex(start_blue + int(blue_step * i))[2:]

            # Fix current colors (we need 2 digits)
            red = red if len(red) == 2 else '0' + red
            green = green if len(green) == 2 else '0' + green
            blue = blue if len(blue) == 2 else '0' + blue

            if map_obj['logarithmic_scale']:
                key = math.log(data_max + addition) - step * (i + 1)
                key = math.pow(math.e, key)
                key -= addition
            else:
                key = data_max - step * (i + 1)
            data_range.append([key, red + green + blue])

    return render(request, 'map.html', dict(
        map=map_obj,
        geojson_data=geojson_data,
        data_range=data_range
    ))


@login_required
def add_map(request):
    """Create Map."""
    if request.method == 'POST':
        form = MapForm(data=request.POST, prefix='map')
        if form.is_valid():
            map_obj = form.save(commit=False)
            map_obj.user = request.user
            map_obj.save()
            form.save_m2m()

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

    regions = Polygon.objects.filter(lft__lte=F('rght')-2)\
        .order_by('tree_id', 'level', 'title')

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
        polygons = get_object_or_404(Polygon, pk=parent_id)\
            .get_children().order_by('title')
    polygons = json.dumps([
        {'pk': polygon.pk, 'title': polygon.title}
        for polygon in polygons
    ])

    return JsonResponse({'polygons': polygons})


def about(request):
    """About page."""

    return render(request, 'about.html')


def charts_view(request, username=None):
    """Charts."""
    if username:
        user = get_object_or_404(User, username=username)
        charts = Chart.objects.filter(user=user)
    else:
        charts = Chart.objects.all()

    params = request.GET.copy()
    params.pop('p', None)

    paginator = Paginator(charts.order_by('-id'), 10)
    page = request.GET.get('p')
    try:
        charts = paginator.page(page)
    except PageNotAnInteger:
        charts = paginator.page(1)
    except EmptyPage:
        charts = paginator.page(paginator.num_pages)

    return render(request, 'list-page.html', dict(
        item_name='chart',
        title=_('Charts'),
        items=charts,
        params=params
    ))


def chart_view(request, slug):
    """Chart page."""
    chart_obj = get_object_or_404(
        Chart.objects.prefetch_related(
            Prefetch('maps', queryset=Map.objects.prefetch_related(
                Prefetch(
                    'elements',
                    queryset=MapElement.objects.select_related('polygon')
                )
            ))
        ),
        slug=slug
    )

    # Get polygon titles.
    titles = {}
    for map_obj in chart_obj.maps.all():
        for element in map_obj.elements.all():
            titles[element.polygon.pk] = element.polygon.title
    titles = sorted(titles.items(), key=operator.itemgetter(1))

    # Get data.
    data = []
    data_min = float('Inf')
    for map_obj in chart_obj.maps.all():
        data.append({
            'name': map_obj.title,
            'data': {},
        })
        for pk in titles:
            data[-1]['data'][pk[0]] = 0
        for element in map_obj.elements.all():
            data[-1]['data'][element.polygon.pk] = element.data
        data[-1]['data'] = list(data[-1]['data'].values())
        map_data_min = min(data[-1]['data'])
        data_min = map_data_min if map_data_min < data_min else data_min

    return render(request, 'chart.html', dict(
        chart=chart_obj,
        titles=[title[1] for title in titles],
        data=data,
        data_min=data_min,
    ))


def log_in(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(reverse('core:maps'))

    return render(request, 'login.html', {'form': form})


@login_required
def log_out(request):
    logout(request)
    return redirect(reverse('core:login'))
