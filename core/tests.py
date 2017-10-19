import sys

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.management import call_command
from django.utils.six import StringIO
from django.test import TestCase


class LoanedBookInstancesByUserListViewTest(TestCase):
    def setUp(self):
        # Create usual user.
        test_user = User.objects.create_user(username='testuser',
                                             password='12345')
        test_user.save()

    # Pages available for anonymous.
    def test_home_page(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'list-page.html')

    def test_charts_page(self):
        resp = self.client.get('/charts')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'list-page.html')

    def test_user_maps_page(self):
        resp = self.client.get(reverse('core:user_maps',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'list-page.html')

    def test_user_charts_page(self):
        resp = self.client.get(reverse('core:user_charts',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'list-page.html')

    def test_world_page(self):
        resp = self.client.get('/world/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'map.html')

    def test_about_page(self):
        resp = self.client.get('/about')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'about.html')

    def test_login_page(self):
        resp = self.client.get('/login')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'login.html')

    def test_sitemap_page(self):
        resp = self.client.get('/sitemap.xml')
        self.assertEqual(resp.status_code, 200)

    # Pages available only for registered users.
    def test_add_map_page(self):
        resp = self.client.get('/add/map')
        self.assertRedirects(resp, '/login?next=/add/map')
        self.client.login(username='testuser', password='12345')
        resp = self.client.get('/add/map')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'map-form.html')

    # manage.py commands.
    def test_world_import_command(self):
        out = StringIO()
        sys.stdout = out
        call_command('import', file='world.geojson')
        self.assertIn('Zimbabwe was created', out.getvalue())

    def test_us_import_command(self):
        out = StringIO()
        sys.stdout = out
        call_command('import', file='world/united States.geojson')
        self.assertIn('Puerto Rico was created', out.getvalue())

    def test_delete_command(self):
        out = StringIO()
        sys.stdout = out
        call_command('delete')
        self.assertIn('polygons were deleted', out.getvalue())
