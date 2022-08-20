from ckeditor_uploader.fields import RichTextUploadingField

from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.contrib.postgres.fields import ArrayField
from django.db import models

from phonenumber_field.modelfields import PhoneNumberField

from taggit.managers import TaggableManager


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(db_index=True, max_length=255, unique=False, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    second_name = models.CharField(max_length=100, blank=True, null=True)
    phone = PhoneNumberField(max_length=15, unique=True, null=True, blank=False)
    sub_phone = ArrayField(PhoneNumberField(max_length=15), unique=True, blank=True, null=True)
    explanation_by_phone = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(max_length=50, db_index=True, unique=True)
    sub_email = ArrayField(models.EmailField(max_length=50), unique=True, blank=True, null=True)
    explanation_by_email = models.CharField(max_length=30, blank=True, null=True)
    website = ArrayField(models.CharField(max_length=100), blank=True, null=True)
    tags = TaggableManager(blank=True)
    event_birthday = ArrayField(models.CharField(max_length=80), blank=True, null=True)
    location = ArrayField(models.CharField(max_length=100), blank=True, null=True)
    life_work = ArrayField(models.CharField(max_length=100), blank=True, null=True)
    education = ArrayField(models.CharField(max_length=100), blank=True, null=True)
    soc_network = ArrayField(models.CharField(max_length=100), blank=True, null=True)
    username = models.CharField(db_index=True, max_length=255, unique=False)
    email = models.EmailField(db_index=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    objects = UserManager()

    def __str__(self):
        return self.email


class NewPerson(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField()
    work_experience = models.TextField()

    def __str__(self):
        return self.first_name


def user_directory_path(instance, filename):
    return 'upload_file/user_{0}/{1}'.format(instance.first_name, filename)


class ContactsUser(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200, blank=True)
    phone = PhoneNumberField(unique=True, null=False, blank=False)
    email = models.EmailField(null=True, blank=True)
    photo = models.ImageField(null=True, blank=True)
    notes = RichTextUploadingField(null=True, blank=True)
    education = ArrayField(models.CharField(max_length=100), blank=True, null=True)
    website = ArrayField(models.CharField(max_length=100), blank=True, null=True)
    upload_file = models.FileField(upload_to=user_directory_path, max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    id_user_creator = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = TaggableManager(blank=True)

    def __str__(self):
        return self.first_name


# -------------add contacts from google and facebook -----------
class ContactsGF(models.Model):
    id_user_creator = models.ForeignKey(User, on_delete=models.CASCADE)
    # id_email = models.EmailField(max_length=50)  # поле не нужно, оно будет дублироваться в User и в этой модели
    contacts = models.JSONField(blank=True, null=True)
    type_contact = models.CharField(null=False, max_length=15)

    def __str__(self):
        return self.type_contact


class OtherPerson(models.Model):
    first_name = models.CharField(max_length=20, blank=True, null=True)
    last_name = models.CharField(max_length=20, blank=True, null=True)
    type = models.CharField(max_length=20)
    email = models.EmailField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.first_name


class TelegramChatsView(models.Model):
    title = models.TextField(blank=True)
    article = models.TextField(blank=True)
    time_of_public = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
