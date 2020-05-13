from core.models import Plot
from covid.celery import app
from covid.utils import get_covid_data


@app.task
def daily_covid_data():
    """ Update youtube info for League and Team weekly. """
    data = get_covid_data()

    data_obj = Plot(slug="covid", data=data, user_id=1)
    data_obj.save()
