from django.db import models
from django.test import TestCase

from django_lifecycle import hook, LifecycleModelMixin, AFTER_CREATE
from django_lifecycle.conditions import Always
from django_lifecycle.decorators import DjangoLifeCycleException
from django_lifecycle.priority import HIGHEST_PRIORITY, LOWER_PRIORITY
from tests.testapp.models import ModelThatFailsIfTriggered


class DecoratorTests(TestCase):
    def test_decorate_with_multiple_hooks(self):
        class FakeModel(object):
            @hook("after_create")
            @hook("after_delete")
            def multiple_hooks(self):
                pass

            @hook("after_create")
            def one_hook(self):
                pass

        instance = FakeModel()
        self.assertEqual(len(instance.multiple_hooks._hooked), 2)
        self.assertEqual(len(instance.one_hook._hooked), 1)

    def test_priority_hooks(self):
        class FakeModel(LifecycleModelMixin, models.Model):
            @hook(AFTER_CREATE)
            def mid_priority(self):
                pass

            @hook(AFTER_CREATE, priority=HIGHEST_PRIORITY)
            def top_priority(self):
                pass

            @hook(AFTER_CREATE, priority=LOWER_PRIORITY)
            def lowest_priority(self):
                pass

        hooked_methods = FakeModel()._get_hooked_methods(AFTER_CREATE)
        hooked_method_names = [method.name for method in hooked_methods]

        expected_method_names = ["top_priority", "mid_priority", "lowest_priority"]
        self.assertListEqual(expected_method_names, hooked_method_names)

    def test_condition_cannot_be_mixed_with_legacy_parameters(self):
        with self.assertRaises(DjangoLifeCycleException):
            hook(AFTER_CREATE, condition=Always(), has_changed=True)

    def test_no_condition_or_legacy_parameters_is_valid(self):
        hook(AFTER_CREATE)  # no exception is raised
