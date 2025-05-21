from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from unidecode import unidecode
from django.utils import timezone

from core.models import Grid, Skill, Timestamp
from .constants import (
    MAX_USER_PATRONYMIC_LENGTH,
    MAX_COUNTRY_LENGTH,
    MAX_CITY_LENGTH,
    MAX_GITHUB_LINK_LENGTH,
    MAX_TELEGRAM_ID_LENGTH,
    MAX_COMPANY_NAME_LENGTH,
    MAX_POSITION_LENGTH,
    MAX_EDUCATION_DEGREE_LENGTH,
    MAX_FIELD_OF_STUDY_LENGTH,
    MAX_INSTITUTION_NAME_LENGTH,
    MAX_PHONE_LENGTH,
    MAX_SLUG_LENGTH,
)


class User(AbstractUser):
    patronymic = models.CharField(
        'Отчество',
        max_length=MAX_USER_PATRONYMIC_LENGTH,
        blank=True,
    )
    telegram_id = models.CharField(
        'Имя пользователя в Telegram',
        max_length=MAX_TELEGRAM_ID_LENGTH,
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
        return self.get_full_name()


class Location(models.Model):
    country = models.CharField(
        'Страна',
        max_length=MAX_COUNTRY_LENGTH,
        db_index=True,
    )
    city = models.CharField(
        'Город',
        max_length=MAX_CITY_LENGTH,
    )

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

    def __str__(self: 'Location') -> str:
        return f'г. {self.city} ({self.country})'


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

    def __str__(self: 'HardSkill') -> str:
        return (
            f'{self.skill.name} - {self.resume.user.username} '
            f'({self.resume.position})'
        )


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

    def __str__(self: 'SoftSkill') -> str:
        return (
            f'{self.skill.name} - {self.resume.user.username} '
            f'({self.resume.position})'
        )


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
        'Степень',
        max_length=MAX_EDUCATION_DEGREE_LENGTH,
    )
    field_of_study = models.CharField(
        'Специальность',
        max_length=MAX_FIELD_OF_STUDY_LENGTH,
    )

    class Meta:
        verbose_name = 'образование'
        verbose_name_plural = 'Образование'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'institution', 'degree', 'field_of_study'],
                name='unique_education'
            )
        ]

    def __str__(self: 'Education') -> str:
        return (
            f'{self.user.username}: '
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
        help_text='В качестве разделителя используйте ";"',
    )

    class Meta:
        verbose_name = 'опыт работы'
        verbose_name_plural = 'Опыт работы'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'company', 'position'],
                name='unique_experience'
            )
        ]

    def __str__(self: 'Experience') -> str:
        return f'{self.user.username}: {self.company} - {self.position}'


class Resume(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='resume',
        verbose_name='Пользователь',
        db_index=True,
    )
    position = models.CharField(
        'Должность',
        max_length=MAX_POSITION_LENGTH,
        db_index=True,
    )
    about_me = models.TextField('Обо мне')
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
        return f'{self.user.username}: {self.position}'

    def save(self: 'Resume', *args: tuple, **kwargs: dict) -> None:
        if not self.slug:
            self.slug = slugify(
                unidecode(f'{self.user.username}-{self.position}'))
        super().save(*args, **kwargs)


class ResumeExperience(models.Model):
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE)
    experience = models.ForeignKey(Experience, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['resume', 'experience'],
                name='unique_experience_per_resume'
            )
        ]


class ResumeEducation(models.Model):
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE)
    education = models.ForeignKey(Education, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['resume', 'education'],
                name='unique_education_per_resume'
            )
        ]
