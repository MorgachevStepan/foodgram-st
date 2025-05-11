from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Subscription
from recipes.models import Recipe

try:
    from recipes.serializers import RecipeMinifiedSerializer, Base64ImageField
except ImportError:
    RecipeMinifiedSerializer = None
    Base64ImageField = None


User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Пользователя (User).
    Используется для чтения данных пользователя (GET /api/users/, GET /api/users/{id}/, GET /api/users/me/).
    Также используется как вложенный сериализатор (например, в RecipeSerializer).
    Добавляет поле is_subscribed.
    """
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        """
        Проверяет, подписан ли текущий пользователь (из запроса)
        на пользователя obj (который сериализуется).
        """
        request = self.context.get('request')
        if request is None or not request.user.is_authenticated:
            return False
        if request.user == obj:
             return False
        return Subscription.objects.filter(user=request.user, author=obj).exists()


class UserWithRecipesSerializer(CustomUserSerializer):
    """
    Сериализатор пользователя с добавлением списка его рецептов (урезанных).
    Используется для страницы подписок (/api/users/subscriptions/).
    """
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ('recipes', 'recipes_count')
        read_only_fields = fields

    def get_recipes(self, obj):
        """
        Возвращает список рецептов пользователя obj с учетом лимита из запроса.
        """
        global RecipeMinifiedSerializer
        if RecipeMinifiedSerializer is None:
            from recipes.serializers import RecipeMinifiedSerializer

        request = self.context.get('request')
        if request is None:
            return []

        limit_param = request.query_params.get('recipes_limit')
        limit = None
        if limit_param:
            try:
                limit = int(limit_param)
                if limit <= 0:
                    limit = None
            except (ValueError, TypeError):
                limit = None

        recipes_queryset = obj.recipes.all()
        if limit is not None:
            recipes_queryset = recipes_queryset[:limit]

        serializer = RecipeMinifiedSerializer(
            recipes_queryset, many=True, context={'request': request}
        )
        return serializer.data


class SetAvatarSerializer(serializers.Serializer):
    """ Сериализатор для загрузки аватара в Base64. """
    global Base64ImageField
    if Base64ImageField is None:
        from recipes.serializers import Base64ImageField

    avatar = Base64ImageField(required=True, allow_null=False)

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


class SetAvatarResponseSerializer(serializers.ModelSerializer):
     """
     Сериализатор для ответа после установки/удаления аватара.
     Используем ModelSerializer для простоты.
     """
     class Meta:
        model = User
        fields = ('avatar',) # Возвращаем только поле аватара
        read_only_fields = fields

