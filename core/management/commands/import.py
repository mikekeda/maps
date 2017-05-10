from django.core.management import BaseCommand
import json
from os import walk
from os.path import join, splitext

from core.models import Polygon


# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    # Show this when the user types help
    help = "Import Polygons from geojson"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('file', nargs='?', type=str)

    def handle(self, *args, **options):
        self.stdout.write("Started Polygons import")
        path = 'geojson'
        for root, subdirs, files in walk(path):
            grandparent = root.split('/')[-1]
            grandparent = grandparent[0].capitalize() + grandparent[1:]
            for json_file in files:
                parent_title = splitext(json_file)[0]
                parent_title = parent_title[0].capitalize() + parent_title[1:]
                parent = Polygon.objects.filter(title=parent_title)
                if len(parent) > 1:
                    for candidate in parent:
                        if candidate.parent and candidate.parent.title == grandparent:
                            parent = candidate
                            break
                else:
                    parent = parent[0] if parent else None
                with open(join(root, json_file)) as f:
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
                            title=name[0].capitalize() + name[1:],
                            parent=parent,
                            defaults={'geom': feature['geometry']}
                        )
                        if created:
                            print(name + ' was created')
                        else:
                            print(name + ' already exists')
