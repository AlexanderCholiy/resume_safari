from rest_framework import viewsets

from user.models import (
    HardSkillName,
    SoftSkillName,
    Location,
    Education,
    User,
)
from .serializers import (
    HardSkillNameSerializer,
    SoftSkillNameSerializer,
    LocationSerializer,
    EducationSerializer,
    UserSerializer,
)


class HardSkillNameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HardSkillName.objects.all()
    serializer_class = HardSkillNameSerializer


class SoftSkillNameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SoftSkillName.objects.all()
    serializer_class = SoftSkillNameSerializer


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class EducationViewSet(viewsets.ModelViewSet):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
