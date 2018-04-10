import datetime
from unittest.mock import MagicMock
from django.test import TestCase
from django.core import mail
from tests.testapp.models import UserAccount, CannotDeleteActiveTrial



class UserAccountTestCase(TestCase):

    @property
    def stub_data(self):
        return {
            'username': 'homer.simpson',
            'first_name': 'Homer',
            'last_name': 'Simpson',
            'password': 'donuts'
        }
        
        
    def test_update_joined_at_before_create(self):
        account = UserAccount.objects.create(**self.stub_data)
        account.refresh_from_db()
        self.assertTrue( isinstance(account.joined_at, datetime.datetime) )


    def test_send_welcome_email_after_create(self):
        account = UserAccount.objects.create(**self.stub_data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Welcome!')



    def test_email_banned_user_after_update(self):
        account = UserAccount.objects.create(status='active', **self.stub_data)
        account.refresh_from_db()
        mail.outbox = []
        account.status = 'banned'
        account.save()
        self.assertEqual(mail.outbox[0].subject, 'You have been banned')
        
              
    def test_update_password_updated_at_during_update(self):
        account = UserAccount.objects.create(**self.stub_data)
        account.refresh_from_db()
        account.password='maggie'
        account.save()
        account.refresh_from_db()
        
        self.assertTrue( 
            isinstance(account.password_updated_at, datetime.datetime) 
        )


    def test_ensure_trial_not_active_before_delete(self):
        account = UserAccount.objects.create(**self.stub_data)
        account.has_trial = True 
        account.save()
        self.assertRaises(CannotDeleteActiveTrial, account.delete)

        
    def test_email_after_delete(self):
        account = UserAccount.objects.create(**self.stub_data)
        mail.outbox = []
        account.delete()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'We have deleted your account')


    def test_lowercase_email(self):
        data = self.stub_data
        data['email'] = 'Homer.Simpson@SpringfieldNuclear.com'
        account = UserAccount.objects.create(**data)
        self.assertEqual(account.email, 'homer.simpson@springfieldnuclear.com')


    def test_skip_hooks(self):
        """
            Hooked method that auto-lowercases email should be skipped.
        """
        account = UserAccount.objects.create(**self.stub_data)
        account.email = 'Homer.Simpson@springfieldnuclear'
        account.save(skip_hooks=True)
        self.assertEqual(account.email, 'Homer.Simpson@springfieldnuclear')