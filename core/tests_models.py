from django.test import TestCase

from core.models import get_unique_slug, Category


class MapsModelsTest(TestCase):
    def test_models_catagory(self):
        slug = get_unique_slug(Category, "Test title")
        self.assertEqual(slug, "test-title")

        category_obj = Category(title="Test title")
        category_obj.save()
        self.assertEqual(category_obj.slug, "test-title")
        self.assertEqual(str(category_obj), "Test title")

        slug = get_unique_slug(Category, "Test title")
        self.assertEqual(slug, "test-title-1")
