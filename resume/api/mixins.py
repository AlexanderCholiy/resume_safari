from rest_framework import serializers
from services.models import PendingUser
from user.models import User


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

    def validate_education_data(
        self: 'UserValidationMixin', data: dict
    ) -> None:
        print(data)
        if (
            not data.get('institution')
            or not data.get('degree')
            or not data.get('field_of_study')
            or not data.get('start_date')
        ):
            raise serializers.ValidationError(
                'Каждое образование должно содержать institution, degree, '
                'field_of_study и start_date.'
            )

    def validate_experience_data(
        self: 'UserValidationMixin', data: dict
    ) -> None:
        if (
            not data.get('company')
            or not data.get('position')
            or not data.get('start_date')
        ):
            raise serializers.ValidationError(
                'Каждый опыт работы должен содержать company, position '
                'и start_date.'
            )
