from typing import Optional

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.urls.exceptions import Resolver404
from django.contrib.sites.shortcuts import get_current_site


def bad_request(
    request: HttpRequest, exception: Optional[Exception] = None
) -> HttpResponse:
    return render(request, 'core/400.html', status=400)


def page_not_found(
    request: HttpRequest, exception: Resolver404 = None
) -> HttpResponse:
    current_site = get_current_site(request)
    path = f'{current_site}{request.path}'
    return render(request, 'core/404.html', {'path': path}, status=404)


def permission_denied(
    request: HttpRequest, exception: Optional[Exception] = None
) -> HttpResponse:
    return render(request, 'core/403.html', status=403)


def csrf_failure(request: HttpRequest, reason: str = '') -> HttpResponse:
    return render(request, 'core/403csrf.html', {'reason': reason}, status=403)


def server_error(request: HttpRequest) -> HttpResponse:
    return render(request, 'core/500.html', status=500)
