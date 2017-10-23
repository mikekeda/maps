from django.contrib import admin
from django.http import HttpResponse
from leaflet.admin import LeafletGeoAdmin
from easy_select2 import select2_modelform
from mptt.admin import MPTTModelAdmin

from .models import Map, Polygon, MapElement, Category, Chart

MapElementForm = select2_modelform(MapElement)
MapForm = select2_modelform(Map)


def export_as_geojson_action():
    """This function returns an export geojson action"""
    def export_as_geojson(modeladmin, request, queryset):
        elements = list(queryset)[0]
        geojson_data = '{"type": "FeatureCollection", "features":['
        for element in elements.get_children():
            geojson_data += element.geojson() + ','
        geojson_data = geojson_data.rstrip(',') + ']}'

        response = HttpResponse(
            content=geojson_data,
            content_type='text/plain'
        )
        response['Content-Disposition'] = 'attachment; filename={}.geojson'\
            .format(
                (elements.title[:1].lower() + elements.title[1:]).replace(
                    '.', '_'
                )
            )
        return response

    export_as_geojson.short_description = "Export to geojson (just one file)"
    return export_as_geojson


class MapElementInline(admin.TabularInline):
    model = MapElement
    exclude = ['polygon']


class MapAdmin(admin.ModelAdmin):
    list_filter = ('user__username',)
    search_fields = ['title']
    form = MapForm
    inlines = [MapElementInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['initial'] = request.user.id
        return db_field.formfield(**kwargs)


class MapElementAdmin(admin.ModelAdmin):
    list_filter = ('map__title',)
    form = MapElementForm


class PolygonAdmin(LeafletGeoAdmin, MPTTModelAdmin):
    search_fields = ['title']
    actions = [export_as_geojson_action()]


class ChartAdmin(admin.ModelAdmin):
    list_filter = ('user__username',)
    search_fields = ['title']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['initial'] = request.user.id
        return db_field.formfield(**kwargs)


admin.site.register(Map, MapAdmin)
admin.site.register(Polygon, PolygonAdmin)
admin.site.register(MapElement, MapElementAdmin)
admin.site.register(Category)
admin.site.register(Chart, ChartAdmin)
