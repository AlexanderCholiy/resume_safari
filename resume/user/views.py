from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


def index(request: HttpRequest) -> HttpResponse:
    template_name = 'homepage/index.html'
    return render(request, template_name)
