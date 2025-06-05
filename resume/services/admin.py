from django.contrib import admin

from .constants import MAX_PENDING_USERS_PER_PAGE
from .models import PendingUser


@admin.register(PendingUser)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
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
