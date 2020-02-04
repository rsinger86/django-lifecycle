from django.test import TestCase

from tests.testapp.models import Companies


class Issue36TestCase(TestCase):

    def test_companies_model_hooks(self):
        c = Companies.objects.create(name='initial_name')
        self.assertEqual(c.name, 'test_name_on_create')  # Because of `before_create` hook

        c.name = 'test2'
        c.save()

        c.refresh_from_db()
        self.assertEqual(c.name, 'test_name_on_update')  # Because of `before_update`
