from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_PATH = os.path.join(BASE_DIR, '../user_website/')
PHOTO_PATH = os.path.join(BASE_DIR, 'media/photo')


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
        )
        user.is_admin = True
        user.save()
        return user


# Create your models here.
class User(AbstractBaseUser):
    email = models.EmailField(blank=False, unique=True, verbose_name="Email")
    nick = models.CharField(max_length=64, blank=True, verbose_name="Nick")
    desc = models.TextField(max_length=256, blank=True, verbose_name="description")
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    avatar = models.ImageField(blank=True, upload_to='avatar', verbose_name="Avatar")
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='date joined')

    # verify code for active and reset password
    verify_code = models.CharField(max_length=8, blank=True, verbose_name="verify code")
    # verify code valid time
    verify_time = models.DateTimeField(blank=True, null=True, verbose_name="verify created time")

    # relative path
    user_relative_path = models.CharField(max_length=32, default=None, blank=False, null=True, verbose_name='user website directory')
    photo_relative_path = models.CharField(max_length=32, default=None, blank=False, null=True, verbose_name='user photos directory')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def __unicode__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.user_relative_path is None or self.photo_relative_path is None:
            self.photo_relative_path = self.user_relative_path = "%04d" % self.id
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        if self.user_relative_path is not None:
            os.system('rm -r ' + self.user_path)
        if self.photo_relative_path is not None:
            os.system('rm -r ' + self.photo_path)
        super().delete(using, keep_parents)

    @property
    def is_staff(self):
        return self.is_admin  # only superuser can login admin

    @property
    def user_path(self):
        return os.path.join(USER_PATH, self.user_relative_path)

    @property
    def photo_path(self):
        return os.path.join(PHOTO_PATH, self.photo_relative_path)

    @property
    def photo_re_path(self):
        return os.path.join('media/photo', self.photo_relative_path)