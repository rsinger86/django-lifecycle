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