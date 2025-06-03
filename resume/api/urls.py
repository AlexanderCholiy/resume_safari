from rest_framework.routers import DefaultRouter
from django.urls import path, include

from . import views


app_name = 'api'

router = DefaultRouter()
router.register(r'auth', views.UserAuthViewSet, basename='auth')
router.register(r'password', views.PasswordViewSet, basename='password')
router.register(
    r'hard-skills', views.HardSkillNameViewSet, basename='hardskill'
)
router.register(
    r'soft-skills', views.SoftSkillNameViewSet, basename='softskill'
)
router.register(r'locations', views.LocationViewSet, basename='location')
router.register(r'positions', views.PositionViewSet, basename='position')
router.register(r'users', views.UserViewSet, basename='users')
# router.register(r'resumes', views.ResumeViewSet, basename='resume')


me_view = views.MeViewSet.as_view({
    'get': 'retrieve',
    'patch': 'update',
    'put': 'update',
    'delete': 'destroy',
})
me_email_confirm_view = views.MeViewSet.as_view({'get': 'confirm_email'})

urlpatterns = [
    path('v1/', include([
        path('', include(router.urls)),
        path('me/', me_view, name='me-detail'),
        path(
            'me/email-confirm/<uidb64>/<token>/',
            me_email_confirm_view,
            name='me-confirm-email'
        ),
    ])),
]
