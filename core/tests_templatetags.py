from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from .templatetags.core_tags import update_param


class MapsViewTest(TestCase):
    def setUp(self):
        # Create usual user.
        test_user = User.objects.create_user(username='testuser',
                                             password='12345')
        test_user.save()

    def test_templatetags_update_param(self):
        resp = self.client.get(reverse('core:maps'))
        request = resp.wsgi_request
        result = update_param(request, 'p', '1')
        self.assertEqual(result, '/?p=1')
