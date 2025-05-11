from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Subscription, User
from .serializers import (
    UserWithRecipesSerializer, SetAvatarSerializer, SetAvatarResponseSerializer
)


class SubscriptionListView(generics.ListAPIView):
    """
    View для получения списка авторов, на которых подписан текущий пользователь.
    Использует стандартную пагинацию DRF (LimitOffsetPagination из настроек).
    """
    serializer_class = UserWithRecipesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Возвращает queryset авторов, на которых подписан текущий пользователь."""
        user = self.request.user
        return User.objects.filter(following__user=user).order_by('username')


class CustomUserViewSet(DjoserUserViewSet):
    """
    Кастомный ViewSet для Пользователей.
    Наследуется от Djoser UserViewSet. Добавляет кастомные действия
    для подписок (создание/удаление) и аватара.
    Список подписок вынесен в отдельный SubscriptionListView.
    """
    def get_permissions(self):
        """
        Определяем права доступа динамически для стандартных действий Djoser.
        """
        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()


    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        """Подписаться или отписаться от пользователя."""
        author = get_object_or_404(User, id=id)
        user = request.user

        if user == author:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription_exists = Subscription.objects.filter(
            user=user, author=author
        ).exists()

        if request.method == 'POST':
            if subscription_exists:
                return Response(
                    {'errors': 'Вы уже подписаны на этого автора.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(user=user, author=author)
            serializer = UserWithRecipesSerializer(
                author, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if not subscription_exists:
                return Response(
                    {'errors': 'Вы не были подписаны на этого автора.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription = get_object_or_404(
                Subscription, user=user, author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Добавить или удалить аватар текущего пользователя."""
        user = request.user

        if request.method == 'PUT':
            serializer = SetAvatarSerializer(
                instance=user,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response_serializer = SetAvatarResponseSerializer(user)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)