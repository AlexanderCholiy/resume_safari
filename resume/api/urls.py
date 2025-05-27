from rest_framework.routers import DefaultRouter
from django.urls import path, include

from . import views


app_name = 'api'

router = DefaultRouter()
router.register(
    r'hard-skills', views.HardSkillNameViewSet, basename='hardskill')
router.register(
    r'soft-skills', views.SoftSkillNameViewSet, basename='softskill')
router.register(
    r'locations', views.LocationViewSet, basename='location')
router.register(
    r'educations', views.EducationViewSet, basename='education')
router.register(
    r'user', views.UserViewSet, basename='user'
)

urlpatterns = [
    path('v1/', include(router.urls)),
]
