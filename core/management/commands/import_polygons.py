from django.core.management import BaseCommand
import json
from os import listdir
from os.path import isfile, join, splitext

from core.models import Polygon, Region


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
        if options['file']:
            files = [options['file']]
        else:
            files = [f for f in listdir(path) if isfile(join(path, f))]

        for json_file in files:
            region, created = Region.objects.get_or_create(filename=splitext(json_file)[0].capitalize())
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
                        region=region,
                        defaults={'geom': feature['geometry']}
                    )
                    if created:
                        print(name + ' was created')
                    else:
                        print(name + ' already exists')
