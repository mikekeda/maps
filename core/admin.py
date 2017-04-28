from leaflet.admin import LeafletGeoAdmin
from django.contrib import admin

from .models import Map, Polygon, MapElement


class MapAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['initial'] = request.user.id
        return db_field.formfield(**kwargs)

admin.site.register(Map, MapAdmin)
admin.site.register(Polygon, LeafletGeoAdmin)
admin.site.register(MapElement)
