import os
import uuid

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.db import models


def course_document_file_path(instance, filename):
    """Generate file path for new recipe image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join('uploads', 'course', filename)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('user must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        return user

    def create_teacher(self, email, password, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.role = 1
        user.save(using=self._db)

        return user

    def create_student(self, email, password, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.role = 2
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    class Role(models.IntegerChoices):
        TEACHER = 1, "Professeur"
        STUDENT = 2, "Etudiant"

    role = models.PositiveSmallIntegerField(
        choices=Role.choices,
        default=Role.STUDENT
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses')
    # category = models.ManyToManyField('Category') # ==>un autre model
    document = models.FileField(null=True, upload_to=course_document_file_path)

    class Level(models.IntegerChoices):
        DEB = 1, "DEBUTANT"
        INT = 2, "INTERMEDIAIRE"
        AVA = 3, "AVANCE"

    level = models.PositiveSmallIntegerField(
        choices=Level.choices,
        default=Level.DEB
    )

    def __str__(self):
        return self.title
