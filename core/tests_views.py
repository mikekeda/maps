from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase


class MapsViewTest(TestCase):
    def setUp(self):
        # Create usual user.
        test_user = User.objects.create_user(username='testuser',
                                             password='12345')
        test_user.save()

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
