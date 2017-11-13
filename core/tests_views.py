import sys

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.management import call_command
from django.http import Http404
from django.utils.six import StringIO
from django.test import TestCase

from .models import Polygon
from .views import map_latest_entry, range_data


class MapsViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(MapsViewTest, cls).setUpClass()

        # Create usual user.
        test_user = User.objects.create_user(username='testuser',
                                             password='12345')
        test_user.save()

        # Import world.geojson
        out = StringIO()
        sys.stdout = out
        call_command('import', file='world.geojson')

        # Import ukraine.geojson
        out = StringIO()
        sys.stdout = out
        call_command('import', file='world/ukraine.geojson')

        # Import argentina.geojson
        out = StringIO()
        sys.stdout = out
        call_command('import', file='world/argentina.geojson')

    # Helpers functions.
    def test_views_map_latest_entry(self):
        with self.assertRaises(Http404):
            map_latest_entry(None, 'not-exists')

    def test_views_range_data(self):
        map_obj = {
            'data_min': 0,
            'data_max': 10,
            'logarithmic_scale': False,
            'grades': 5,
            'start_color': '352515',
            'end_color': '000000',
        }
        result = range_data(map_obj)
        # Convert to set.
        result = {tuple(item) for item in result}
        self.assertEqual(len(result), 5)
        self.assertEqual(set(result), {
            (0.0, '0b0805'),
            (2.0, '160f09'),
            (4.0, '20170d'),
            (6.0, '2b1e11'),
            (8.0, '352515')
        })

        # Logarithmic scale.
        map_obj = {
            'data_min': -2.3,
            'data_max': 9.7,
            'logarithmic_scale': True,
            'grades': 4,
            'start_color': 'dff0d8',
            'end_color': 'fcf8e3',
        }
        result = range_data(map_obj)
        # Convert to set.
        result = {tuple(item) for item in result}
        self.assertEqual(len(result), 4)
        self.assertEqual(set(result), {
            (-2.3, 'f4f6e0'),
            (-1.4011710778840583, 'edf4dd'),
            (0.3055512754639893, 'e6f2da'),
            (3.546325042023046, 'dff0d8')
        })

    # Pages available for anonymous.
    def test_views_home(self):
        resp = self.client.get(reverse('core:maps'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'list-page.html')

    def test_views_charts(self):
        resp = self.client.get(reverse('core:charts'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'list-page.html')

    def test_views_user_maps(self):
        resp = self.client.get(reverse('core:user_maps',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'list-page.html')

    def test_views_user_charts(self):
        resp = self.client.get(reverse('core:user_charts',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'list-page.html')

    def test_views_world(self):
        resp = self.client.get('/world/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'map.html')

    def test_views_polygon(self):
        # Doesn't exists yet.
        resp = self.client.get(reverse('core:polygons') + 'Ukraine')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'map.html')

    def test_views_polygon_second_lvl(self):
        resp = self.client.get(
            reverse('core:polygons') + 'Argentina/Buenos Aires'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'map.html')

    def test_views_polygon_export(self):
        polygon = Polygon.objects.get(title='Ukraine')

        resp = self.client.get(reverse('core:polygon_export',
                                       kwargs={'pk': polygon.pk}))
        self.assertRedirects(
            resp,
            '/login?next=/polygon/' + str(polygon.pk) + '/geojson'
        )

        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('core:polygon_export',
                                       kwargs={'pk': polygon.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_views_get_polygons(self):
        polygon = Polygon.objects.get(title='Ukraine')

        resp = self.client.get(reverse('core:get_polygons',
                                       kwargs={'parent_id': polygon.pk}))
        self.assertRedirects(
            resp,
            '/login?next=/api/get-polygons/' + str(polygon.pk)
        )

        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('core:get_polygons',
                                       kwargs={'parent_id': polygon.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_views_map(self):
        resp = self.client.get(reverse('core:map',
                                       kwargs={'slug': 'not-exists'}))
        self.assertEqual(resp.status_code, 404)
        self.assertTemplateUsed(resp, '404.html')

    def test_views_chart(self):
        resp = self.client.get(reverse('core:chart',
                                       kwargs={'slug': 'not-exists'}))
        self.assertEqual(resp.status_code, 404)
        self.assertTemplateUsed(resp, '404.html')

    def test_views_about(self):
        resp = self.client.get(reverse('core:about'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'about.html')

    def test_views_login(self):
        resp = self.client.get(reverse('core:login'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'login.html')

    def test_views_logout(self):
        resp = self.client.get(reverse('core:logout'))
        self.assertRedirects(resp, '/login?next=/logout')
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('core:logout'))
        self.assertRedirects(resp, reverse('core:login'))

    def test_views_sitemap(self):
        resp = self.client.get('/sitemap.xml')
        self.assertEqual(resp.status_code, 200)

    # Pages available only for registered users.
    def test_views_add_map(self):
        resp = self.client.get(reverse('core:add_map'))
        self.assertRedirects(resp, '/login?next=/add/map')
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('core:add_map'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'map-form.html')
