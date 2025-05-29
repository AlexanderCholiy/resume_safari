from rest_framework import viewsets

from user.models import (
    HardSkillName,
    SoftSkillName,
    Location,
    User,
    Resume,
    Position,
)
from .serializers import (
    HardSkillNameSerializer,
    SoftSkillNameSerializer,
    LocationSerializer,
    UserSerializer,
    ResumeSerializer,
    PositionSerializer,
)
from .permissions import IsAdminOrStaff, IsOwnerOrStaffOrAdmin


class HardSkillNameViewSet(viewsets.ModelViewSet):
    queryset = HardSkillName.objects.all()
    serializer_class = HardSkillNameSerializer


class SoftSkillNameViewSet(viewsets.ModelViewSet):
    queryset = SoftSkillName.objects.all()
    serializer_class = SoftSkillNameSerializer


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self: 'UserViewSet') -> bool:
        if self.action == 'create':
            return [IsAdminOrStaff()]
        elif self.action in ('update', 'partial_update', 'destroy'):
            return [IsOwnerOrStaffOrAdmin()]
        return super().get_permissions()


class ResumeViewSet(viewsets.ModelViewSet):
    lookup_field = 'slug'
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
