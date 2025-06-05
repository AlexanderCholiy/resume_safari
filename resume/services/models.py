from core.config import WebConfig
from django.db import models
from django.utils import timezone

from .constants import MAX_PASSWORD_LEN, MAX_USERNAME_LEN


class PendingUser(models.Model):
    username = models.CharField(
        'Имя пользователя', max_length=MAX_USERNAME_LEN, unique=True
    )
    email = models.EmailField('Email', unique=True)
    password = models.CharField(max_length=MAX_PASSWORD_LEN)  # hashed

    # Эти поля необходимы для генерации токена для завершения регистрации:
    last_login = models.DateTimeField('Дата регистрации', default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'пользователь для регистрации'
        verbose_name_plural = 'Регистрация пользоватей'

    def __str__(self: 'PendingUser') -> str:
        return self.username

    def get_email_field_name(self: 'PendingUser') -> str:
        return 'email'

    @property
    def is_expired(self: 'PendingUser') -> bool:
        """Проверка, актуальная ли регистрация для этого пользователя."""
        return (
            timezone.now() - self.last_login > WebConfig.ACCESS_TOKEN_LIFETIME
        )
