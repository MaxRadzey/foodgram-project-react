from django.contrib import admin

from recipes.admin import FavouritesAdmin
from users.models import User, UserFollow


class UserFollowAdmin(admin.TabularInline):
    model = UserFollow
    fk_name = 'user_id'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'id', 'email', 'first_name',
        'last_name'
    )
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')
    inlines = (FavouritesAdmin, UserFollowAdmin)
