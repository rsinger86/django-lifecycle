from django.test import TestCase

from django_lifecycle import hook


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
