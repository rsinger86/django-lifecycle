import datetime
from unittest.mock import MagicMock
from django.test import TestCase
from django.core import mail
from tests.testapp.models import UserAccount



class LifecycleMixinTests(TestCase):

    def setUp(self):
        UserAccount.objects.all().delete()

        
    @property
    def stub_data(self):
        return {
            'username': 'homer.simpson',
            'first_name': 'Homer',
            'last_name': 'Simpson',
            'password': 'donuts'
        }

    
    def test_has_changed(self):
        data = self.stub_data
        data['username'] = 'Joe'
        UserAccount.objects.create(**data)
        useraccount = UserAccount.objects.get()
        self.assertFalse(useraccount.has_changed('username'))
        useraccount.username = 'Josephine'
        self.assertTrue(useraccount.has_changed('username'))


    def test_initial_value(self):
        data = self.stub_data
        data['username'] = 'Joe'
        UserAccount.objects.create(**data)
        useraccount = UserAccount.objects.get()
        self.assertFalse(useraccount.has_changed('username'))
        useraccount.username = 'Josephine'
        self.assertEqual(useraccount.initial_value('username'), 'Joe')


    def test_has_changed_specs(self):
        specs =  {
            'when': 'first_name',
            'has_changed': True
        }

        data = self.stub_data
        data['first_name'] = 'Homer'
        UserAccount.objects.create(**data)
        useraccount = UserAccount.objects.get()

        self.assertFalse(useraccount._check_has_changed(specs))
        useraccount.first_name = 'Ned'
        self.assertTrue(useraccount._check_has_changed(specs))


    def test_value_transition_specs(self):
        specs =  {
            'when': 'first_name',
            'was': 'Homer',
            'is_now': 'Ned'
        }

        data = self.stub_data
        data['first_name'] = 'Homer'
        UserAccount.objects.create(**data)
        useraccount = UserAccount.objects.get()

        self.assertFalse(useraccount._check_value_transition(specs))
        useraccount.first_name = 'Ned'
        self.assertTrue(useraccount._check_value_transition(specs))


    def test_value_transition_specs_wildcard(self):
        specs =  {
            'when': 'first_name',
            'was': '*',
            'is_now': 'Ned'
        }

        data = self.stub_data
        data['first_name'] = 'Homer'
        UserAccount.objects.create(**data)
        useraccount = UserAccount.objects.get()

        self.assertFalse(useraccount._check_value_transition(specs))
        useraccount.first_name = 'Ned'
        self.assertTrue(useraccount._check_value_transition(specs))


    def test_is_not_condition_should_pass(self):
        specs =  {
            'when': 'first_name',
            'is_not': 'Ned'
        }

        data = self.stub_data
        data['first_name'] = 'Homer'
        UserAccount.objects.create(**data)
        useraccount = UserAccount.objects.get()
        self.assertTrue(useraccount._check_is_not_condition(specs))


    def test_is_not_condition_should_not_pass(self):
        specs =  {
            'when': 'first_name',
            'is_not': 'Ned'
        }

        data = self.stub_data
        data['first_name'] = 'Ned'
        UserAccount.objects.create(**data)
        useraccount = UserAccount.objects.get()
        self.assertFalse(useraccount._check_is_not_condition(specs))


    def test_should_not_call_cached_property(self):
        """
            full_name is cached_property. Accessing _potentially_hooked_methods
            should not call it incidentally.
        """
        data = self.stub_data
        data['first_name'] = 'Bart'
        data['last_name'] = 'Simpson'
        account = UserAccount.objects.create(**data)
        account._potentially_hooked_methods
        account.first_name = 'Bartholomew'
        # Should be first time this property is accessed...
        self.assertEqual(account.full_name, 'Bartholomew Simpson')


    def test_comparison_state_should_reset_after_save(self):
        data = self.stub_data
        data['first_name'] = 'Marge'
        data['last_name'] = 'Simpson'
        account = UserAccount.objects.create(**data)
        account.first_name = 'Maggie'
        self.assertTrue(account.has_changed('first_name'))
        account.save()
        self.assertFalse(account.has_changed('first_name'))