from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from unidecode import unidecode
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator

from core.models import Grid, Skill, Timestamp, NormalizedPairModel
from .constants import (
    MAX_USER_PATRONYMIC_LENGTH,
    MAX_COUNTRY_LENGTH,
    MAX_CITY_LENGTH,
    MAX_GITHUB_LINK_LENGTH,
    MAX_COMPANY_NAME_LENGTH,
    MAX_POSITION_LENGTH,
    MAX_EDUCATION_DEGREE_LENGTH,
    MAX_FIELD_OF_STUDY_LENGTH,
    MAX_INSTITUTION_NAME_LENGTH,
    MAX_PHONE_LENGTH,
    MAX_SLUG_LENGTH,
    MAX_CATEGORY_LENGTH,
    MAX_RESUME_COUNT,
    MAX_RESUME_TEXT_LENGTH,
)


class User(AbstractUser):
    email = models.EmailField('Email', unique=True, blank=True)
    patronymic = models.CharField(
        'Отчество',
        max_length=MAX_USER_PATRONYMIC_LENGTH,
        blank=True,
    )
    telegram_id = models.SlugField(
        'Имя пользователя в Telegram',
        blank=True,
        null=True,
    )
    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        related_name='users',
        verbose_name='Локация',
        null=True,
        blank=True,
    )
    git_hub_link = models.URLField(
        'Ссылка на GitHub',
        max_length=MAX_GITHUB_LINK_LENGTH,
        blank=True,
        null=True,
    )
    date_of_birth = models.DateField(
        'Дата рождения',
        blank=True,
        null=True,
    )
    phone = models.CharField(
        'Телефон',
        max_length=MAX_PHONE_LENGTH,
        blank=True,
        null=True,
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/',
        blank=True,
        null=True,
    )

    def get_full_name(self: 'User') -> str:
        full_name = (
            f'{self.last_name or ""} '
            f'{self.first_name or ""} '
            f'{self.patronymic or ""} '
            .strip()
        )
        return full_name or self.username

    def age(self: 'User') -> int | None:
        if self.date_of_birth:
            today = timezone.now().date()
            return (
                today.year - self.date_of_birth.year -
                (
                    (today.month, today.day) < (
                        self.date_of_birth.month, self.date_of_birth.day)
                )
            )
        return None

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self: 'User') -> str:
        return self.username

    def clean(self: 'User') -> None:
        super().clean()
        if self.phone:
            phone = self.phone
            if (
                not phone.startswith('7')
                or len(phone) != 11
                or not phone.isdigit()
            ):
                raise ValidationError({
                    'phone': 'Телефон должен быть в формате 7xxxxxxxxxx'
                })


class Location(NormalizedPairModel):
    country = models.CharField(
        'Страна',
        max_length=MAX_COUNTRY_LENGTH,
        db_index=True,
    )
    city = models.CharField(
        'Город',
        max_length=MAX_CITY_LENGTH,
    )

    field1_name = 'country'
    field2_name = 'city'

    class Meta:
        verbose_name = 'локация'
        verbose_name_plural = 'Локации'
        constraints = [
            models.UniqueConstraint(
                fields=['country', 'city'],
                name='unique_location'
            )
        ]
        ordering = ('-country', '-city',)


class HardSkillName(Skill):
    class Meta:
        verbose_name = 'навык'
        verbose_name_plural = 'Справочник профессиональных навыков'
        unique_together = ['name']


class SoftSkillName(Skill):
    class Meta:
        verbose_name = 'навык'
        verbose_name_plural = 'Справочник личностных навыков'
        unique_together = ['name']


class HardSkill(Grid):
    skill = models.ForeignKey(
        HardSkillName,
        on_delete=models.CASCADE,
        related_name='hard_skills',
        verbose_name='Профессиональный навык',
    )
    resume = models.ForeignKey(
        'Resume',
        on_delete=models.CASCADE,
        related_name='hard_skills',
        verbose_name='Резюме',
        db_index=True,
    )

    class Meta:
        verbose_name = 'проффесиональный навык'
        verbose_name_plural = 'Профессиональные навыки'
        constraints = [
            models.UniqueConstraint(
                fields=['resume', 'skill'],
                name='unique_resume_hard_skill'
            )
        ]
        ordering = ('grid_row', 'grid_column', 'updated_at',)

    def __str__(self: 'HardSkill') -> str:
        return f'{self.skill} - {self.resume}'


class SoftSkill(Grid):
    skill = models.ForeignKey(
        SoftSkillName,
        on_delete=models.CASCADE,
        related_name='soft_skills',
        verbose_name='Личностный навык',
    )
    resume = models.ForeignKey(
        'Resume',
        on_delete=models.CASCADE,
        related_name='soft_skills',
        verbose_name='Резюме',
        db_index=True,
    )

    class Meta:
        verbose_name = 'личностный навык'
        verbose_name_plural = 'Личностные навыки'
        constraints = [
            models.UniqueConstraint(
                fields=['resume', 'skill'],
                name='unique_resume_soft_skill'
            )
        ]
        ordering = ('grid_row', 'grid_column', 'updated_at',)

    def __str__(self: 'SoftSkill') -> str:
        return f'{self.skill} - {self.resume}'


