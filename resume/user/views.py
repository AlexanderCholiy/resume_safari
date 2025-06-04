from django.views.generic import ListView, DetailView
from django.contrib.auth import get_user_model
from django.db.models import QuerySet, Q, Count
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Resume, HardSkill, SoftSkill, Location, Position
from .constants import MAX_RESUME_PER_PAGE_ON_FRONT
from core.utils import build_grid, grid_contains_any_items


User = get_user_model()


class ResumeListView(ListView):
    model = Resume
    template_name = 'resume/index.html'
    paginate_by = MAX_RESUME_PER_PAGE_ON_FRONT

    def get_queryset(self: 'ResumeListView') -> 'QuerySet[Resume]':
        queryset = (
            Resume.objects
            .filter(user__is_active=True, is_published=True)
            .select_related('user', 'user__location', 'position')
            .order_by('-created_at', 'pk')
        )

        search_query = self.request.GET.get('q', '').strip()
        country = self.request.GET.get('country')
        category = self.request.GET.get('category')

        if search_query:
            queryset = queryset.filter(
                Q(user__last_name__contains=search_query) |
                Q(user__first_name__contains=search_query) |
                Q(user__patronymic__contains=search_query) |
                Q(user__username=search_query) |
                Q(position__position__contains=search_query)
            )

        if country:
            queryset = queryset.filter(user__location__country=country)

        if category:
            queryset = queryset.filter(position__category=category)

        return queryset

    def get_context_data(self: 'ResumeListView', **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_country'] = self.request.GET.get('country', '')
        context['selected_category'] = self.request.GET.get('category', '')

        context['countries'] = (
            Location.objects
            .filter(users__resume__is_published=True, users__is_active=True)
            .exclude(country__isnull=True)
            .exclude(country__exact='')
            .values_list('country', flat=True)
            .distinct()
            .order_by('country')
        )
        context['categories'] = (
            Position.objects
            .filter(resume__is_published=True, resume__user__is_active=True)
            .values_list('category', flat=True)
            .distinct()
            .order_by('category')
        )

        return context


class MyResumeListView(LoginRequiredMixin, ListView):
    model = Resume
    template_name = 'resume/index.html'
    paginate_by = MAX_RESUME_PER_PAGE_ON_FRONT
    login_url = 'login'

    def get_queryset(self: 'MyResumeListView') -> QuerySet:
        return (
            Resume.objects
            .filter(user=self.request.user)
            .select_related('user', 'user__location', 'position')
            .order_by('-is_published', '-created_at', 'pk')
        )


class ResumeDetailView(DetailView):
    model = Resume
    template_name = 'resume/resume_detail.html'
    context_object_name = 'resume'

    def get_queryset(self: 'ResumeDetailView') -> QuerySet[Resume]:
        base_qs = (
            Resume.objects
            .prefetch_related('educations', 'experiences')
            .select_related('user', 'user__location')
        )

        if self.request.user.is_authenticated:
            slug = self.kwargs.get('slug')
            if slug:
                try:
                    resume = Resume.objects.only('user_id').get(slug=slug)
                    if resume.user_id == self.request.user.id:
                        return base_qs
                except Resume.DoesNotExist:
                    pass

        return base_qs.filter(user__is_active=True, is_published=True)

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
