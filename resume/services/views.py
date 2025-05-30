from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator

from .forms import CustomUserCreationForm
from user.models import User
from .models import PendingUser
from .utils import send_activation_email


def register(request: HttpRequest) -> HttpResponse:
    context = {'auth_page': True}
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            pending_user = form.save()
            send_activation_email(pending_user, request)
            return render(
                request, 'registration/email_confirmation_sent.html', context)
    else:
        form = CustomUserCreationForm()

    context['form'] = form
    return render(request, 'registration/register.html', context)


def activate(request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
    context = {'auth_page': True}

    pending_user = None
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        pending_user = PendingUser.objects.get(pk=uid)
    except Exception:
        pass

    if (
        pending_user
        and default_token_generator.check_token(pending_user, token)
    ):
        User.objects.create(
            username=pending_user.username,
            email=pending_user.email,
            password=pending_user.password,  # hashed
            is_active=True
        )
        pending_user.delete()
        return render(request, 'registration/activation_success.html', context)
    return render(request, 'registration/activation_invalid.html', context)