class Education(Timestamp):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='educations',
        verbose_name='Пользователь',
        db_index=True,
    )
    institution = models.CharField(
        'Учебное заведение',
        max_length=MAX_INSTITUTION_NAME_LENGTH,
    )
    degree = models.CharField(
        'Степень (курсы)',
        max_length=MAX_EDUCATION_DEGREE_LENGTH,
    )
    field_of_study = models.CharField(
        'Специальность (направление)',
        max_length=MAX_FIELD_OF_STUDY_LENGTH,
    )

    class Meta:
        verbose_name = 'образование'
        verbose_name_plural = 'Образование'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'institution', 'start_date'],
                name='unique_education'
            )
        ]
        ordering = ('-start_date',)

    def __str__(self: 'Education') -> str:
        return (
            f'{self.user}: '
            f'{self.institution} - {self.degree} - {self.field_of_study}'
        )


class Experience(Timestamp):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='experiences',
        verbose_name='Пользователь',
        db_index=True,
    )
    company = models.CharField(
        'Компания',
        max_length=MAX_COMPANY_NAME_LENGTH,
    )
    position = models.CharField(
        'Должность',
        max_length=MAX_POSITION_LENGTH,
    )
    responsibilities = models.TextField(
        'Обязанности',
        blank=True,
        null=True,
        help_text='В качестве разделителя используйте "новую строку"',
    )

    class Meta:
        verbose_name = 'опыт работы'
        verbose_name_plural = 'Опыт работы'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'company', 'start_date'],
                name='unique_experience'
            )
        ]
        ordering = ('-start_date',)

    def __str__(self: 'Experience') -> str:
        return f'{self.user}: {self.company} - {self.position}'


class Resume(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='resume',
        verbose_name='Пользователь',
        db_index=True,
    )
    position = models.ForeignKey(
        'Position',
        on_delete=models.CASCADE,
        related_name='resume',
        verbose_name='Позиция',
        db_index=True,
    )
    about_me = models.TextField(
        'Обо мне',
        validators=[MaxLengthValidator(MAX_RESUME_TEXT_LENGTH)],
        help_text=f'Максимум {MAX_RESUME_TEXT_LENGTH} символов'
    )
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Отметьте, если хотите опубликовать резюме',
    )
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
    )
    educations = models.ManyToManyField(
        Education,
        through='ResumeEducation',
        verbose_name='Образование',
        related_name='resumes',
        blank=True,
    )
    experiences = models.ManyToManyField(
        Experience,
        through='ResumeExperience',
        verbose_name='Опыт работы',
        related_name='resumes',
        blank=True,
    )
    slug = models.SlugField(
        'Слаг',
        max_length=MAX_SLUG_LENGTH,
        unique=True,
        blank=True,
        help_text='Слаг для резюме. Генерируется автоматически.',
    )

    class Meta:
        verbose_name = 'резюме'
        verbose_name_plural = 'Резюме'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'position'],
                name='unique_resume'
            )
        ]
        ordering = ('-created_at',)

    def __str__(self: 'Resume') -> str:
        return f'{self.user}: {self.position}'

    def save(self: 'Resume', *args: tuple, **kwargs: dict) -> None:
        if self.pk is None:
            count = Resume.objects.filter(
                user=self.user, is_published=self.is_published).count()
            if count >= MAX_RESUME_COUNT:
                status = 'опубликованных' if self.is_published else (
                    'черновиков')
                raise ValidationError(
                    f'У пользователя может быть максимум {MAX_RESUME_COUNT} '
                    f'{status} резюме.'
                )

        first_slug = slugify(
            unidecode(f'{self.user.username}-{self.position.position}')
        )
        second_slug = slugify(
            unidecode(
                f'{self.user.username}-'
                f'{self.position.category}-{self.position.position}'
            )
        )

        if not (
            Resume.objects.exclude(pk=self.pk).filter(slug=first_slug).exists()
        ):
            self.slug = first_slug
        else:
            self.slug = second_slug

        super().save(*args, **kwargs)


class ResumeExperience(models.Model):
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name='resume_experiences',
    )
    experience = models.ForeignKey(
        Experience,
        on_delete=models.CASCADE,
        related_name='resume_experiences',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['resume', 'experience'],
                name='unique_experience_per_resume'
            )
        ]


class ResumeEducation(models.Model):
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name='resume_educations',
    )
    education = models.ForeignKey(
        Education,
        on_delete=models.CASCADE,
        related_name='resume_educations',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['resume', 'education'],
                name='unique_education_per_resume'
            )
        ]


class Position(NormalizedPairModel):
    category = models.CharField(
        'Категория',
        max_length=MAX_CATEGORY_LENGTH,
        db_index=True,
    )
    position = models.CharField(
        'Должность',
        max_length=MAX_POSITION_LENGTH,
        db_index=True,
    )

    field1_name = 'category'
    field2_name = 'position'

    class Meta:
        verbose_name = 'должность'
        verbose_name_plural = 'Должности'
        constraints = [
            models.UniqueConstraint(
                fields=['position', 'category'],
                name='unique_position'
            )
        ]
        ordering = ('-category', '-position',)
