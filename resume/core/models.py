from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

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


class Timestamp(models.Model):
    start_date = models.DateField('Дата начала')
    end_date = models.DateField('Дата окончания', null=True, blank=True)

    class Meta:
        abstract = True
