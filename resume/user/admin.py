from django.contrib import admin

from .models import User
from .constants import MAX_USERS_PER_PAGE


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active')
    ordering = ('username',)
    list_per_page = MAX_USERS_PER_PAGE
    filter_horizontal = ('user_permissions', 'groups',)
