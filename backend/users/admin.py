from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Subscription

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name',
        'is_staff', 'get_recipes_count', 'get_follower_count'
    )
    list_filter = ('email', 'username', 'first_name', 'last_name')
    search_fields = ('email', 'username')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'avatar')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                   'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('last_login', 'date_joined')

    @admin.display(description='Кол-во рецептов')
    def get_recipes_count(self, obj):
        return obj.recipes.count()

    @admin.display(description='Кол-во подписчиков')
    def get_follower_count(self, obj):
        return obj.following.count()

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author', 'created_at')
    search_fields = ('user__username', 'user__email', 'author__username', 'author__email')
    list_filter = ('created_at',)
    ordering = ('-created_at',)