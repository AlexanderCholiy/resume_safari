from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('test400/', views.bad_request),
    path('test403/', views.permission_denied),
    path('test403csrf/', views.csrf_failure),
    path('test404/', views.page_not_found),
    path('test500/', views.server_error),
]
