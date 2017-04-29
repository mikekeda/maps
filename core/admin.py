from leaflet.admin import LeafletGeoAdmin
from django.contrib import admin
from easy_select2 import select2_modelform

from .models import Map, Polygon, MapElement

MapElementForm = select2_modelform(MapElement)


class MapAdmin(admin.ModelAdmin):
    list_filter = ('user__username',)
    search_fields = ['title']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['initial'] = request.user.id
        return db_field.formfield(**kwargs)


class MapElementAdmin(admin.ModelAdmin):
    list_filter = ('map__title',)
    form = MapElementForm


class PolygonAdmin(LeafletGeoAdmin):
    search_fields = ['title']
    list_filter = ('region',)
    readonly_fields = ('region',)

admin.site.register(Map, MapAdmin)
admin.site.register(Polygon, PolygonAdmin)
admin.site.register(MapElement, MapElementAdmin)
