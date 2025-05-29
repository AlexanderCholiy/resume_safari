from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from .constants import (
    MAX_GRID_SIZE_X,
    MAX_GRID_SIZE_Y,
    MAX_SKILL_DESCRIPTION_LENGTH,
    MAX_SKILL_NAME_LENGTH,
    DEFAULT_GRID_ROW_AND_COLUMN,
    MAX_EDUCATION_AND_EXPERIENCE,
)


class Grid(models.Model):
    grid_row = models.PositiveIntegerField(
        'Строка',
        default=DEFAULT_GRID_ROW_AND_COLUMN,
        validators=[MinValueValidator(1), MaxValueValidator(MAX_GRID_SIZE_Y)],
        help_text='Номер строки в HTML-сетке для отображения этого навыка',
    )
    grid_column = models.PositiveIntegerField(
        'Столбец',
        default=DEFAULT_GRID_ROW_AND_COLUMN,
        validators=[MinValueValidator(1), MaxValueValidator(MAX_GRID_SIZE_X)],
        help_text='Номер столбца в HTML-сетке для отображения этого навыка',
    )
    updated_at = models.DateTimeField(
        'Дата обновления',
        auto_now=True,
    )

    class Meta:
        abstract = True

    def clean(self: 'Grid') -> None:
        super().clean()
        resume = getattr(self, 'resume', None)
        if resume is not None:
            model_class = self.__class__
            qs = model_class.objects.filter(resume=resume)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            count = qs.count()
            max_allowed = MAX_GRID_SIZE_Y * MAX_GRID_SIZE_X
            if count >= max_allowed:
                raise ValidationError(
                    f'У одного резюме может быть максимум {max_allowed} '
                    f'элементов в {model_class.__name__}.'
                )


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
        # Для SQLite лучше использовать __iregex для работы с кирилецей:
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

    def clean(self: 'Timestamp') -> None:
        super().clean()
        user = getattr(self, 'user', None)
        if user is not None:
            model_class = self.__class__
            qs = model_class.objects.filter(user=user)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            count = qs.count()
            if count >= MAX_EDUCATION_AND_EXPERIENCE:
                raise ValidationError(
                    f'У одного пользователя может быть максимум '
                    f'{MAX_EDUCATION_AND_EXPERIENCE} элементов в '
                    f'{model_class.__name__}.'
                )


class NormalizedPairModel(models.Model):
    field1_name: str = None
    field2_name: str = None

    class Meta:
        abstract = True

    def __str__(self: 'NormalizedPairModel') -> str:
        val1 = getattr(self, self.field1_name)
        val2 = getattr(self, self.field2_name)
        return f'{val1}: {val2}'

    def clean(self: 'NormalizedPairModel') -> None:
        super().clean()
        Model = self.__class__
        val1 = getattr(self, self.field1_name)
        val2 = getattr(self, self.field2_name)
        # Для SQLite лучше использовать __iregex для работы с кирилецей:
        filters = {
            f'{self.field1_name}__iregex': rf'^\s*{val1}\s*$',
            f'{self.field2_name}__iregex': rf'^\s*{val2}\s*$',
        }
        if Model.objects.filter(**filters).exclude(pk=self.pk).exists():
            raise ValidationError({
                self.field1_name: (
                    f'Запись с такими значениями уже существует: '
                    f'"{val1}" и "{val2}" (без учёта регистра).'
                )
            })

    @classmethod
    def update_or_create_normalized(
        cls: type['NormalizedPairModel'], val1: str, val2: str
    ) -> tuple['NormalizedPairModel', bool]:
        filters = {
            f'{cls.field1_name}__iregex': rf'^\s*{val1}\s*$',
            f'{cls.field2_name}__iregex': rf'^\s*{val2}\s*$',
        }
        instance = cls.objects.filter(**filters).first()
        if instance:
            setattr(instance, cls.field1_name, val1)
            setattr(instance, cls.field2_name, val2)
            instance.full_clean()
            instance.save()
            return instance, False
        else:
            kwargs = {
                cls.field1_name: val1,
                cls.field2_name: val2,
            }
            instance = cls(**kwargs)
            instance.full_clean()
            instance.save()
            return instance, True
