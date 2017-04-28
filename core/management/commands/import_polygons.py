from django.core.management import BaseCommand
import json

from core.models import Polygon


# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    # Show this when the user types help
    help = "Import Polygons from geojson"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('file', nargs='?', type=str)

    def handle(self, *args, **options):
        file_name = options['file'] if options['file'] else 'frontend/src/app/countries.ts'
        self.stdout.write("Started Polygons import")

        for polygon in Polygon.objects.all():
            print(polygon.geom)

        with open(file_name) as f:
            data = json.load(f)
            for feature in data['features']:
                print(feature['properties']['name'])
                print(feature['geometry']['type'])
                print(feature['geometry']['coordinates'])
