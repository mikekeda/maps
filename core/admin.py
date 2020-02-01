from django.contrib import admin
from django.core.cache import cache
from django.urls import reverse
from django.utils.html import format_html

from leaflet.admin import LeafletGeoAdmin
from easy_select2 import select2_modelform
from mptt.admin import MPTTModelAdmin

from core.models import Map, Polygon, MapElement, Category, Chart

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

    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id, from_field)
        # Get all related polygon titles and send to the cache,
        # we will use it later in MapElement.__str__ to improve performance.
        elements = MapElement.objects.select_related('polygon')\
            .filter(map=obj).values_list('polygon__pk', 'polygon__title')
        cache.set_many({
            'polygon:{}:title'.format(element[0]): element[1]
            for element in elements
        }, 90)
        return obj

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['initial'] = request.user.id

        if db_field.name == 'region':
            # Optimize queryset to avoid loading unneeded fields.
            kwargs['queryset'] = db_field.remote_field.model._default_manager\
                .using(None).only('id', 'title')

        return db_field.formfield(**kwargs)


class MapElementAdmin(admin.ModelAdmin):
    list_display = ('polygon', 'data')
    list_filter = ('map__title',)
    form = MapElementForm


class PolygonAdmin(LeafletGeoAdmin, MPTTModelAdmin):
    search_fields = ['title']
    list_display = ('title', 'export')

    @staticmethod
    def export(obj):
        return format_html(
            '<a href="{}" class="button" style="float: right;"> {} </a>',
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
