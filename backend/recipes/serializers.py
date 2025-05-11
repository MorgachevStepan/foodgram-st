from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import Ingredient, Recipe, RecipeIngredient
from users.serializers import CustomUserSerializer

try:
    from api.fields import Base64ImageField
except ImportError:
    Base64ImageField = serializers.ImageField

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ингредиента (только чтение).
    """
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = fields


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ингредиентов внутри рецепта (для чтения).
    """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения рецептов (список и детальная страница).
    """
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(read_only=True, default=False)
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def _get_user(self):
        """Вспомогательный метод для получения пользователя из контекста."""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return request.user
        return None


class RecipeIngredientWriteSerializer(serializers.Serializer):
    """
    Сериализатор для валидации ID ингредиента и его количества при записи рецепта.
    """
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1, max_value=32767)


class RecipeWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления рецептов.
    """
    image = Base64ImageField(required=True, allow_null=False)
    ingredients = RecipeIngredientWriteSerializer(many=True, allow_empty=False)
    author = CustomUserSerializer(read_only=True)
    cooking_time = serializers.IntegerField(min_value=1, max_value=32767)


    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'name', 'image',
            'text', 'cooking_time',  # 'tags',
        )

    def validate(self, data):
        """
        Общая валидация. Проверяем наличие ключа 'ingredients' в исходных
        данных при обновлении (PATCH), чтобы соответствовать тесту Postman.
        """
        is_partial_update = getattr(self, 'partial', False)

        if is_partial_update and 'ingredients' not in self.initial_data:
            raise serializers.ValidationError({
                'ingredients': ['Это поле обязательно при обновлении.']
            })

        return data

    def validate_ingredients(self, ingredients_data):
        """ Проверяем ингредиенты на уникальность ID и наличие данных. """
        if not ingredients_data:
            raise serializers.ValidationError('Нужен хотя бы один ингредиент.')
        ingredient_ids = [item['id'].id for item in ingredients_data]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError('Ингредиенты не должны повторяться.')
        for item in ingredients_data:
            if item['amount'] < 1:
                raise serializers.ValidationError({
                    'ingredients': f'Количество "{item["id"].name}" д.б. >= 1.'
                })
        return ingredients_data


    def _set_ingredients(self, recipe, ingredients_data):
        """ Создает связи RecipeIngredient для рецепта. """
        recipe.recipe_ingredients.all().delete()
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount']
            ) for item in ingredients_data
        ])


    @transaction.atomic
    def create(self, validated_data):
        """ Создает новый рецепт с ингредиентами (и тегами). """
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self._set_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """ Обновляет рецепт, включая ингредиенты (и теги). """
        ingredients_data = validated_data.pop('ingredients', None)
        instance = super().update(instance, validated_data)

        if ingredients_data is not None:
            self._set_ingredients(instance, ingredients_data)

        return instance

    def to_representation(self, instance):
        """ При ответе используем сериализатор для чтения. """
        return RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """
    Сериализатор для рецепта (для ответов actions).
    """
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields
