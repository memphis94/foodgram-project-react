from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = [
        'username',
        'first_name',
        'last_name',
        'email',
        'is_superuser',
    ]
    search_fields = ['username', 'email']


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):

    list_display = ['user', 'author']
    list_filter = ['user', 'author']
    empty_value_display = '-пусто-'
