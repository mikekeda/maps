from collections import defaultdict
import json
import operator

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Prefetch, F, Max
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse, Http404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from maps.utils import range_data

from core.models import Map, MapElement, Polygon, Chart, Plot
from core.forms import MapForm

User = get_user_model()


def maps_view(request, username=None):
    """ Maps. """
    if username:
        user = get_object_or_404(User, username=username)
        maps = Map.objects.filter(user=user)
    else:
        maps = Map.objects.all()

    params = request.GET.copy()
    params.pop('p', None)
    if 'category' in params:
        maps = maps.filter(categories__slug=params['category'])
    if 'year' in params and params['year'].isdigit():
        maps = maps.filter(date_of_information__year=params['year'])
    if 'region' in params and params['region'].isdigit():
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


def new_style_map_view(request, slug):
    """ Google chart map. """
    map_obj = get_object_or_404(
        Map.objects.prefetch_related(
            Prefetch(
                'elements',
                queryset=MapElement.objects.order_by('-data').select_related('polygon')
            )
        ),
        slug=slug
    )
    elements = map_obj.elements.all()

    return render(request, 'new-style-map.html', dict(
        map=map_obj,
        google_map_api_key=settings.GOOGLE_MAP_API_KEY,
        data=[
            ['Country', map_obj.title],
        ] + [
            [elem.polygon.title, elem.data]
            for elem in elements
        ],
    ))


def map_view(request, slug):
    """ Map. """
    map_obj = get_object_or_404(
        Map.objects.prefetch_related('elements__polygon'),
        slug=slug
    )

    data_min = float('Inf')
    data_max = -float('Inf')

    # Get geojson data.
    geojson_data = '{"type": "FeatureCollection", "features":['
    for element in map_obj.elements.all():
        data_min = element.data if element.data < data_min else data_min
        data_max = element.data if element.data > data_max else data_max
        geojson_data += element.geojson()
    geojson_data += ']}'

    map_obj = map_obj.__dict__
    map_obj['data_min'] = data_min
    map_obj['data_max'] = data_max

    return render(request, 'map.html', dict(
        map=map_obj,
        geojson_data=geojson_data,
        data_range=range_data(map_obj)
    ))


def polygons_view(request):
    """ Polygons. """
    args = request.path.split('/')[2:]
    level = len(args) - 1
    title = args[-1]

    map_obj = {
        'title': title or 'World',
        'grades': 8,
        'end_color': 'BD0026',
        'start_color': 'FFEDA0',
        'opacity': '0.7',
        'unit': 'polygons',
        'logarithmic_scale': True,
        'data_min': float('Inf'),
        'data_max': -float('Inf')
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

    # Get geojson data.
    geojson_data = '{"type": "FeatureCollection", "features":['
    for element in elements:
        data = (element.rght - element.lft - 1) // 2
        map_obj['data_min'] = min([data, map_obj['data_min']])
        map_obj['data_max'] = max([data, map_obj['data_max']])

        path = request.path
        if path[-1] != '/':
            path += '/'
        path += element.title

        geojson_data += element.geojson(data, path)
    geojson_data += ']}'

    return render(request, 'map.html', dict(
        map=map_obj,
        geojson_data=geojson_data,
        data_range=range_data(map_obj)
    ))


@login_required
def polygon_export(request, pk):
    """ Polygon export callback. """
    element = get_object_or_404(Polygon, pk=pk)
    geojson_data = '{"type": "FeatureCollection", "features":['
    for child in element.get_children():
        geojson_data += child.geojson() + ','
    geojson_data = geojson_data.rstrip(',') + ']}'

    response = HttpResponse(
        content=geojson_data,
        content_type='text/plain'
    )
    response['Content-Disposition'] = 'attachment; filename={}.geojson'\
        .format(
            (element.title[:1].lower() + element.title[1:]).replace(
                '.', '_'
            )
        )
    return response


@login_required
def add_map(request):
    """ Create Map. """
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
    """ Get array of polygons by region. """
    # Get level of detail (default 1).
    params = request.GET.copy()
    lvl = params.get('lvl')
    try:
        lvl = int(lvl)
    except (ValueError, TypeError):
        lvl = 1

    if parent_id == '0':
        parent_id = None

    # Get polygons.
    filter_field = 'parent__' * (lvl - 1) + 'parent_id'
    polygons = Polygon.objects.filter(
        **{filter_field: parent_id}
    ).order_by('title')

    polygons = json.dumps([
        {'pk': polygon.pk, 'title': polygon.title}
        for polygon in polygons
    ])

    return JsonResponse({'polygons': polygons})


def about(request):
    """ About page. """
    return render(request, 'about.html')


def charts_view(request, username=None):
    """ Charts. """
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
    """ Chart page. """
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


def plots_view(request, username=None):
    """ Plots page. """
    if username:
        user = get_object_or_404(User, username=username)
        plots = Plot.objects.values('slug', 'user').annotate(date_of_information=Max("added")).filter(user=user)
    else:
        plots = Plot.objects.values('slug', 'user').annotate(date_of_information=Max("added")).all()

    params = request.GET.copy()
    params.pop('p', None)

    paginator = Paginator(plots.order_by('-id'), 10)
    page = request.GET.get('p')
    try:
        plots = paginator.page(page)
    except PageNotAnInteger:
        plots = paginator.page(1)
    except EmptyPage:
        plots = paginator.page(paginator.num_pages)

    return render(request, 'list-page.html', dict(
        item_name='plot',
        title=_('Plots'),
        items=plots,
        params=params
    ))


def plot_view(request, slug: str, key: str = None):
    """ Plot page. """

    if slug == 'covid':
        key = key or 'cases'

        if key not in {"cases", "deaths", "total_recovered", "new_deaths", "new_cases",
                       "serious_critical", "active_cases"}:
            raise Http404

    data = Plot.objects.filter(slug=slug).order_by('-added')

    data_per_country = defaultdict(dict)
    for d in data:
        for country, v in d.data.items():
            if slug == 'covid' and key == "active_cases":
                try:
                    cases = int(v["cases"].replace(',', ''))
                    total_recovered = int(v["total_recovered"].replace(',', ''))
                    deaths = int(v["deaths"].replace(',', ''))
                except ValueError:
                    continue

                if cases:
                    data_per_country[country][d.added.isoformat()[:10]] = cases - total_recovered - deaths
            elif key in v:
                try:
                    value = int(v[key].replace(',', ''))
                except ValueError:
                    continue
                if value:
                    data_per_country[country][d.added.isoformat()[:10]] = value

    data_per_country = {k: data_per_country[k] for k in sorted(data_per_country.keys())}

    return render(request, 'covid-chart.html', {'data': data_per_country, 'key': key.replace('_', ' ')})


def log_in(request):
    """ User login page. """
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(reverse('core:maps'))

    return render(request, 'login.html', {'form': form})


@login_required
def log_out(request):
    """ User logout callback. """
    logout(request)
    return redirect(reverse('core:login'))
