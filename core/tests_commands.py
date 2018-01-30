import sys
import types

from django.core.management import call_command
from django.utils.six import StringIO
from django.test import TestCase

from .models import Polygon


class MapsCommandsTest(TestCase):
    # Helpers functions.
    def test_commands_map_name(self):
        commands = __import__(
            'core.management.commands.import',
            fromlist=['']
        )

        feature = {'properties': {'name:en': 'name1'}}
        result = commands.map_name(feature)
        self.assertEqual(result, 'name1')

        feature = {'properties': {'name': 'name2'}}
        result = commands.map_name(feature)
        self.assertEqual(result, 'name2')

        feature = {'properties': {'nom': 'name3'}}
        result = commands.map_name(feature)
        self.assertEqual(result, 'name3')

        feature = {'properties': {'namelsad': 'name4'}}
        result = commands.map_name(feature)
        self.assertEqual(result, 'name4')

        feature = {'properties': {'provincia': 'name5'}}
        result = commands.map_name(feature)
        self.assertEqual(result, 'name5')

        feature = {'properties': {'DEPARTAMTO': 'name6'}}
        result = commands.map_name(feature)
        self.assertEqual(result, 'name6')

        feature = {'properties': {'prefecture': 'name7'}}
        result = commands.map_name(feature)
        self.assertEqual(result, 'name7')

        feature = {'properties': {'REGION': 'name8'}}
        result = commands.map_name(feature)
        self.assertEqual(result, 'name8')

        # Not existing key.
        feature = {'properties': {'existing_key': 'name9'}}
        result = commands.map_name(feature)
        self.assertEqual(result, '')

    def test_commands_get_files(self):
        commands = __import__(
            'core.management.commands.import',
            fromlist=['']
        )
        result = commands.get_files('geojson', '')
        self.assertIsInstance(result, types.GeneratorType)

        result = commands.get_files('geojson', file='world/united States')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 'geojson/world/united States')
        self.assertEqual(result[0][1], None)
        self.assertTrue(isinstance(result[0][2], list))

        result = commands.get_files('geojson', file='world/france.geojson')
        self.assertListEqual(
            result,
            [('geojson/world', None, ['france.geojson'])]
        )

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

        out = StringIO()
        sys.stdout = out
        call_command('import', file='world/united States/new Jersey.geojson')
        self.assertIn('Bergen County was created', out.getvalue())

        polygon_obj = Polygon.objects.filter(title="Texas").first()
        assert polygon_obj
        self.assertEqual(str(polygon_obj), "Texas")

    def test_commands_delete(self):
        out = StringIO()
        sys.stdout = out
        call_command('delete')
        self.assertIn('polygons were deleted', out.getvalue())
