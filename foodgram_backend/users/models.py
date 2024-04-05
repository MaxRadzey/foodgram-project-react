from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from users.constants import ADMIN, ROLE_CHOICES, ROLE_MAX_LENGTH, USER


class UserManager(BaseUserManager):

    def create_user(
            self, username, email=None,
            password=None, **extra_fields
    ):
        if not username:
            raise ValueError('Поле username обязательное для заполнения')
        if not email:
            raise ValueError('Поле email обязательное для заполнения')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
            self,
            username,
            email=None,
            password=None,
            **extra_fields
    ):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):

    role = models.CharField(
        max_length=ROLE_MAX_LENGTH,
        choices=ROLE_CHOICES,
        default=USER,
    )

    @property
    def is_admin(self):
        return (
            self.role == ADMIN
            or self.is_superuser
            or self.is_staff
        )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class UserFollow(models.Model):

    user_id = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE
    )
    following_user_id = models.ForeignKey(
        User,
        related_name='followers',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user_id', 'following_user_id'],
                name='subscription_has_already_been_issued'
            ),
        ]

    def save(self, *args, **kwargs):
        if self.user_id == self.following_user_id:
            raise ValidationError('Нельзя подписываться на самого себя!')
        return super().save(*args, **kwargs)
