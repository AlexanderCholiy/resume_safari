from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .models import Resume


User = get_user_model()


def index(request: HttpRequest) -> HttpResponse:
    template_name = 'resume/index.html'
    resume_list = (
        Resume.objects
        .filter(user__is_active=True, is_published=True)
    )
    context = {'resume_list': resume_list}
    return render(request, template_name, context)


def resume_detail(request: HttpRequest, slug: str) -> HttpResponse:
    template_name = 'resume/resume_detail.html'
    resume = get_object_or_404(
        Resume,
        slug=slug, user__is_active=True, is_published=True,
    )
    context = {'resume': resume}
    return render(request, template_name, context)
