import json
from os import walk, listdir
from os.path import join, splitext, isfile

from django.core.management import BaseCommand

from core.models import Polygon


def map_name(feature):
    """Fix title for some json files."""
    name = ''
    if 'name:en' in feature['properties']:
        name = feature['properties']['name:en']
    elif 'name' in feature['properties']:
        name = feature['properties']['name']
    elif 'nom' in feature['properties']:
        name = feature['properties']['nom']
    elif 'namelsad' in feature['properties']:
        name = feature['properties']['namelsad']
    elif 'provincia' in feature['properties']:
        # for argentina.geojson
        name = feature['properties']['provincia']
    elif 'DEPARTAMTO' in feature['properties']:
        # for argentina.geojson
        name = feature['properties']['DEPARTAMTO']
    elif 'prefecture' in feature['properties']:
        # for mongolia.geojson
        name = feature['properties']['prefecture']
    elif 'REGION' in feature['properties']:
        # for nepal.geojson
        name = feature['properties']['REGION']

    return name


def get_files(path: str, file: str):
    """Get all files for import."""
    if file:
        if isfile(join(path, file)):
            root = path
            subdir = file.rsplit('/', 1)
            if len(subdir) > 1:
                root += '/' + subdir[0]
            need_process = [(
                root,
                None,
                [file.split('/')[-1]]
            )]
        else:
            root = path + '/' + file
            need_process = [(
                root,
                None,
                [f for f in listdir(root) if isfile(join(root, f))]
            )]
    else:
        need_process = walk(path)

    return need_process


# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    # Show this when the user types help
    help = "Import Polygons from geojson"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('file', nargs='?', type=str)

    def handle(self, *args, **options):
        self.stdout.write("Started Polygons import")
        need_process = get_files('geojson', options['file'])

        for root, _, files in need_process:
            grandparent = root.split('/')[-1]
            grandparent = grandparent[0].capitalize() + grandparent[1:]
            for json_file in files:
                parent_title = splitext(json_file)[0]
                parent_title = parent_title[0].capitalize() + parent_title[1:]
                parent = Polygon.objects.filter(title=parent_title)
                if len(parent) > 1:
                    level = len(root.split('/')) - 1
                    parent = [
                        candidate
                        for candidate in parent
                        if candidate.level == level - 1
                    ]

                if len(parent) > 1:
                    for candidate in parent:
                        if candidate.parent \
                                and candidate.parent.title == grandparent:
                            parent = candidate
                            break
                else:
                    parent = parent[0] if parent else None
                with open(join(root, json_file)) as f:
                    data = json.load(f)
                    for feature in data['features']:
                        name = map_name(feature)
                        _, created = Polygon.objects.get_or_create(
                            title=name[0].capitalize() + name[1:],
                            parent=parent,
                            defaults={'geom': feature['geometry']}
                        )
                        if created:
                            print(name + ' was created')
                        else:
                            print(name + ' already exists')
