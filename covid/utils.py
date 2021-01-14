from collections import defaultdict
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from django.core.cache import cache

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

    return None


def populate_stats(stats, data, mapping) -> None:
    if data:
        province = data[0]
        data = [
            int(node.strip('(').strip('-').strip('—').strip(';').strip('.'))
            for node in data
            if node.strip('(').strip('-').strip('—').strip(';').strip('.').isdigit()
        ]
        data += [0] * (3 - len(data))

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


def get_covid_country_data(country: str) -> dict:
    stats = {}

    if country == 'Ukraine':
        mapping = {
            'Чернівецька': 'Chernivtsi Oblast',
            'Житомирська': 'Zhytomyr Oblast',
            'Київська': 'Kiev Oblast',
            'Донецька': 'Donetsk Oblast',
            'Дніпропетровська': 'Dnipropetrovsk Oblast',
            'Івано-Франківська': 'Ivano-Frankivsk Oblast',
            'Івано': 'Ivano-Frankivsk Oblast',
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
            'Крим': 'Autonomous Republic of Crimea',
        }

        for province in mapping.values():
            stats[province] = {'confirmed': 0, 'deaths': 0, 'recovered': 0}

        url = "https://moz.gov.ua/article/news" \
              "/operativna-informacija-pro-poshirennja-koronavirusnoi-infekcii-2019-cov19"

        try:
            res = requests.get(url, timeout=30)
        except requests.exceptions.ReadTimeout:
            return stats

        if res.status_code == 200:
            soup = BeautifulSoup(res.content, 'html.parser')
            for tr in soup.select('.medical__vacancy-desc > .editor > table tr')[3:]:
                if not tr:
                    continue

                data = [td.text.strip('\n') for td in tr.select('td')]
                data = [data[0]] + data[1::2]
                populate_stats(stats, data, mapping)

            cache.set(f'covid_19_{country}_last_modified', datetime.now().isoformat(), None)

    else:
        res = requests.get(
            "https://covid-19-coronavirus-statistics.p.rapidapi.com/v1/stats",
            headers={
                "x-rapidapi-host": "covid-19-coronavirus-statistics.p.rapidapi.com",
                "x-rapidapi-key": get_env_var("X_RAPIDAPI_KEY"),
            },
            params={"country": country if country != 'United States' else 'US'}
        )
        if res.status_code == 200:
            res = res.json()

            stats = defaultdict(lambda: {'confirmed': 0, 'deaths': 0, 'recovered': 0})
            for v in res['data']['covid19Stats']:
                stats[v['province']]['confirmed'] += v['confirmed'] or 0
                stats[v['province']]['deaths'] += v['deaths'] or 0
                stats[v['province']]['recovered'] += v['recovered'] or 0

            stats = dict(stats)

            cache.set(f'covid_19_{country}_last_modified', res['data']['lastChecked'], None)

    if any(stats[k]['confirmed'] for k in stats):
        cache.set(f'covid_19_{country}_data', stats, 900)  # 15m

    return stats
