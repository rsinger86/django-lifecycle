import django
from django.test import TestCase
from tests.testapp.models import ModelWithGenericForeignKey
from tests.testapp.models import Organization


class TestCaseMixin:
    """Dummy implementation for Django >= 4.0"""


class ModelWithGenericForeignKeyTestCase(TestCaseMixin, TestCase):
    def test_saving_model_with_generic_fk_doesnt_break(self):
        evil_corp = Organization.objects.create(name="Evil corp.")
        good_corp = Organization.objects.create(name="Good corp.")
        model = ModelWithGenericForeignKey.objects.create(
            tag="evil-corp",
            content_object=evil_corp,
        )

        # One hook should be executed
        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            model.tag = "good-corp"
            model.content_object = good_corp
            model.save()

        self.assertEqual(len(callbacks), 1)
