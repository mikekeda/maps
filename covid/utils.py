from collections import defaultdict
from datetime import datetime
import requests

from bs4 import BeautifulSoup

from django.core.cache import cache

from core.models import Polygon
from maps.settings import get_env_var


def get_covid_data():
    res = requests.get(
        "https://coronavirus-monitor.p.rapidapi.com"
        "/coronavirus/cases_by_country.php",
        headers={
            "x-rapidapi-host": "coronavirus-monitor.p.rapidapi.com",
            "x-rapidapi-key": get_env_var("X_RAPIDAPI_KEY"),
        }
    )
    if res.status_code == 200:
        res = res.json()

        remap = {
            "Czechia": "Czech Republic",
            "North Macedonia": "Macedonia",
            "S. Korea": "South Korea",
            "UAE": "United Arab Emirates",
            "UK": "United Kingdom",
            "USA": "United States",
            "DRC": "Democratic Republic of the Congo",
            "CAR": "Central African Republic",
            "Congo": "Republic of the Congo",
        }

        stats = {
            remap.get(v['country_name'], v['country_name']): v
            for v in res['countries_stat']
        }

        cache.set('covid_19_data', stats, 900)  # 15m
        cache.set('covid_19_last_modified', res['statistic_taken_at'], None)

        return stats


def get_covid_country_data(country):
    stats = {}

    if country == 'Ukraine':
        mapping = {
            'Чернівецька': 'Chernivtsi Oblast',
            'Житомирська': 'Zhytomyr Oblast',
            'Київська': 'Kiev Oblast',
            'Донецька': 'Donetsk Oblast',
            'Дніпропетровська': 'Dnipropetrovsk Oblast',
            'Івано-Франківська': 'Ivano-Frankivsk Oblast',
            'Львівська': 'Lviv Oblast',
            'Тернопільська': 'Ternopil Oblast',
            'Харківська': 'Kharkiv Oblast',
            'Вінницька': 'Vinnytsia Oblast',
            'Волинська': 'Volyn Oblast',
            'Запорізька': 'Zaporizhia Oblast',
            'Луганська': 'Luhansk Oblast',
            'Одеська': 'Odessa Oblast',
            'Херсонська': 'Kherson Oblast',
            'Черкаська': 'Cherkasy Oblast',
            'Рівненська': 'Rivne Oblast',
            'Закарпатська': 'Zakarpattia Oblast',
            'Миколаївська': 'Mykolaiv Oblast',
            'Полтавська': 'Poltava Oblast',
            'Сумська': 'Sumy Oblast',
            'Хмельницька': 'Khmelnytskyi Oblast',
            'Чернігівська': 'Chernihiv Oblast',
            'Кіровоградська': 'Kirovohrad Oblast',
        }

        country = Polygon.objects.filter(level=0, title='Ukraine').first()
        provinces = Polygon.objects.filter(parent=country)
        for province in provinces:
            stats[province.title] = {'confirmed': 0, 'deaths': 0, 'recovered': 0}

        url = "https://moz.gov.ua" \
              "/article/news/operativna-informacija-pro-poshirennja-koronavirusnoi-infekcii-2019-ncov-"

        res = requests.get(url)
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, 'html.parser')
            ul = []
            for ul in soup.select('.medical__vacancy-desc > div > p'):
                ul = ul.text.split('\n')
                if len(ul) > 10:
                    break

            for li in ul:
                data = li.split()
                if not data:
                    continue

                province = data[0]
                data = [
                    int(node.strip('(').strip('-').strip(';').strip('.'))
                    for node in data
                    if node.strip('(').strip('-').strip(';').strip('.').isdigit()
                ]
                data = [data[0] if data else 0, data[1] if len(data) > 1 else 0, data[2] if len(data) > 2 else 0]

                if province in mapping:
                    stats[mapping[province]] = {
                        'confirmed': stats.get(mapping[province], {}).get('confirmed', 0) + data[0],
                        'deaths': stats.get(mapping[province], {}).get('deaths', 0) + data[1],
                        'recovered': stats.get(mapping[province], {}).get('recovered', 0) + data[2],
                    }
                elif province == 'м.':
                    stats['Kiev Oblast'] = {
                        'confirmed': stats['Kiev Oblast'].get('confirmed', 0) + data[0],
                        'deaths': stats['Kiev Oblast'].get('deaths', 0) + data[1],
                        'recovered': stats['Kiev Oblast'].get('recovered', 0) + data[2],
                    }

            cache.set(f'covid_19_{country}_last_modified', datetime.now().isoformat(), None)

    else:
        if country == 'United States':
            country = 'US'

        res = requests.get(
            "https://covid-19-coronavirus-statistics.p.rapidapi.com/v1/stats",
            headers={
                "x-rapidapi-host": "covid-19-coronavirus-statistics.p.rapidapi.com",
                "x-rapidapi-key": get_env_var("X_RAPIDAPI_KEY"),
            },
            params={"country": country}
        )
        if res.status_code == 200:
            res = res.json()

            stats = defaultdict(lambda: {'confirmed': 0, 'deaths': 0, 'recovered': 0})
            for v in res['data']['covid19Stats']:
                stats[v['province']]['confirmed'] += v['confirmed']
                stats[v['province']]['deaths'] += v['deaths']
                stats[v['province']]['recovered'] += v['recovered']

            stats = dict(stats)

            cache.set(f'covid_19_{country}_last_modified', res['data']['lastChecked'], None)

    if any(stats[k]['confirmed'] for k in stats):
        cache.set(f'covid_19_{country}_data', stats, 900)  # 15m

        return stats
