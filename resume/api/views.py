from rest_framework import viewsets

from user.models import (
    HardSkillName,
    SoftSkillName,
    Location,
    User,
    Resume,
)
from .serializers import (
    HardSkillNameSerializer,
    SoftSkillNameSerializer,
    LocationSerializer,
    UserSerializer,
    ResumeSerializer,
)


class HardSkillNameViewSet(viewsets.ModelViewSet):
    queryset = HardSkillName.objects.all()
    serializer_class = HardSkillNameSerializer


class SoftSkillNameViewSet(viewsets.ModelViewSet):
    queryset = SoftSkillName.objects.all()
    serializer_class = SoftSkillNameSerializer


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ResumeViewSet(viewsets.ModelViewSet):
    lookup_field = 'slug'
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
