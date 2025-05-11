from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Exists, OuterRef, Value, BooleanField, Sum
from django.http import HttpResponse

from .models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart
)
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (
    IngredientSerializer, RecipeMinifiedSerializer, RecipeReadSerializer,
    RecipeWriteSerializer
)
from .filters import IngredientFilter, RecipeFilter


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра ингредиентов.
    Предоставляет только list и retrieve (GET запросы).
    Поддерживает фильтрацию по ?name=...
    """
    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления Рецептами.
    Поддерживает CRUD, фильтрацию, добавление в избранное/корзину.
    """
    queryset = Recipe.objects.select_related('author').prefetch_related(
        'recipe_ingredients__ingredient',
    ).order_by('-pub_date')

    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """ Выбираем сериализатор в зависимости от действия. """
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_authenticated:
            is_favorited_param = self.request.query_params.get('is_favorited')
            if is_favorited_param is not None and is_favorited_param.lower() in ['1', 'true']:
                queryset = queryset.filter(favorited_by__user=user)

            is_in_shopping_cart_param = self.request.query_params.get('is_in_shopping_cart')
            if is_in_shopping_cart_param is not None and is_in_shopping_cart_param.lower() in ['1', 'true']:
                queryset = queryset.filter(in_shopping_carts__user=user)

        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(user=user, recipe=OuterRef('pk'))
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(user=user, recipe=OuterRef('pk'))
                )
            )
        else:
            queryset = queryset.annotate(
                is_favorited=Value(False, output_field=BooleanField()),
                is_in_shopping_cart=Value(False, output_field=BooleanField())
            )
        return queryset

    def get_permissions(self):
        """ Определяем права доступа в зависимости от действия. """
        if self.action in ('list', 'retrieve'):
            permission_classes = [AllowAny]
        elif self.action in ('create', 'favorite', 'shopping_cart', 'download_shopping_cart'):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthorOrAdminOrReadOnly]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """ Устанавливаем автора при создании рецепта. """
        serializer.save(author=self.request.user)

    def _add_or_remove_relation(self, request, pk, related_model, error_messages):
        """
        Вспомогательный метод для добавления/удаления связи M2M
        (Избранное, Список покупок).
        """
        recipe = get_object_or_404(Recipe, pk=pk)
        relation_exists = related_model.objects.filter(
            user=request.user, recipe=recipe
        ).exists()

        if request.method == 'POST':
            if relation_exists:
                return Response(
                    {'errors': error_messages['exists']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            related_model.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if not relation_exists:
                return Response(
                    {'errors': error_messages['not_exists']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            relation = get_object_or_404(
                related_model, user=request.user, recipe=recipe
            )
            relation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавить рецепт в избранное или удалить из избранного."""
        return self._add_or_remove_relation(
            request, pk,
            related_model=Favorite,
            error_messages={
                'exists': 'Рецепт уже в избранном.',
                'not_exists': 'Рецепта не было в избранном.'
            }
        )

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Добавить рецепт в список покупок или удалить из него."""
        return self._add_or_remove_relation(
            request, pk,
            related_model=ShoppingCart,
            error_messages={
                'exists': 'Рецепт уже в списке покупок.',
                'not_exists': 'Рецепта не было в списке покупок.'
            }
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """
        Возвращает TXT-файл со списком покупок для пользователя.
        Ингредиенты агрегируются по названию и единице измерения.
        """
        user = request.user

        if not user.shopping_cart.exists():
             return Response(
                 {"errors": "Список покупок пуст."},
                 status=status.HTTP_400_BAD_REQUEST
             )

        ingredients = RecipeIngredient.objects.filter(
            recipe__in_shopping_carts__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        shopping_list_content = "Список покупок для Foodgram:\n\n"
        for item in ingredients:
            name = item['ingredient__name']
            unit = item['ingredient__measurement_unit']
            amount = item['total_amount']
            shopping_list_content += f"• {name} ({unit}) — {amount}\n"

        filename = 'shopping_list.txt'
        response = HttpResponse(
            shopping_list_content,
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[AllowAny],
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        """
        Возвращает короткую ссылку на рецепт (в данном случае просто ID).
        """
        recipe = self.get_object()
        short_link_data = {'short-link': str(recipe.pk)}
        return Response(short_link_data, status=status.HTTP_200_OK)