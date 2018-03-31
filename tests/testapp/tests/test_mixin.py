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