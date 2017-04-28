from django.core.management import BaseCommand
import json
from os import listdir
from os.path import isfile, join

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
        if options['file']:
            files = [options['file']]
        else:
            path = 'geojson'
            files = [join(path, f) for f in listdir(path) if isfile(join(path, f))]

        for json_file in files:
            with open(json_file) as f:
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
                        title=name,
                        defaults={'geom': feature['geometry']}
                    )
                    if created:
                        print(name + ' was created')
                    else:
                        print(name + ' already exists')
