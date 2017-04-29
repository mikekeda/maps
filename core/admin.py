from leaflet.admin import LeafletGeoAdmin
from django.contrib import admin

from .models import Map, Polygon, MapElement


class MapAdmin(admin.ModelAdmin):
    list_filter = ('user__username',)
    search_fields = ['title']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['initial'] = request.user.id
        return db_field.formfield(**kwargs)


class MapElementAdmin(admin.ModelAdmin):
    list_filter = ('map__title',)


class PolygonAdmin(LeafletGeoAdmin):
    search_fields = ['title']

admin.site.register(Map, MapAdmin)
admin.site.register(Polygon, PolygonAdmin)
admin.site.register(MapElement, MapElementAdmin)
