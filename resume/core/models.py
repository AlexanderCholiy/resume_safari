from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from .constants import (
    MAX_GRID_SIZE_X,
    MAX_GRID_SIZE_Y,
    MAX_SKILL_DESCRIPTION_LENGTH,
    MAX_SKILL_NAME_LENGTH,
)


class Grid(models.Model):
    grid_row = models.PositiveIntegerField(
        'Строка',
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(MAX_GRID_SIZE_Y)],
        help_text='Номер строки в HTML-сетке для отображения этого навыка',
    )
    grid_column = models.PositiveIntegerField(
        'Столбец',
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(MAX_GRID_SIZE_X)],
        help_text='Номер столбца в HTML-сетке для отображения этого навыка',
    )
    updated_at = models.DateTimeField(
        'Дата обновления',
        auto_now=True,
    )

    class Meta:
        abstract = True


class Skill(models.Model):
    name = models.CharField(
        'Название',
        max_length=MAX_SKILL_NAME_LENGTH,
    )
    description = models.CharField(
        'Описание',
        max_length=MAX_SKILL_DESCRIPTION_LENGTH,
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True

    def __str__(self: 'Skill') -> str:
        return self.name

    def clean(self: 'Skill') -> None:
        super().clean()
        cls = self.__class__
        # Для SQLite лучше использовать __iregex для работы с кирилецей.
        if (
            cls.objects
            .filter(name__iregex=rf'^\s*{self.name}\s*$')
            .exclude(pk=self.pk).exists()
        ):
            raise ValidationError({
                'name': (
                    f'{cls._meta.verbose_name.capitalize()} с названием '
                    f'"{self.name}" уже существует (без учёта регистра).'
                )
            })

    @classmethod
    def update_or_create_normalized(
        cls: 'Skill', name: str, description: str = None
    ) -> tuple['Skill', bool]:
        existing_skill = (
            cls.objects.filter(name__iregex=rf'^\s*{name}\s*$').first()
        )

        if existing_skill:
            existing_skill.name = name
            existing_skill.description = description
            existing_skill.full_clean()
            existing_skill.save()
            return existing_skill, False
        else:
            skill = cls(name=name, description=description)
            skill.full_clean()
            skill.save()
            return skill, True


class Timestamp(models.Model):
    start_date = models.DateField('Дата начала')
    end_date = models.DateField('Дата окончания', null=True, blank=True)

    class Meta:
        abstract = True
