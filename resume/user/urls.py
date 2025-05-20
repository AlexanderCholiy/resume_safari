from django.urls import path

from . import views


app_name = 'user'

urlpatterns = [
    path('resume/', views.index, name='resume_list'),
    path('resume/<slug:slug>/', views.resume_detail, name='resume_detail'),
]
