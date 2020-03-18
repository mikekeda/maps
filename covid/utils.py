import requests

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
        }

        stats = {
            remap.get(v['country_name'], v['country_name']): v
            for v in res['countries_stat']
        }

        cache.set('covid_19_data', stats, 900)  # 15m
        cache.set('covid_19_last_modified', res['statistic_taken_at'], None)

        return stats


def get_covid_country_data(country):
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

        stats = {
            v['province']: v
            for v in res['data']['covid19Stats']
        }

        cache.set(f'covid_19_{country}_data', stats, 900)  # 15m
        cache.set(f'covid_19_{country}_last_modified', res['data']['lastChecked'], None)

        return stats
