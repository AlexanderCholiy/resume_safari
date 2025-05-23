from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.http import HttpRequest, HttpResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site

from .forms import CustomUserCreationForm
from user.models import User


def register(request: HttpRequest) -> HttpResponse:
    context = {'auth_page': True}
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.is_active = False
            user.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            link = request.build_absolute_uri(
                reverse(
                    'services:activate', kwargs={'uidb64': uid, 'token': token}
                )
            )

            current_site = get_current_site(request)
            subject = f'Подтверждение почты на {current_site}'
            message = (
                f'Привет, {user.username}!\n\n'
                f'Для активации аккаунта на сайте {current_site} перейдите '
                f'по ссылке:\n\n{link}'
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )
            return render(
                request, 'registration/email_confirmation_sent.html', context)
    else:
        form = CustomUserCreationForm()

    context['form'] = form
    return render(request, 'registration/register.html', context)


def activate(request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    context = {'auth_page': True}
    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'registration/activation_success.html', context)
    else:
        return render(request, 'registration/activation_invalid.html', context)
