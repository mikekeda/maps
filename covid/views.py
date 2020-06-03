from django.core.cache import cache
from django.http import Http404
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.views.decorators.http import last_modified
from django.urls import reverse
from django.utils.dateparse import parse_datetime

from maps.utils import range_data

from core.models import Polygon
from covid.utils import get_covid_data, get_covid_country_data


def covid_19_data_last_modified(*_, **__):
    """ Check when data was modified. """
    modified = cache.get('covid_19_last_modified')
    if modified:
        return parse_datetime(modified)


@cache_page(60 * 15)
@last_modified(covid_19_data_last_modified)
def covid_19_view(request, key: str = 'cases'):
    """ COVID-19 map. """

    if key not in ("cases", "deaths", "total_recovered", "new_deaths", "new_cases", "serious_critical", "active_cases"):
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

        if key == "active_cases":
            for key in ("cases", "total_recovered", "deaths"):
                try:
                    stats[country.title][key] = int(stats[country.title][key].replace(',', ''))
                except ValueError:
                    stats[country.title][key] = 0

            data = stats[country.title]["cases"] - stats[country.title]["total_recovered"] - \
                   stats[country.title]["deaths"]
        else:
            try:
                data = int(stats[country.title][key].replace(',', ''))
            except ValueError:
                continue

        total += data
        map_obj['data_min'] = min([data, map_obj['data_min']])
        map_obj['data_max'] = max([data, map_obj['data_max']])

        remaped_key = {"cases": "confirmed", "deaths": "deaths", "total_recovered": "recovered",
                       "active_cases": "active_cases"}

        path = ''
        if key in remaped_key and country.title in {'United States', 'Canada', 'Australia', 'China', 'Ukraine'}:
            path = reverse('covid_country_key', kwargs={'country': country.title, 'key': remaped_key[key]})

        geojson_data += country.geojson(data, path)
    geojson_data += ']}'

    map_obj['title'] = f"COVID-19 ({total} {key.replace('_', ' ')}, {cache.get('covid_19_last_modified')[:10]})"

    return render(request, 'map.html', dict(
        map=map_obj,
        geojson_data=geojson_data,
        data_range=range_data(map_obj)
    ))


def covid_19_country_data_last_modified(*_, country, **__):
    """ Check when data was modified. """
    modified = cache.get(f'covid_19_{country}_last_modified')
    if modified:
        return parse_datetime(modified)


@cache_page(60 * 15)
@last_modified(covid_19_country_data_last_modified)
def covid_19_country_view(request, country, key: str = 'confirmed'):
    if key not in {"confirmed", "deaths", "recovered", "active_cases"}:
        raise Http404

    total = 0
    stats = cache.get(f'covid_19_{country}_data')  # get from cache
    if not stats:
        stats = get_covid_country_data(country)

    if not stats:
        raise Http404

    provinces = Polygon.objects.filter(parent__title=country)

    map_obj = {
        'grades': 8,
        'end_color': 'F1DDF5',
        'start_color': 'ED1C24',
        'opacity': '0.7',
        'unit': key.replace('_', ' '),
        'logarithmic_scale': True,
        'data_min': float('Inf'),
        'data_max': -float('Inf'),
        'description': f"COVID-19 (coronavirus) {country} interactive map, updates every 15m"
    }

    # Get geojson data.
    geojson_data = '{"type": "FeatureCollection", "features":['
    for province in provinces:
        if province.title not in stats:
            continue

        if key == "active_cases":
            confirmed = stats[province.title]["confirmed"]
            deaths = stats[province.title]["deaths"]
            recovered = stats[province.title]["recovered"]
            data = confirmed - recovered - deaths
        else:
            data = stats[province.title][key]
        total += data
        map_obj['data_min'] = min([data, map_obj['data_min']])
        map_obj['data_max'] = max([data, map_obj['data_max']])

        geojson_data += province.geojson(data)
    geojson_data += ']}'

    map_obj['title'] = f"COVID-19 {country} ({total} {key.replace('_', ' ')}, " \
                       f"{cache.get(f'covid_19_{country}_last_modified')[:10]})"

    return render(request, 'map.html', dict(
        map=map_obj,
        geojson_data=geojson_data,
        data_range=range_data(map_obj)
    ))
