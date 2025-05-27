from rest_framework import serializers

from user.models import (
    HardSkillName,
    SoftSkillName,
    Location,
    Education,
    Experience,
    User,
    Resume,
    SoftSkill,
    HardSkill,
    ResumeExperience,
    ResumeEducation,
)
from core.constants import DEFAULT_GRID_ROW_AND_COLUMN


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
    location = LocationSerializer(required=False)
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
            'avatar',
            'location',
            'educations',
            'experiences',
        )
        read_only_fields = ('email',)

    def create(self: 'UserSerializer', validated_data: dict) -> User:
        educations: list[dict] = validated_data.pop('educations', [])
        experiences: list[dict] = validated_data.pop('experiences', [])
        location: dict | None = validated_data.pop('location', None)

        user = User.objects.create(**validated_data)

        if location:
            Location.objects.get_or_create(**location)

        for education in educations:
            Education.objects.get_or_create(
                user=user,
                institution=education.get('institution'),
                degree=education.get('degree'),
                field_of_study=education.get('field_of_study'),
            )
        for experience in experiences:
            Experience.objects.get_or_create(
                user=user,
                company=experience.get('company'),
                position=experience.get('position'),
                responsibilities=experience.get('responsibilities'),
            )

        return user

    def update(
        self: 'UserSerializer', instance: User, validated_data: dict
    ) -> User:
        educations: list[dict] = validated_data.pop('educations', None)
        experiences: list[dict] = validated_data.pop('experiences', None)
        location: dict | None = validated_data.pop('location', None)

        if educations is not None:
            instance.educations.all().delete()
            for education in educations:
                Education.objects.update_or_create(
                    user=instance,
                    institution=education.get('institution'),
                    degree=education.get('degree'),
                    field_of_study=education.get('field_of_study'),
                )

        if experiences is not None:
            instance.experiences.all().delete()
            for experience in experiences:
                Experience.objects.get_or_create(
                    user=instance,
                    company=experience.get('company'),
                    position=experience.get('position'),
                    responsibilities=experience.get('responsibilities'),
                )

        if location:
            Location.objects.get(**location)
        else:
            instance.location.delete()

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
            'about_me',
            'is_published',
            'hard_skills',
            'soft_skills',
            'educations',
            'experiences',
        )

    def create(self: 'ResumeSerializer', validated_data: dict) -> Resume:
        educations: list[dict] = validated_data.pop('educations', [])
        experiences: list[dict] = validated_data.pop('experiences', [])
        hard_skills: list[dict] = validated_data.pop('hard_skills', [])
        soft_skills: list[dict] = validated_data.pop('soft_skills', [])

        resume = Resume.objects.create(**validated_data)

        for education in educations:
            ResumeEducation.objects.get_or_create(
                resume=resume,
                experience=education,
            )
        for experience in experiences:
            ResumeExperience.objects.get_or_create(
                resume=resume,
                experience=experience,
            )

        for skill in hard_skills:
            HardSkill.objects.get_or_create(
                resume=resume,
                skill=skill['skill'],
                grid_row=skill.get(
                    'grid_row', DEFAULT_GRID_ROW_AND_COLUMN),
                grid_column=skill.get(
                    'grid_column', DEFAULT_GRID_ROW_AND_COLUMN),
            )

        for skill in soft_skills:
            SoftSkill.objects.get_or_create(
                resume=resume,
                skill=skill['skill'],
                grid_row=skill.get(
                    'grid_row', DEFAULT_GRID_ROW_AND_COLUMN),
                grid_column=skill.get(
                    'grid_column', DEFAULT_GRID_ROW_AND_COLUMN),
            )

        return resume

    def update(
        self: 'ResumeSerializer', instance: Resume, validated_data: dict
    ) -> Resume:
        educations: list[dict] = validated_data.pop('educations', None)
        experiences: list[dict] = validated_data.pop('experiences', None)
        hard_skills: list[dict] = validated_data.pop('hard_skills', None)
        soft_skills: list[dict] = validated_data.pop('soft_skills', None)

        if educations is not None:
            instance.educations.all().delete()
            for education in educations:
                ResumeEducation.objects.create(
                    resume=instance,
                    education=education,
                )

        if experiences is not None:
            instance.experiences.all().delete()
            for experience in experiences:
                ResumeExperience.objects.create(
                    resume=instance,
                    experience=experience,
                )

        if hard_skills is not None:
            instance.hard_skills.all().delete()
            for skill in hard_skills:
                HardSkill.objects.create(
                    resume=instance,
                    skill=skill['skill'],
                    grid_row=skill.get(
                        'grid_row', DEFAULT_GRID_ROW_AND_COLUMN),
                    grid_column=skill.get(
                        'grid_column', DEFAULT_GRID_ROW_AND_COLUMN),
                )

        if soft_skills is not None:
            instance.soft_skills.all().delete()
            for skill in soft_skills:
                SoftSkill.objects.create(
                    resume=instance,
                    skill=skill['skill'],
                    grid_row=skill.get(
                        'grid_row', DEFAULT_GRID_ROW_AND_COLUMN),
                    grid_column=skill.get(
                        'grid_column', DEFAULT_GRID_ROW_AND_COLUMN),
                )

        return instance
