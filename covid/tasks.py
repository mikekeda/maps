from covid.celery import app
from covid.models import Data
from covid.utils import get_covid_data


@app.task
def daily_covid_data():
    """ Update youtube info for League and Team weekly. """
    data = get_covid_data()

    category_obj = Data(slug="covid", data=data)
    category_obj.save()
