from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .models import Resume, HardSkill, SoftSkill
from core.grid import build_grid, grid_contains_any_items


User = get_user_model()


def index(request: HttpRequest) -> HttpResponse:
    template_name = 'resume/index.html'
    resume_list = (
        Resume.objects
        .filter(user__is_active=True, is_published=True)
    ).select_related('user', 'user__location')
    context = {'resume_list': resume_list}
    return render(request, template_name, context)


def resume_detail(request: HttpRequest, slug: str) -> HttpResponse:
    template_name = 'resume/resume_detail.html'
    resume = get_object_or_404(
        (
            Resume.objects
            .select_related('user', 'user__location',)
            .prefetch_related('educations', 'experiences',)
        ),
        slug=slug, user__is_active=True, is_published=True,
    )

    hard_skills = build_grid(HardSkill.objects.filter(resume=resume))
    soft_skills = build_grid(SoftSkill.objects.filter(resume=resume))

    check_hard_slills = grid_contains_any_items(hard_skills)
    check_soft_slills = grid_contains_any_items(soft_skills)

    context = {
        'resume': resume,
        'hard_skills': hard_skills if check_hard_slills else None,
        'soft_skills': soft_skills if check_soft_slills else None,
    }
    return render(request, template_name, context)
