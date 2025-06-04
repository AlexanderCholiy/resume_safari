import datetime as dt

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from .constants import MIN_AGE, MAX_AGE
from user.models import (
    HardSkillName,
    SoftSkillName,
    Location,
    Position,
    Education,
    Experience,
    User,
    Resume,
    SoftSkill,
    HardSkill,
)
from services.models import PendingUser
from .mixins import UserValidationMixin


class PendingUserSerializer(serializers.ModelSerializer, UserValidationMixin):
    password = serializers.CharField(
        write_only=True, validators=[validate_password])

    class Meta:
        model = PendingUser
        fields = ('username', 'email', 'password')

    def validate_username(self: 'PendingUserSerializer', username: str) -> str:
        return self.validate_username_common(username)

    def validate_email(self: 'PendingUserSerializer', email: str) -> str:
        return self.validate_email_common(email)

    def create(
        self: 'PendingUserSerializer', validated_data: dict
    ) -> PendingUser:
        raw_password = validated_data.pop('password')
        validated_data['password'] = make_password(raw_password)
        return PendingUser.objects.create(**validated_data)


class UserMeSerializer(serializers.ModelSerializer, UserValidationMixin):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email')

    def validate_username(self: 'UserMeSerializer', username: str) -> str:
        return self.validate_username_common(
            username, current_username=self.instance.username)

    def validate_email(self: 'UserMeSerializer', email: str) -> str:
        return self.validate_email_common(
            email, current_email=self.instance.email)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True, validators=[validate_password])


class HardSkillNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = HardSkillName
        fields = ('id', 'name', 'description',)


class SoftSkillNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoftSkillName
        fields = ('id', 'name', 'description',)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'country', 'city',)
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Location.objects.all(),
                fields=('country', 'city')
            )
        ]


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ('id', 'category', 'position',)
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Position.objects.all(),
                fields=('position', 'category')
            )
        ]


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = (
            'id',
            'institution',
            'degree',
            'field_of_study',
            'start_date',
            'end_date',
        )

    def validate(self: 'EducationSerializer', data: dict) -> dict:
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if end_date and start_date and end_date < start_date:
            raise serializers.ValidationError(
                {
                    'end_date': (
                        'Дата окончания не может быть раньше даты начала.'
                    )
                }
            )
        return data


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = (
            'id',
            'company',
            'position',
            'responsibilities',
            'start_date',
            'end_date',
        )

    def validate(self: 'ExperienceSerializer', data: dict) -> dict:
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if end_date and start_date and end_date < start_date:
            raise serializers.ValidationError(
                {
                    'end_date': (
                        'Дата окончания не может быть раньше даты начала.'
                    )
                }
            )
        return data


