from rest_framework import serializers

from user.models import (
    HardSkillName,
    SoftSkillName,
    Location,
    Education,
    Experience,
    User,
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


class EducationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Education
        fields = (
            'pk',
            'institution',
            'degree',
            'field_of_study',
            'start_date',
            'end_date',
            'user',
        )


class UserSerializer(serializers.ModelSerializer):
    educations = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'patronymic',
            'email',
            'location',
            'git_hub_link',
            'date_of_birth',
            'phone',
            'avatar',
            'educations',
        )
