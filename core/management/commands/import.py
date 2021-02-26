from __future__ import annotations

import json
from os import walk, listdir
from os.path import join, splitext, isfile

from django.core.management import BaseCommand

from core.models import Polygon


def map_name(feature: dict[str, dict]) -> str:
    """Fix title for some json files."""
    name = ""
    if "name:en" in feature["properties"]:
        # for slovakia.geojson
        name = feature["properties"]["name:en"]
    elif "name" in feature["properties"]:
        name = feature["properties"]["name"]
    elif "nom" in feature["properties"]:
        # for world/france.geojson
        name = feature["properties"]["nom"]
    elif "namelsad" in feature["properties"]:
        # for united States folder (new Jersey.geojson)
        name = feature["properties"]["namelsad"]
    elif "provincia" in feature["properties"]:
        # for argentina.geojson
        name = feature["properties"]["provincia"]
    elif "DEPARTAMTO" in feature["properties"]:
        # for argentina folder
        name = feature["properties"]["DEPARTAMTO"]
    elif "prefecture" in feature["properties"]:
        # for mongolia.geojson
        name = feature["properties"]["prefecture"]
    elif "REGION" in feature["properties"]:
        # for nepal.geojson
        name = feature["properties"]["REGION"]

    return name


def get_files(path: str, file: str):
    """Get all files for import."""
    if file:
        if isfile(join(path, file)):
            root = path
            subdir = file.rsplit("/", 1)
            if len(subdir) > 1:
                root += "/" + subdir[0]
            need_process = [(root, None, [file.split("/")[-1]])]
        else:
            root = path + "/" + file
            need_process = [
                (root, None, [f for f in listdir(root) if isfile(join(root, f))])
            ]
    else:
        need_process = walk(path)

    return need_process


# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    # Show this when the user types help
    help = "Import Polygons from geojson"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("file", nargs="?", type=str)

    def handle(self, *args, **options):
        self.stdout.write("Started Polygons import")

        for root, _, files in get_files("geojson", options["file"]):
            grandparent = root.split("/")[-1]
            grandparent = grandparent[0].capitalize() + grandparent[1:]
            for json_file in files:
                # Get parent title.
                parent = splitext(json_file)[0]
                parent = parent[0].capitalize() + parent[1:]

                # Get parent.
                parent = Polygon.objects.filter(title=parent)
                if len(parent) > 1:
                    parent = [
                        candidate
                        for candidate in parent
                        if candidate.level == len(root.split("/")) - 2
                    ]

                if len(parent) > 1:
                    for candidate in parent:
                        if candidate.parent and candidate.parent.title == grandparent:
                            parent = candidate
                            break
                else:
                    parent = parent[0] if parent else None

                with open(join(root, json_file)) as f:
                    for feature in json.load(f).get("features", []):
                        name = map_name(feature)
                        _, created = Polygon.objects.get_or_create(
                            title=name[0].capitalize() + name[1:],
                            parent=parent,
                            defaults={"geom": feature["geometry"]},
                        )
                        if created:
                            print(name + " was created")
                        else:
                            print(name + " already exists")
