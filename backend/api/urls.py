from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import CustomUserViewSet, SubscriptionListView
from recipes.views import IngredientViewSet, RecipeViewSet


router = DefaultRouter()


router.register('users', CustomUserViewSet, basename='users')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('users/subscriptions/', SubscriptionListView.as_view(), name='user-subscriptions-list'),
    path('', include(router.urls)),
]