from django.core.management import BaseCommand

from core.models import Polygon


# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    # Show this when the user types help
    help = "Delete all Polygons"

    def handle(self, *args, **options):
        self.stdout.write("Started Polygons deleting")
        deleted = Polygon.objects.all().delete()
        self.stdout.write("{} polygons were deleted".format(deleted[0]))
