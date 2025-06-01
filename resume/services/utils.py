from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpRequest

from .models import PendingUser


def send_activation_email(
    pending_user: PendingUser, request: HttpRequest
) -> None:
    token = default_token_generator.make_token(pending_user)
    uid = urlsafe_base64_encode(force_bytes(pending_user.pk))
    activation_path = reverse(
        'services:activate', kwargs={'uidb64': uid, 'token': token})
    activation_link = request.build_absolute_uri(activation_path)

    current_site = get_current_site(request)
    subject = f'Подтверждение почты на {current_site.name}'

    message = (
        f'Здравствуйте, {pending_user.username}!\n\n'
        f'Вы указали этот адрес при регистрации на {current_site.domain}.\n'
        f'Для подтверждения перейдите по ссылке:\n{activation_link}\n\n'
        f'Срок действия ссылки — 1 день.\n\n'
        f'Если вы не регистрировались — просто проигнорируйте это письмо.'
    )
    send_mail(
        subject, message, settings.DEFAULT_FROM_EMAIL, [pending_user.email])
