import debug_toolbar
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views

urlpatterns = [
    path('', include('user.urls', namespace='user')),
    path('admin/', admin.site.urls),
    path('pages/', include('pages.urls', namespace='pages')),
    path('auth/', include('services.urls', namespace='services')),
    path(
        'login/',
        views.LoginView.as_view(extra_context={'auth_page': True}),
        name='login',
    ),
    path(
        'logout/',
        views.LogoutView.as_view(
            next_page='login',
            extra_context={'auth_page': True}
        ),
        name='logout',
    ),
    path(
        'password_change/',
        views.PasswordChangeView.as_view(extra_context={'auth_page': True}),
        name='password_change',
    ),
    path(
        'password_change/done/',
        views.PasswordChangeDoneView.as_view(
            extra_context={'auth_page': True}),
        name='password_change_done',
    ),
    path(
        'password_reset/',
        views.PasswordResetView.as_view(extra_context={'auth_page': True}),
        name='password_reset',
    ),
    path(
        'password_reset/done/',
        views.PasswordResetDoneView.as_view(extra_context={'auth_page': True}),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        views.PasswordResetConfirmView.as_view(
            extra_context={'auth_page': True}),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        views.PasswordResetCompleteView.as_view(
            extra_context={'auth_page': True}),
        name='password_reset_complete',
    ),
]


if settings.DEBUG:
    urlpatterns += [path('debug/', include(debug_toolbar.urls)),]
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
