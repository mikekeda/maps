from django.core.cache import cache
from django.shortcuts import render
from django.http import Http404
from django.views.decorators.http import last_modified
from django.utils.dateparse import parse_datetime

from maps.utils import range_data

from core.models import Polygon
from covid.utils import get_covid_data


def covid_19_data_last_modified(*_, **__):
    """ Check when data was modified. """
    modified = cache.get('covid_19_last_modified')
    if modified:
        return parse_datetime(modified)


@last_modified(covid_19_data_last_modified)
def covid_19_view(request, key: str = 'cases'):
    """ COVID-19 map. """

    if key not in ("cases", "deaths", "total_recovered", "new_deaths",
                   "new_cases", "serious_critical"):
        raise Http404

    total = 0
    stats = cache.get('covid_19_data')  # get from cache
    if not stats:
        stats = get_covid_data()

    countries = Polygon.objects.filter(level=0)

    map_obj = {
        'grades': 8,
        'end_color': 'F1DDF5',
        'start_color': 'ED1C24',
        'opacity': '0.7',
        'unit': key.replace('_', ' '),
        'logarithmic_scale': True,
        'data_min': float('Inf'),
        'data_max': -float('Inf'),
        'description': "COVID-19 (coronavirus) interactive map, updates every 15m"
    }

    # Get geojson data.
    geojson_data = '{"type": "FeatureCollection", "features":['
    for country in countries:
        if country.title not in stats:
            continue

        data = int(stats[country.title][key].replace(',', ''))
        total += data
        map_obj['data_min'] = min([data, map_obj['data_min']])
        map_obj['data_max'] = max([data, map_obj['data_max']])

        geojson_data += country.geojson(data)
    geojson_data += ']}'

    map_obj['title'] = f"COVID-19 ({total} {key.replace('_', ' ')}, {cache.get('covid_19_last_modified')[:10]})"

    return render(request, 'map.html', dict(
        map=map_obj,
        geojson_data=geojson_data,
        data_range=range_data(map_obj)
    ))
