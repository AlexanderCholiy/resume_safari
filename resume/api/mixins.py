from rest_framework import serializers

from user.models import User
from services.models import PendingUser


class UserValidationMixin:
    def validate_username_common(
        self: 'UserValidationMixin',
        username: str,
        current_username: str | None = None
    ) -> str:
        if current_username and username == current_username:
            return username

        for validator in User._meta.get_field('username').validators:
            validator(username)

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError('Имя пользователя уже занято.')

        pending_user = PendingUser.objects.filter(username=username).first()
        if pending_user:
            if pending_user.is_expired:
                pending_user.delete()
            else:
                raise serializers.ValidationError(
                    'Имя пользователя ожидает подтверждения.')

        return username

    def validate_email_common(
        self: 'UserValidationMixin',
        email: str,
        current_email: str | None = None
    ) -> str:
        if current_email and email == current_email:
            return email

        for validator in User._meta.get_field('email').validators:
            validator(email)

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email уже зарегистрирован.')

        pending_user = PendingUser.objects.filter(email=email).first()
        if pending_user:
            if pending_user.is_expired:
                pending_user.delete()
            else:
                raise serializers.ValidationError(
                    'Регистрация с этим email ожидает подтверждения.')

        return email
