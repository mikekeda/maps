from django.contrib import admin
from django.utils.html import format_html
from django.core.urlresolvers import reverse

from leaflet.admin import LeafletGeoAdmin
from easy_select2 import select2_modelform
from mptt.admin import MPTTModelAdmin

from .models import Map, Polygon, MapElement, Category, Chart

MapElementForm = select2_modelform(MapElement)
MapForm = select2_modelform(Map)


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
    list_display = ('title', 'export')

    @staticmethod
    def export(obj):
        return format_html(
            '<a href="{}" class="button" style="float: right;">{}</a>',
            reverse('core:polygon_export', args=[obj.pk]),
            'Export to geojson'
        )


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
