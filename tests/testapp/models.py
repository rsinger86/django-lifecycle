import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from urlman import Urls

from django_lifecycle import AFTER_SAVE
from django_lifecycle import AFTER_UPDATE
from django_lifecycle import hook
from django_lifecycle.models import LifecycleModel


class CannotDeleteActiveTrial(Exception):
    pass


class CannotRename(Exception):
    pass


class Organization(LifecycleModel):
    name = models.CharField(max_length=100)


class UserAccount(LifecycleModel):
    username = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password = models.CharField(max_length=200)
    email = models.EmailField(null=True)
    password_updated_at = models.DateTimeField(null=True)
    joined_at = models.DateTimeField(null=True)
    has_trial = models.BooleanField(default=False)
    organization = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL)
    name_changes = models.IntegerField(default=0)
    configurations = models.JSONField(default=dict)

    status = models.CharField(
        default="active",
        max_length=30,
        choices=(("active", "Active"), ("banned", "Banned"), ("inactive", "Inactive")),
    )

    class urls(Urls):
        view = "/books/{self.pk}/"

    @hook("before_save", when="email", is_not=None)
    def lowercase_email(self):
        self.email = self.email.lower()

    @hook("before_create")
    def timestamp_joined_at(self):
        self.joined_at = timezone.now()

    @hook("after_create", on_commit=True)
    def do_after_create_jobs(self):
        # queue background job to process thumbnail image...
        mail.send_mail(
            "Welcome!",
            "Thank you for joining.",
            "from@example.com",
            ["to@example.com"],
        )

    @staticmethod
    def build_email_changed_body(old_email, new_email):
        return f"We've changed your email from {old_email} to {new_email}"

    @hook(AFTER_UPDATE, when="email", has_changed=True, on_commit=True)
    def notify_email_changed(self):
        mail.send_mail(
            subject="Email changed succesfully",
            message=self.build_email_changed_body(
                old_email=self.initial_value("email"), new_email=self.email
            ),
            from_email="from@example.com",
            recipient_list=["to@example.com"],
        )

    @hook("before_update", when="password", has_changed=True)
    def timestamp_password_change(self):
        self.password_updated_at = timezone.now()

    @hook("before_update", when="first_name", has_changed=True)
    @hook("before_update", when="last_name", has_changed=True)
    def count_name_changes(self):
        self.name_changes += 1

    @hook("before_delete", when="has_trial", was="*", is_now=True)
    def ensure_trial_not_active(self):
        raise CannotDeleteActiveTrial("Cannot delete trial user!")

    @hook("before_update", when="last_name", changes_to="Flanders")
    def ensure_last_name_is_not_changed_to_flanders(self):
        raise CannotRename("Oh, not Flanders. Anybody but Flanders.")

    @hook("after_update", when="organization.name", has_changed=True, on_commit=True)
    def notify_org_name_change(self):
        mail.send_mail(
            "The name of your organization has changed!",
            f"You organization is now named {self.organization.name}",
            "from@example.com",
            ["to@example.com"],
        )

    @hook(
        "after_update",
        when="organization.name",
        was="Hogwarts",
        is_now="Hogwarts Online",
    )
    def notify_user_they_were_moved_to_online_school(self):
        mail.send_mail(
            "You were moved to our online school!",
            f"You organization is now named {self.organization.name}",
            "from@example.com",
            ["to@example.com"],
        )

    @hook("after_delete")
    def email_deleted_user(self):
        mail.send_mail(
            "We have deleted your account",
            "Thank you for your time.",
            "from@example.com",
            ["to@example.com"],
        )

    @hook("after_update", when="status", was="active", is_now="banned")
    def email_banned_user(self):
        mail.send_mail(
            "You have been banned",
            "You may or may not deserve it.",
            "from@example.com",
            ["to@example.com"],
        )

    @hook("after_update", when_any=["first_name", "last_name"], has_changed=True)
    def email_user_about_name_change(self):
        mail.send_mail(
            "Update",
            "You changed your first name or your last name",
            "from@example.com",
            ["to@example.com"],
        )

    @cached_property
    def full_name(self):
        return self.first_name + " " + self.last_name


class Locale(models.Model):
    code = models.CharField(max_length=20)

    users = models.ManyToManyField(UserAccount)


class ModelCustomPK(LifecycleModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(null=True)
    answer = models.IntegerField(null=True, default=None)

    @hook("before_create")
    def timestamp_created_at(self):
        self.created_at = timezone.now()

    @hook("after_create")
    def answer_to_the_ultimate_question_of_life(self):
        self.answer = 42


class ModelWithGenericForeignKey(LifecycleModel):
    tag = models.SlugField()
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey("content_type", "object_id")

    @hook(AFTER_SAVE, when="content_object", has_changed=True, on_commit=True)
    def do_something(self):
        print("Hey there! I am using django-lifecycle")


class ModelThatFailsIfTriggered(LifecycleModel):
    @hook("after_create")
    def one_hook(self):
        raise RuntimeError
