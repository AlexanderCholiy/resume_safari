from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password

from .models import PendingUser
from user.models import User


class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput,
        help_text='Пароль должен содержать минимум 8 символов.',
    )
    password2 = forms.CharField(
        label='Повторите пароль',
        widget=forms.PasswordInput,
    )

    class Meta:
        model = PendingUser
        fields = ['username', 'email']

    def clean_username(self: 'CustomUserCreationForm') -> str:
        username = self.cleaned_data['username']

        for validator in User._meta.get_field('username').validators:
            validator(username)

        if User.objects.filter(username=username).exists():
            raise ValidationError('Имя пользователя уже занято.')

        pending_user = PendingUser.objects.filter(username=username).first()
        if pending_user:
            if pending_user.is_expired:
                pending_user.delete()
            else:
                raise ValidationError(
                    'Имя пользователя ожидает подтверждения.')

        return username

    def clean_email(self: 'CustomUserCreationForm') -> str:
        email = self.cleaned_data['email']

        for validator in User._meta.get_field('email').validators:
            validator(email)

        if User.objects.filter(email=email).exists():
            raise ValidationError('Email уже зарегистрирован.')

        pending_user = PendingUser.objects.filter(email=email).first()
        if pending_user:
            if pending_user.is_expired:
                pending_user.delete()
            else:
                raise ValidationError(
                    'Регистрация с этим email ожидает подтверждения.')

        return email

    def clean(self: 'CustomUserCreationForm') -> None:
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2:
            if password1 != password2:
                raise ValidationError('Пароли не совпадают.')

            validate_password(password1)

    def save(
        self: 'CustomUserCreationForm', commit: bool = True
    ) -> PendingUser:
        instance = super().save(commit=False)
        raw_password = self.cleaned_data['password1']
        instance.password = make_password(raw_password)
        if commit:
            instance.save()
        return instance