class UserSerializer(serializers.ModelSerializer, UserValidationMixin):
    """
    Данный сериализатор расчитан для обновления дополнительных полей
    пользователя, относящиеся к его резюме. Для обновления полей email,
    password, username иcпользуется djoser.
    """
    educations = EducationSerializer(many=True, required=False)
    experiences = ExperienceSerializer(many=True, required=False)
    location = LocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    age = serializers.SerializerMethodField(read_only=True)
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'patronymic',
            'email',
            'phone',
            'telegram_id',
            'git_hub_link',
            'date_of_birth',
            'age',
            'avatar',
            'location',
            'location_id',
            'educations',
            'experiences',
        )
        read_only_fields = ('username', 'email',)

    def get_age(self: 'UserSerializer', obj: User) -> int | None:
        return obj.age()

    def validate_date_of_birth(
        self: 'UserSerializer', value: dt.date | None
    ) -> dt.date:
        if value is not None:
            today = dt.date.today()
            min_age = MIN_AGE
            max_age = MAX_AGE
            earliest = today.replace(year=today.year - max_age)
            latest = today.replace(year=today.year - min_age)

            if not (earliest <= value <= latest):
                raise serializers.ValidationError(
                    f'Возраст пользователя должен быть от {min_age} до '
                    f'{max_age} лет.'
                )
        return value

    def update(
        self: 'UserSerializer', instance: User, validated_data: dict
    ) -> User:

        educations: list[dict] = validated_data.pop('educations', None)
        experiences: list[dict] = validated_data.pop('experiences', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if educations is not None:
            existing_educations = {
                (e.institution, e.start_date): e
                for e in Education.objects.filter(user=instance).all()
            }
            incoming_keys = set()

            for data in educations:
                self.validate_education_data(data)
                key = (
                    data.get('institution'),
                    data.get('start_date'),
                )
                incoming_keys.add(key)

                Education.objects.update_or_create(
                    user=instance,
                    institution=key[0],
                    start_date=key[1],
                    defaults={
                        'degree': data.get('degree'),
                        'field_of_study': data.get('field_of_study'),
                        'end_date': data.get('end_date'),
                    }
                )

            for key, obj in existing_educations.items():
                if key not in incoming_keys:
                    obj.delete()

        if experiences is not None:
            existing_experiences = {
                (e.company, e.start_date): e
                for e in Experience.objects.filter(user=instance).all()
            }
            incoming_keys = set()

            for data in experiences:
                self.validate_experience_data(data)
                key = (
                    data.get('company'),
                    data.get('start_date')
                )
                incoming_keys.add(key)

                Experience.objects.update_or_create(
                    user=instance,
                    company=key[0],
                    start_date=key[1],
                    defaults={
                        'position': data.get('position'),
                        'responsibilities': data.get('responsibilities'),
                        'end_date': data.get('end_date'),
                    }
                )

            for key, obj in existing_experiences.items():
                if key not in incoming_keys:
                    obj.delete()

        return instance


class UserInResumeSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'patronymic',
            'email',
            'phone',
            'telegram_id',
            'git_hub_link',
            'date_of_birth',
            'avatar',
            'location',
        )


class HardSkillSerializer(serializers.ModelSerializer):
    skill = HardSkillNameSerializer(read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=HardSkillName.objects.all(), write_only=True, source='skill'
    )

    class Meta:
        model = HardSkill
        fields = ('skill', 'skill_id', 'grid_column', 'grid_row',)


class SoftSkillSerializer(serializers.ModelSerializer):
    skill = SoftSkillNameSerializer(read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=SoftSkillName.objects.all(), write_only=True, source='skill'
    )

    class Meta:
        model = SoftSkill
        fields = ('skill', 'skill_id', 'grid_column', 'grid_row',)


