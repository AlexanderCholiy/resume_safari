import debug_toolbar
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views

urlpatterns = [
    path('', include('user.urls', namespace='user')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('admin/', admin.site.urls),
    path(
        'password_reset/', views.PasswordResetView.as_view(),
        name='password_reset'),
    path(
        'password_reset/done/', views.PasswordResetDoneView.as_view(),
        name='password_reset_done'),
    path(
        'reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'),
    path(
        'reset/done/', views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete'),
]


if settings.DEBUG:
    urlpatterns += [path('debug/', include(debug_toolbar.urls)),]
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
