from django.contrib import admin
from .models import (Ingredient, Recipe, RecipeIngredient,
                     Favorite, ShoppingCart)

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    ordering = ('name',)

class RecipeIngredientInline(admin.TabularInline):
    """ Инлайн для отображения ингредиентов внутри рецепта. """
    model = RecipeIngredient
    extra = 1
    min_num = 1
    autocomplete_fields = ('ingredient',)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'get_favorite_count', 'cooking_time', 'pub_date')
    list_filter = ('author__username', 'name')
    search_fields = ('name', 'author__username', 'text')
    readonly_fields = ('pub_date', 'get_favorite_count_display')
    inlines = (RecipeIngredientInline,)
    ordering = ('-pub_date',)

    @admin.display(description='В избранном (кол-во)')
    def get_favorite_count(self, obj):
        return obj.favorited_by.count()

    @admin.display(description='Добавлений в избранное')
    def get_favorite_count_display(self, obj):
         return self.get_favorite_count(obj)

@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')
    autocomplete_fields = ('recipe', 'ingredient') # Удобный поиск

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe', 'added_at')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('added_at',)
    ordering = ('-added_at',)
    autocomplete_fields = ('user', 'recipe')

@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe', 'added_at')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('added_at',)
    ordering = ('-added_at',)
    autocomplete_fields = ('user', 'recipe')