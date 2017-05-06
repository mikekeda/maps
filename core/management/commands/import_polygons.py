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
        parser.add_argument('level', nargs='?', type=str)

    def handle(self, *args, **options):
        self.stdout.write("Started Polygons import")
        path = 'geojson'
        if options['file']:
            files = [options['file']]
        else:
            files = [f for f in listdir(path) if isfile(join(path, f))]

        for json_file in files:
            if options['level']:
                parent = Polygon.objects.filter(title=splitext(json_file)[0].capitalize(), level=options['level']).first()
            else:
                parent = Polygon.objects.filter(title=splitext(json_file)[0].capitalize()).first()
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
                    polygon, created = Polygon.objects.get_or_create(
                        title=name.capitalize(),
                        parent=parent,
                        defaults={'geom': feature['geometry']}
                    )
                    if created:
                        print(name + ' was created')
                    else:
                        print(name + ' already exists')
