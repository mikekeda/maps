from django.test import TestCase


class LoanedBookInstancesByUserListViewTest(TestCase):

    # Pages available for anonymous.
    def test_home_page(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'list-page.html')
