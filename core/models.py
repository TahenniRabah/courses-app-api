from django.db import models

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


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
        user = self.create_user(email, password, extra_fields=extra_fields)
        user.is_teacher = True
        user.save(using=self._db)

        return user

    def create_student(self, email, password, **extra_fields):
        user = self.create_user(email, password, extra_fields=extra_fields)
        user.is_student = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Course(models.Model):

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    # category = models. ==>un autre model
    created_at = models.DateTimeField(auto_now=True)

    class Level(models.IntegerChoices):
        DEB = 1, "DEBUTANT"
        INT = 2, "INTERMEDIAIRE"
        AVA = 3, "AVANCE"

    level = models.PositiveSmallIntegerField(
        choices=Level.choices,
        default=Level.DEB
    )


