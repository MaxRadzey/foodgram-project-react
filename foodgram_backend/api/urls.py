from django.urls import include, path
from rest_framework import routers

from api.views import (TagViewSet, RecipeViewSet,
                       IngredientViewSet, FavouritesViewSet)
from users.views import UserViewSet

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
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
