from django.core import mail
from django.test import TestCase

from django_capture_on_commit_callbacks import capture_on_commit_callbacks

from tests.testapp.models import Post

class PostTestCase(TestCase):
    databases = ("default", "other",)

    @property
    def stub_data(self):
        return {
            "content": "plain text"
        }

    def test_send_notification_mail_after_create(self):
        with capture_on_commit_callbacks(execute=True, using="other") as callbacks:
            Post.objects.create(**self.stub_data)
        
        self.assertEquals(len(callbacks), 1, msg=f"{callbacks}")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "New Post!")