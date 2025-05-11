import django_filters
from django.contrib.auth import get_user_model
from .models import Ingredient, Recipe

User = get_user_model()

class IngredientFilter(django_filters.FilterSet):
    """
    Фильтр для модели Ingredient.
    Позволяет искать по частичному вхождению в начале названия ингредиента.
    """
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='startswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.ModelChoiceFilter(queryset=User.objects.all())

    class Meta:
        model = Recipe
        fields = ['author']