from django.urls import path

from .views import ResumeListView, ResumeDetailView


app_name = 'user'

urlpatterns = [
    path('resume', ResumeListView.as_view(), name='resume_list'),
    path(
        'resume/<slug:slug>/', ResumeDetailView.as_view(), name='resume_detail'
    ),
]
