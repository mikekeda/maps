from leaflet.admin import LeafletGeoAdmin
from django.contrib import admin

from .models import Polygon


admin.site.register(Polygon, LeafletGeoAdmin)
