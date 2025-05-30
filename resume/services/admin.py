from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.db.models.query import QuerySet

from .models import PendingUser
from .constants import MAX_PENDING_USERS_PER_PAGE


@admin.register(PendingUser)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'last_login',
    )
    search_fields = (
        'username',
        'email',
    )
    ordering = ('-last_login',)
    list_per_page = MAX_PENDING_USERS_PER_PAGE
