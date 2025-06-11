import debug_toolbar
from core.config import web_config
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# --- Error Handlers ---
handler400 = 'core.views.bad_request'
handler403 = 'core.views.permission_denied'
handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_error'


# --- Swagger Schema ---
schema_view = get_schema_view(
    openapi.Info(
        title='Resume Safari API',
        default_version='v1',
        description='Документация для проекта Resume Safari',
        contact=openapi.Contact(email=web_config.EMAIL_LOGIN),
        license=openapi.License(name='BSD License'),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# --- Swagger/Redoc URLs ---
swagger_urls = [
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json',
    ),
    re_path(
        r'^swagger/$',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui',
    ),
    re_path(
        r'^redoc/$',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc',
    ),
]

# --- Auth Views with Extra Context ---
auth_urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(extra_context={'auth_page': True}),
        name='login',
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(
            next_page='login', extra_context={'auth_page': True}
        ),
        name='logout',
    ),
    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(
            extra_context={'auth_page': True}),
        name='password_change',
    ),
    path(
        'password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            extra_context={'auth_page': True}),
        name='password_change_done',
    ),
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            extra_context={'auth_page': True}),
        name='password_reset',
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            extra_context={'auth_page': True}),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            extra_context={'auth_page': True}),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            extra_context={'auth_page': True}),
        name='password_reset_complete',
    ),
]

# --- Основной набор маршрутов с префиксом ---
app_urls = [
    path('api/', include('djoser.urls.jwt')),
    path('api/', include('api.urls', namespace='api')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('admin/', admin.site.urls),
    path('auth/', include('services.urls', namespace='services')),
    path('', include('user.urls', namespace='user')),
]

urlpatterns = swagger_urls + auth_urlpatterns + app_urls

# --- DEBUG MODE ---
if settings.DEBUG:
    urlpatterns += [
        path('debug/', include(debug_toolbar.urls)),
        path('core/', include('core.urls', namespace='cores')),
    ]
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
