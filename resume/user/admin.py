from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.db.models.query import QuerySet

from .constants import (MAX_EDUCATIONS_PER_PAGE, MAX_EXPERIANCE_PER_PAGE,
                        MAX_LOCATIONS_PER_PAGE, MAX_POSITION_PER_PAGE,
                        MAX_RESUMES_PER_PAGE, MAX_SKILLS_PER_PAGE,
                        MAX_USERS_PER_PAGE)
from .models import (Education, Experience, HardSkill, HardSkillName, Location,
                     Position, Resume, ResumeEducation, ResumeExperience,
                     SoftSkill, SoftSkillName, User)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'patronymic',
    )
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
        'patronymic',
    )
    list_filter = ('is_staff', 'is_active')
    ordering = ('username',)
    list_per_page = MAX_USERS_PER_PAGE
    filter_horizontal = ('user_permissions', 'groups',)
    list_editable = (
        'first_name',
        'last_name',
        'patronymic'
    )
    autocomplete_fields = ('location',)

    def get_queryset(
        self: 'UserAdmin', request: WSGIRequest
    ) -> QuerySet:
        queryset = super().get_queryset(request)
        return queryset.select_related('location',)


@admin.register(Location)
class LocatiomAdmin(admin.ModelAdmin):
    list_display = ('pk', 'country', 'city',)
    search_fields = ('city',)
    list_filter = ('country',)
    list_per_page = MAX_LOCATIONS_PER_PAGE


@admin.register(Position)
class PostionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'category', 'position',)
    search_fields = ('category', 'position',)
    list_filter = ('category',)
    list_per_page = MAX_POSITION_PER_PAGE


@admin.register(HardSkillName)
class HardSkillNameAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'description',)
    search_fields = ('name',)
    list_editable = ('description',)
    list_per_page = MAX_SKILLS_PER_PAGE


@admin.register(SoftSkillName)
class SoftSkillNameAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'description',)
    search_fields = ('name',)
    list_editable = ('description',)
    list_per_page = MAX_SKILLS_PER_PAGE


@admin.register(SoftSkill)
class SoftSkillAdmin(admin.ModelAdmin):
    list_display = ('pk', 'skill', 'resume', 'grid_row', 'grid_column',)
    search_fields = ('skill__name',)
    list_filter = ('resume',)
    list_editable = ('grid_row', 'grid_column',)
    autocomplete_fields = ('skill', 'resume',)
    list_per_page = MAX_SKILLS_PER_PAGE

    def get_queryset(
        self: 'SoftSkillAdmin', request: WSGIRequest
    ) -> QuerySet:
        queryset = super().get_queryset(request)
        return queryset.select_related('skill', 'resume', 'resume__user')


@admin.register(HardSkill)
class HardSkillAdmin(admin.ModelAdmin):
    list_display = ('pk', 'skill', 'resume', 'grid_row', 'grid_column',)
    search_fields = ('skill__name',)
    list_filter = ('resume',)
    list_editable = ('grid_row', 'grid_column',)
    autocomplete_fields = ('skill', 'resume',)
    list_per_page = MAX_SKILLS_PER_PAGE

    def get_queryset(
        self: 'HardSkillAdmin', request: WSGIRequest
    ) -> QuerySet:
        queryset = super().get_queryset(request)
        return queryset.select_related('skill', 'resume', 'resume__user')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'institution',
        'degree',
        'field_of_study',
        'start_date',
        'end_date',
    )
    search_fields = ('institution',)
    list_filter = ('user',)
    list_per_page = MAX_EDUCATIONS_PER_PAGE
    autocomplete_fields = ('user',)

    def get_queryset(
        self: 'EducationAdmin', request: WSGIRequest
    ) -> QuerySet:
        queryset = super().get_queryset(request)
        return queryset.select_related('user',)


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'company',
        'position',
        'start_date',
        'end_date',
    )
    search_fields = ('company',)
    list_filter = ('user',)
    list_editable = ('company', 'position',)
    list_per_page = MAX_EXPERIANCE_PER_PAGE
    autocomplete_fields = ('user',)

    def get_queryset(
        self: 'EducationAdmin', request: WSGIRequest
    ) -> QuerySet:
        queryset = super().get_queryset(request)
        return queryset.select_related('user',)


class BaseResumeInline(admin.StackedInline):
    extra = 0
    fields = ()

    foreign_key_field = None
    related_model = None

    def get_resume_user(
        self: 'BaseResumeInline', request: WSGIRequest
    ) -> User | None:
        resume_id = request.resolver_match.kwargs.get('object_id')
        if resume_id:
            try:
                resume = Resume.objects.get(pk=resume_id)
                return resume.user
            except Resume.DoesNotExist:
                pass
        return None

    def formfield_for_foreignkey(
        self: 'BaseResumeInline',
        db_field: Experience | Education,
        request: WSGIRequest,
        **kwargs: dict
    ) -> Experience | Education:
        if db_field.name == self.foreign_key_field:
            user = self.get_resume_user(request)
            if user:
                kwargs['queryset'] = self.related_model.objects.filter(
                    user=user)
            else:
                kwargs['queryset'] = self.related_model.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_module_permission(
        self: 'BaseResumeInline', request: WSGIRequest
    ) -> bool:
        return bool(request.resolver_match.kwargs.get('object_id'))


class ExperienceInline(BaseResumeInline):
    model = ResumeExperience
    fields = ('experience',)
    foreign_key_field = 'experience'
    related_model = Experience

    def get_queryset(
        self: 'HardSkillInline', request: WSGIRequest
    ) -> QuerySet:
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'resume', 'experience', 'experience__user', 'resume__user')


class EducationInline(BaseResumeInline):
    model = ResumeEducation
    fields = ('education',)
    foreign_key_field = 'education'
    related_model = Education

    def get_queryset(
        self: 'HardSkillInline', request: WSGIRequest
    ) -> QuerySet:
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'resume', 'education', 'education__user', 'resume__user')


class HardSkillInline(admin.TabularInline):
    model = HardSkill
    extra = 1
    autocomplete_fields = ('skill',)

    def get_queryset(
        self: 'HardSkillInline', request: WSGIRequest
    ) -> QuerySet:
        queryset = super().get_queryset(request)
        return queryset.select_related('skill', 'resume', 'resume__user')


class SoftSkillInline(admin.TabularInline):
    model = SoftSkill
    extra = 1
    autocomplete_fields = ('skill',)

    def get_queryset(
        self: 'SoftSkillInline', request: WSGIRequest
    ) -> QuerySet:
        queryset = super().get_queryset(request)
        return queryset.select_related('skill', 'resume', 'resume__user')


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'position',
        'is_published',
        'slug',
    )
    search_fields = ('position', 'user__username',)
    list_filter = ('user', 'is_published',)
    list_editable = ('is_published', 'position',)
    list_per_page = MAX_RESUMES_PER_PAGE
    autocomplete_fields = ('user', 'position',)
    inlines = (
        EducationInline,
        ExperienceInline,
        HardSkillInline,
        SoftSkillInline,
    )

    def get_queryset(self: 'ResumeAdmin', request: WSGIRequest) -> QuerySet:
        return (
            super().get_queryset(request)
            .prefetch_related('educations', 'experiences',)
            .select_related('user', 'position',)
        )