class ResumeSerializer(serializers.ModelSerializer, UserValidationMixin):
    position = PositionSerializer(read_only=True)
    position_id = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(),
        required=True,
        write_only=True,
        source='position'
    )
    educations = EducationSerializer(many=True, required=False)
    experiences = ExperienceSerializer(many=True, required=False)
    hard_skills = HardSkillSerializer(many=True, required=False)
    soft_skills = SoftSkillSerializer(many=True, required=False)

    class Meta:
        model = Resume
        fields = (
            'slug',
            'user',
            'position',
            'position_id',
            'about_me',
            'is_published',
            'educations',
            'experiences',
            'hard_skills',
            'soft_skills',
        )
        read_only_fields = ('slug',)
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Resume.objects.all(),
                fields=('user', 'position')
            )
        ]

    def __init__(
        self: 'ResumeSerializer', *args: tuple, **kwargs: dict
    ) -> None:
        super().__init__(*args, **kwargs)
        request = self.context.get('request', None)
        if request and request.method != 'GET':
            self.fields['user'] = serializers.HiddenField(
                default=serializers.CurrentUserDefault())
        else:
            self.fields['user'] = UserInResumeSerializer(
                read_only=True)

    def validate(self: 'ResumeSerializer', attrs: dict) -> dict:
        request = self.context['request']
        user: User = request.user
        attrs['user'] = user

        if request.method == 'POST':
            position = attrs.get('position')
            if position is None:
                raise serializers.ValidationError(
                    {'position_id': 'Это поле обязательно.'}
                )
        else:
            position = attrs.get(
                'position', getattr(self.instance, 'position', None))

        return super().validate(attrs)

    def create(self: 'ResumeSerializer', validated_data: dict) -> Resume:
        educations = validated_data.pop('educations', [])
        experiences = validated_data.pop('experiences', [])
        hard_skills = validated_data.pop('hard_skills', [])
        soft_skills = validated_data.pop('soft_skills', [])

        user = validated_data['user']
        resume = Resume.objects.create(**validated_data)

        created_educations = []
        for data in educations:
            self.validate_education_data(data)
            education, _ = Education.objects.update_or_create(
                user=user,
                institution=data.get('institution'),
                start_date=data.get('start_date'),
                defaults={
                    'degree': data.get('degree'),
                    'field_of_study': data.get('field_of_study'),
                    'end_date': data.get('end_date'),
                }
            )
            created_educations.append(education)
        resume.educations.add(*created_educations)

        created_experiences = []
        for data in experiences:
            self.validate_experience_data(data)
            experience, _ = Experience.objects.update_or_create(
                user=user,
                company=data.get('company'),
                start_date=data.get('start_date'),
                defaults={
                    'position': data.get('position'),
                    'responsibilities': data.get('responsibilities'),
                    'end_date': data.get('end_date'),
                }
            )
            created_experiences.append(experience)
        resume.experiences.add(*created_experiences)

        skills_seen = set()
        for data in hard_skills:
            skill = data.get('skill')
            if skill in skills_seen:
                raise serializers.ValidationError(
                    'Дублирование hard_skill в одном резюме запрещено.')
            skills_seen.add(skill)
            HardSkill.objects.create(resume=resume, **data)

        skills_seen = set()
        for data in soft_skills:
            skill = data.get('skill')
            if skill in skills_seen:
                raise serializers.ValidationError(
                    'Дублирование soft_skill в одном резюме запрещено.')
            skills_seen.add(skill)
            SoftSkill.objects.create(resume=resume, **data)

        return resume

    def update(
        self: 'ResumeSerializer', instance: Resume, validated_data: dict
    ) -> Resume:
        educations = validated_data.pop('educations', None)
        experiences = validated_data.pop('experiences', None)
        hard_skills = validated_data.pop('hard_skills', None)
        soft_skills = validated_data.pop('soft_skills', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        user = instance.user

        if educations is not None:
            resume_educations = []
            for data in educations:
                self.validate_education_data(data)
                key = (data.get('institution'), data.get('start_date'))
                education, _ = Education.objects.update_or_create(
                    user=user,
                    institution=key[0],
                    start_date=key[1],
                    defaults={
                        'degree': data.get('degree'),
                        'field_of_study': data.get('field_of_study'),
                        'end_date': data.get('end_date'),
                    }
                )
                resume_educations.append(education)
            instance.educations.clear()
            instance.educations.add(*resume_educations)

        if experiences is not None:
            resume_experiences = []
            for data in experiences:
                self.validate_experience_data(data)
                key = (data.get('company'), data.get('start_date'))
                experience, _ = Experience.objects.update_or_create(
                    user=user,
                    company=key[0],
                    start_date=key[1],
                    defaults={
                        'position': data.get('position'),
                        'responsibilities': data.get('responsibilities'),
                        'end_date': data.get('end_date'),
                    }
                )
                resume_experiences.append(experience)
            instance.experiences.clear()
            instance.experiences.add(*resume_experiences)

        if hard_skills is not None:
            skills_seen = set()
            for data in hard_skills:
                skill = data.get('skill')
                if skill in skills_seen:
                    raise serializers.ValidationError(
                        'Дублирование hard_skill в одном резюме запрещено.')
                skills_seen.add(skill)

            instance.hard_skills.all().delete()
            for data in hard_skills:
                skill = data.get('skill')
                HardSkill.objects.create(resume=instance, **data)

        if soft_skills is not None:
            skills_seen = set()
            for data in soft_skills:
                skill = data.get('skill')
                if skill in skills_seen:
                    raise serializers.ValidationError(
                        'Дублирование soft_skill в одном резюме запрещено.')
                skills_seen.add(skill)

            instance.soft_skills.all().delete()
            for data in soft_skills:
                skill = data.get('skill')
                SoftSkill.objects.create(resume=instance, **data)

        return instance
