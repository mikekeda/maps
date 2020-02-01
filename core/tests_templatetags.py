from django.test import TestCase
from django.urls import reverse

from core.templatetags.core_tags import update_param


class MapsViewTest(TestCase):
    def test_templatetags_update_param(self):
        resp = self.client.get(reverse('core:maps'))
        request = resp.wsgi_request
        result = update_param(request, 'p', '1')
        self.assertEqual(result, '/?p=1')
        result = update_param(request, 'p')
        self.assertEqual(result, '/')
