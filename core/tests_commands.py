import sys

from django.contrib.auth.models import User
from django.core.management import call_command
from django.utils.six import StringIO
from django.test import TestCase


class MapsViewTest(TestCase):
    def setUp(self):
        # Create usual user.
        test_user = User.objects.create_user(username='testuser',
                                             password='12345')
        test_user.save()

    # manage.py commands.
    def test_commands_world_import(self):
        out = StringIO()
        sys.stdout = out
        call_command('import', file='world.geojson')
        self.assertIn('Zimbabwe was created', out.getvalue())

    def test_commands_us_import(self):
        out = StringIO()
        sys.stdout = out
        call_command('import', file='world/united States.geojson')
        self.assertIn('Puerto Rico was created', out.getvalue())

    def test_commands_delete(self):
        out = StringIO()
        sys.stdout = out
        call_command('delete')
        self.assertIn('polygons were deleted', out.getvalue())
