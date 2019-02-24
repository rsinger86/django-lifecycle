import uuid

from django.utils import timezone
from django.core import mail
from django.db import models
from django.utils.functional import cached_property
from django_lifecycle import hook
from django_lifecycle.models import LifecycleModel


class CannotDeleteActiveTrial(Exception):
    pass


class UserAccount(LifecycleModel):
    username = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password = models.CharField(max_length=200)
    email = models.EmailField(null=True)
    password_updated_at = models.DateTimeField(null=True)
    joined_at = models.DateTimeField(null=True)
    has_trial = models.BooleanField(default=False)

    status = models.CharField(
        default='active',
        max_length=30,
        choices=(
            ('active', 'Active'),
            ('banned', 'Banned'),
            ('inactive', 'Inactive')
        )
    )

    @hook('before_save', when='email', is_not=None)
    def lowercase_email(self):
        self.email = self.email.lower()

    @hook('before_create')
    def timestamp_joined_at(self):
        self.joined_at = timezone.now()

    @hook('after_create')
    def do_after_create_jobs(self):
        ## queue background job to process thumbnail image...
        mail.send_mail(
            'Welcome!', 'Thank you for joining.',
            'from@example.com', ['to@example.com'],
        )

    @hook('before_update', when='password', has_changed=True)
    def timestamp_password_change(self):
        self.password_updated_at = timezone.now()

    @hook('before_delete', when='has_trial', was='*', is_now=True)
    def ensure_trial_not_active(self):
        raise CannotDeleteActiveTrial('Cannot delete trial user!')

    @hook('after_delete')
    def email_deleted_user(self):
        mail.send_mail(
            'We have deleted your account', 'Thank you for your time.',
            'from@example.com', ['to@example.com'],
        )

    @hook('after_update', when='status', was='active', is_now='banned')
    def email_banned_user(self):
        mail.send_mail(
            'You have been banned', 'You may or may not deserve it.',
            'from@example.com', ['to@example.com'],
        )

    @cached_property
    def full_name(self):
        return self.first_name + ' ' + self.last_name


class Locale(models.Model):
    code = models.CharField(max_length=20)

    users = models.ManyToManyField(UserAccount)


class ModelCustomPK(LifecycleModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(null=True)
    answer = models.IntegerField(null=True, default=None)

    @hook('before_create')
    def timestamp_created_at(self):
        self.created_at = timezone.now()

    @hook('after_create')
    def answer_to_the_ultimate_question_of_life(self):
        self.answer = 42
