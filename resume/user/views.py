from django.views.generic import ListView, DetailView
from django.contrib.auth import get_user_model
from django.db.models import Prefetch, QuerySet
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import (
    Resume, HardSkill, SoftSkill, ResumeEducation, ResumeExperience)
from core.utils import build_grid, grid_contains_any_items
from .constants import MAX_RESUMES_PER_PAGE


User = get_user_model()


class ResumeListView(ListView):
    model = Resume
    template_name = 'resume/index.html'
    paginate_by = MAX_RESUMES_PER_PAGE

    def get_queryset(self: 'ResumeListView') -> 'QuerySet[Resume]':
        return (
            Resume.objects
            .filter(user__is_active=True, is_published=True)
            .select_related('user', 'user__location')
            .order_by('-created_at', 'pk')
        )


class MyResumeListView(LoginRequiredMixin, ListView):
    model = Resume
    template_name = 'resume/index.html'
    paginate_by = MAX_RESUMES_PER_PAGE
    login_url = 'login'

    def get_queryset(self: 'MyResumeListView') -> QuerySet:
        return (
            Resume.objects
            .filter(user=self.request.user)
            .select_related('user', 'user__location')
            .order_by('-created_at', 'pk')
        )


class ResumeDetailView(DetailView):
    model = Resume
    template_name = 'resume/resume_detail.html'
    context_object_name = 'resume'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self: 'ResumeDetailView') -> 'QuerySet[Resume]':
        return (
            Resume.objects
            .select_related('user', 'user__location')
            .prefetch_related(
                Prefetch(
                    'resume_educations',
                    queryset=ResumeEducation.objects.select_related(
                        'education')
                ),
                Prefetch(
                    'resume_experiences',
                    queryset=ResumeExperience.objects.select_related(
                        'experience')
                ),
            )
            .filter(user__is_active=True, is_published=True)
        )

    def get_context_data(self: 'ResumeDetailView', **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        resume = self.object

        hard_skills = build_grid(HardSkill.objects.filter(resume=resume))
        soft_skills = build_grid(SoftSkill.objects.filter(resume=resume))

        if grid_contains_any_items(hard_skills):
            context['hard_skills'] = hard_skills
        if grid_contains_any_items(soft_skills):
            context['soft_skills'] = soft_skills

        return context
