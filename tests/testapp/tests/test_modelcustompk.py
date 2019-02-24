import datetime
from django.test import TestCase
from tests.testapp.models import ModelCustomPK


class ModelCustomPKTestCase(TestCase):
    def test_update_created_at_before_create(self):
        instance = ModelCustomPK.objects.create()
        instance.refresh_from_db()
        self.assertTrue(isinstance(instance.created_at, datetime.datetime))

    def test_update_answer_after_create(self):
        instance = ModelCustomPK.objects.create()
        self.assertEqual(instance.answer, 42)
