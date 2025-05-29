from django.utils import timezone
from rest_framework import serializers

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
    ResumeExperience,
    ResumeEducation,
)


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

    def get_age(self: 'UserSerializer', obj: User) -> int | None:
        return obj.age()

    def create(self: 'UserSerializer', validated_data: dict) -> User:
        educations: list[dict] = validated_data.pop('educations', [])
        experiences: list[dict] = validated_data.pop('experiences', [])

        user = User.objects.create(**validated_data)

        for education in educations:
            Education.objects.create(user=user, **education)

        for experience in experiences:
            Experience.objects.create(user=user, **experience)

        return user

    def update(
        self: 'UserSerializer', instance: User, validated_data: dict
    ) -> User:
        request = self.context.get('request')
        if 'email' in validated_data and not (
            request and request.user and request.user.is_active and (
                request.user.is_staff or request.user.is_superuser
            )
        ):
            raise serializers.ValidationError({
                'email': (
                    'Изменение email по данному url доступно только персоналу.'
                )
            })

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


class ResumeSerializer(serializers.ModelSerializer):
    user = UserInResumeSerializer(read_only=True)
    position = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(),
        required=True,
    )
    hard_skills = serializers.PrimaryKeyRelatedField(
        queryset=HardSkill.objects.all(),
        many=True,
        required=False,
        write_only=True,
    )
    hard_skills_detail = HardSkillSerializer(
        many=True, source='hard_skills', read_only=True)
    soft_skills = serializers.PrimaryKeyRelatedField(
        queryset=SoftSkill.objects.all(),
        many=True,
        required=False,
        write_only=True,
    )
    soft_skills_detail = SoftSkillSerializer(
        many=True, source='soft_skills', read_only=True)
    educations = serializers.PrimaryKeyRelatedField(
        queryset=Education.objects.all(),
        many=True,
        required=False,
        write_only=True,
    )
    educations_detail = EducationSerializer(
        many=True, source='educations', read_only=True)
    experiences = serializers.PrimaryKeyRelatedField(
        queryset=Experience.objects.all(),
        many=True,
        required=False,
        write_only=True,
    )
    experiences_detail = ExperienceSerializer(
        many=True, source='experiences', read_only=True)

    class Meta:
        model = Resume
        fields = (
            'slug',
            'user',
            'position',
            'about_me',
            'is_published',
            'hard_skills',
            'hard_skills_detail',
            'soft_skills',
            'soft_skills_detail',
            'educations',
            'educations_detail',
            'experiences',
            'experiences_detail',
        )
        read_only_fields = ('slug',)

    def create(self: 'ResumeSerializer', validated_data: dict) -> Resume:
        hard_skills: list[dict] = validated_data.pop('hard_skills', [])
        soft_skills: list[dict] = validated_data.pop('soft_skills', [])
        educations: list[int] = validated_data.pop('educations', [])
        experiences: list[int] = validated_data.pop('experiences', [])

        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                'Вы должны быть авторизованы для создания резюме.'
            )
        user = request.user

        resume = Resume.objects.create(user=user, **validated_data)

        for skill in hard_skills:
            HardSkill.objects.create(resume=resume, skill=skill)

        for skill in soft_skills:
            SoftSkill.objects.create(resume=resume, skill=skill)

        for education in educations:
            ResumeEducation.objects.create(resume=resume, education=education)

        for experience in experiences:
            ResumeEducation.objects.create(
                resume=resume, experience=experience)

        return resume
