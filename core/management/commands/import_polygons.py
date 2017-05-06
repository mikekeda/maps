from django.core.management import BaseCommand
import json
from os import listdir
from os.path import isfile, join, splitext

from core.models import Polygon


# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    # Show this when the user types help
    help = "Import Polygons from geojson"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('file', nargs='?', type=str)
        parser.add_argument('parent', nargs='?', type=str)

    def handle(self, *args, **options):
        self.stdout.write("Started Polygons import")
        path = 'geojson'
        need_parent = []
        if options['file']:
            files = [options['file']]
        else:
            files = [f for f in listdir(path) if isfile(join(path, f))]

        for json_file in files:
            if options['parent']:
                parent = Polygon.objects.filter(
                    title=splitext(json_file)[0].capitalize(),
                    parent__title=options['parent']).first()
            else:
                parent = Polygon.objects.filter(title=splitext(json_file)[0].capitalize())
                if len(parent) > 1:
                    need_parent.append(json_file)
                    continue
                else:
                    parent = parent[0] if parent else None
            with open(join(path, json_file)) as f:
                data = json.load(f)
                for feature in data['features']:
                    name = ''
                    if 'name:en' in feature['properties']:
                        name = feature['properties']['name:en']
                    elif 'name' in feature['properties']:
                        name = feature['properties']['name']
                    elif 'nom' in feature['properties']:
                        name = feature['properties']['nom']
                    elif 'namelsad' in feature['properties']:
                        name = feature['properties']['namelsad']
                    polygon, created = Polygon.objects.get_or_create(
                        title=name.capitalize(),
                        parent=parent,
                        defaults={'geom': feature['geometry']}
                    )
                    if created:
                        print(name + ' was created')
                    else:
                        print(name + ' already exists')
        if need_parent:
            print('{} need provide parent'.format(', '.join(need_parent)))
