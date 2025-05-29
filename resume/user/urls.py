from django.urls import path

from .views import ResumeListView, ResumeDetailView, MyResumeListView


app_name = 'user'

urlpatterns = [
    path('', ResumeListView.as_view(), name='resume_list'),
    path(
        'my/',
        MyResumeListView.as_view(),
        name='resume_my_list'
    ),
    path(
        '<slug:slug>/',
        ResumeDetailView.as_view(),
        name='resume_detail'
    ),
]
