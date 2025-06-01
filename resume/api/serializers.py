import datetime as dt

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from .constants import MIN_AGE, MAX_AGE
from user.models import (
    HardSkillName,
    SoftSkillName,
    Location,
    Position,
    Education,
    Experience,
    User,
    # Resume,
    SoftSkill,
    HardSkill,
    # ResumeExperience,
    # ResumeEducation,
)
from services.models import PendingUser


class PendingUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, validators=[validate_password])

    class Meta:
        model = PendingUser
        fields = ('username', 'email', 'password')

    def validate_username(self: 'PendingUserSerializer', username: str) -> str:
        for validator in User._meta.get_field('username').validators:
            validator(username)

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError('Имя пользователя уже занято.')

        pending_user = PendingUser.objects.filter(username=username).first()
        if pending_user:
            if pending_user.is_expired:
                pending_user.delete()
            else:
                raise serializers.ValidationError(
                    'Имя пользователя ожидает подтверждения.')

        return username

    def validate_email(self: 'PendingUserSerializer', email: str) -> str:
        for validator in User._meta.get_field('email').validators:
            validator(email)

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email уже зарегистрирован.')

        pending_user = PendingUser.objects.filter(email=email).first()
        if pending_user:
            if pending_user.is_expired:
                pending_user.delete()
            else:
                raise serializers.ValidationError(
                    'Регистрация с этим email ожидает подтверждения.')

        return email

    def create(
        self: 'PendingUserSerializer', validated_data: dict
    ) -> PendingUser:
        raw_password = validated_data.pop('password')
        validated_data['password'] = make_password(raw_password)
        return PendingUser.objects.create(**validated_data)


class UserMeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('pk', 'username', 'email')

    def validate_username(self, username):
        user = self.instance
        if username == user.username:
            return username

        for validator in User._meta.get_field('username').validators:
            validator(username)

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError('Имя пользователя уже занято.')

        pending_user = PendingUser.objects.filter(username=username).first()
        if pending_user:
            if pending_user.is_expired:
                pending_user.delete()
            else:
                raise serializers.ValidationError('Имя пользователя ожидает подтверждения.')

        return username

    def validate_email(self, email):
        user = self.instance
        if email == user.email:
            return email

        for validator in User._meta.get_field('email').validators:
            validator(email)

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email уже зарегистрирован.')

        pending_user = PendingUser.objects.filter(email=email).first()
        if pending_user:
            if pending_user.is_expired:
                pending_user.delete()
            else:
                raise serializers.ValidationError('Регистрация с этим email ожидает подтверждения.')

        return email


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True, validators=[validate_password])


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(
        write_only=True, validators=[validate_password])


class HardSkillNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = HardSkillName
        fields = ('pk', 'name', 'description',)


class SoftSkillNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoftSkillName
        fields = ('pk', 'name', 'description',)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('pk', 'country', 'city',)


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ('pk', 'category', 'position',)


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = (
            'pk',
            'institution',
            'degree',
            'field_of_study',
            'start_date',
            'end_date',
        )


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = (
            'pk',
            'company',
            'position',
            'responsibilities',
            'start_date',
            'end_date',
        )


class UserSerializer(serializers.ModelSerializer):
    """
    Данный сериализатор расчитан для обновления дополнительных полей
    пользователя, относящиеся к его резюме. Для обновления полей email,
    password, username иcпользуется djoser.
    """
    educations = EducationSerializer(many=True, required=False)
    experiences = ExperienceSerializer(many=True, required=False)
    location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    location_detail = LocationSerializer(source='location', read_only=True)
    age = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'pk',
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
            'location_detail',
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

    class Meta:
        model = HardSkill
        fields = ('skill', 'grid_column', 'grid_row',)


class SoftSkillSerializer(serializers.ModelSerializer):
    skill = SoftSkillNameSerializer(read_only=True)

    class Meta:
        model = SoftSkill
        fields = ('skill', 'grid_column', 'grid_row',)
