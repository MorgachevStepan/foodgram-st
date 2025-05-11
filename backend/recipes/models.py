from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Ingredient(models.Model):
    """
    Модель ингредиента.
    """
    name = models.CharField(
        _('Название ингредиента'),
        max_length=128,
        unique=True,
        db_index=True,
    )
    measurement_unit = models.CharField(
        _('Единица измерения'),
        max_length=64,
    )

    class Meta:
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """
    Модель рецепта.
    """
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name=_('Автор рецепта'),
    )
    name = models.CharField(
        _('Название рецепта'),
        max_length=256,
        db_index=True,
    )
    image = models.ImageField(
        _('Изображение'),
        upload_to='recipes/images/',
        help_text=_('Картинка рецепта')
    )
    text = models.TextField(
        _('Описание рецепта'),
        help_text=_('Подробное описание процесса приготовления')
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name=_('Ингредиенты'),
    )
    cooking_time = models.PositiveIntegerField(
        _('Время приготовления (мин)'),
        validators=[
            MinValueValidator(1, message=_('Время должно быть не менее 1 мин.'))
        ],
        help_text=_('Укажите время в минутах')
    )
    pub_date = models.DateTimeField(
        _('Дата публикации'),
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.name} (Автор: {self.author.username})'


class RecipeIngredient(models.Model):
    """
    Промежуточная модель: Ингредиент в Рецепте с количеством.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name=_('Рецепт'),
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        verbose_name=_('Ингредиент'),
    )
    amount = models.PositiveIntegerField(
        _('Количество'),
        validators=[
            MinValueValidator(1, message=_('Количество должно быть не менее 1'))
        ],
        help_text=_('Укажите количество')
    )

    class Meta:
        verbose_name = _('Ингредиент в рецепте')
        verbose_name_plural = _('Ингредиенты в рецептах')
        constraints = [
            UniqueConstraint(
                fields=['recipe', 'ingredient'], name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return (f'{self.ingredient.name} - {self.amount} '
                f'{self.ingredient.measurement_unit}')


class Favorite(models.Model):
    """
    Модель для Избранных рецептов пользователя.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name=_('Пользователь'),
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name=_('Избранный рецепт'),
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата добавления')
    )

    class Meta:
        verbose_name = _('Избранный рецепт')
        verbose_name_plural = _('Избранные рецепты')
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='unique_user_favorite_recipe'
            )
        ]
        ordering = ('-added_at',)

    def __str__(self):
        return f'"{self.recipe.name}" в избранном у {self.user.username}'


class ShoppingCart(models.Model):
    """
    Модель для Списка покупок пользователя.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name=_('Пользователь'),
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_carts',
        verbose_name=_('Рецепт в списке покупок'),
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата добавления')
    )

    class Meta:
        verbose_name = _('Рецепт в списке покупок')
        verbose_name_plural = _('Рецепты в списке покупок')
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='unique_user_shopping_cart_recipe'
            )
        ]
        ordering = ('-added_at',)

    def __str__(self):
        return f'"{self.recipe.name}" в списке покупок у {self.user.username}'