from django.urls import path

from .views import ResumeListView, ResumeDetailView, MyResumeListView


app_name = 'user'

urlpatterns = [
    path('resume', ResumeListView.as_view(), name='resume_list'),
    path('resume/my/', MyResumeListView.as_view(), name='resume_my_list'),
    path(
        'resume/<slug:slug>/', ResumeDetailView.as_view(), name='resume_detail'
    ),
]
