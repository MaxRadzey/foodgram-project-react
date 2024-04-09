from django.urls import include, path
from rest_framework import routers

from api.custom_404_page import custom404
from api.views import (FavouritesViewSet, IngredientViewSet,
                       RecipeViewSet, TagViewSet)
from cart.views import CartAPI
from users.views import UserViewSet

handler404 = custom404

router_v1 = routers.DefaultRouter()
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('users', UserViewSet, basename='users')

urlpatterns = [
    path(
        'recipes/<int:pk>/favorite/',
        FavouritesViewSet.as_view(),
        name='favorite-recipes'
    ),
    path(
        'recipes/<int:pk>/shopping_cart/',
        CartAPI.as_view(),
        name='cart'
    ),
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
