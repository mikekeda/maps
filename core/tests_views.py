import sys

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.management import call_command
from django.utils.six import StringIO
from django.test import TestCase

from .models import Polygon
from .views import range_data


class MapsViewTest(TestCase):
    def setUp(self):
        # Create usual user.
        test_user = User.objects.create_user(username='testuser',
                                             password='12345')
        test_user.save()

    # Helpers functions.
    def test_views_range_data(self):
        map_obj = {
            'data_min': 0,
            'data_max': 10,
            'logarithmic_scale': False,
            'grades': 5,
            'start_color': 'f5f5f5',
            'end_color': '331155',
        }
        result = range_data(map_obj)
        # Convert to set.
        result = {tuple(item) for item in result}
        self.assertEqual(len(result), 5)
        self.assertEqual(set(result), {
            (0.0, '5a3f75'),
            (2.0, '816d95'),
            (4.0, 'a89ab5'),
            (6.0, 'cfc8d5'),
            (8.0, 'f5f5f5')
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
        self.assertEqual(resp.status_code, 404)
        self.assertTemplateUsed(resp, '404.html')

        out = StringIO()
        sys.stdout = out
        call_command('import', file='world.geojson')
        self.assertIn('Zimbabwe was created', out.getvalue())

        # Import ukraine.geojson
        out = StringIO()
        sys.stdout = out
        call_command('import', file='world/ukraine.geojson')
        self.assertIn('Zhytomyr Oblast was created', out.getvalue())

        polygon = Polygon.objects.filter(title='Ukraine')
        self.assertEqual(len(polygon), 1)

        resp = self.client.get(reverse('core:polygons') + 'Ukraine')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'map.html')

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
