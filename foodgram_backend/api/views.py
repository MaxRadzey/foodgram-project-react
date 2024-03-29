from django.contrib.auth import get_user_model
from rest_framework import generics, viewsets, status, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from recipes.models import Ingredient, Recipe, Tag, Favourites
from api.serializers import (IngredientSerializer, RecipeReadSerializer,
                             RecipeWriteSerializer, TagSerializer,
                             FavouritesSerializer)
from api.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeWriteSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly
    )

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeReadSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serialazer = self.get_serializer(data=request.data)
        serialazer.is_valid(raise_exception=True)
        result = serialazer.save(author=self.request.user)
        return Response(
            RecipeReadSerializer(result, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def partial_update(self, request, *args, **kwargs):
        recipe_id = self.kwargs['pk']
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        serialazer = self.get_serializer(
            instance=recipe,
            data=request.data)
        serialazer.is_valid(raise_exception=True)
        result = serialazer.save(author=self.request.user)
        return Response(
            RecipeReadSerializer(result, context={'request': request}).data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        recipe_id = self.kwargs['pk']
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        recipe.delete()
        return Response(
            {'message': 'Рецепт удален!'},
            status=status.HTTP_204_NO_CONTENT
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Возвращает ингредиент или список ингредиентов. """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = IsAdminOrReadOnly,


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Возвращает тег или список тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = IsAdminOrReadOnly,


class FavouritesViewSet(generics.CreateAPIView, generics.DestroyAPIView):
    """Возвращает рецепт, добавленный в избранное или удаляет его."""

    queryset = Favourites.objects.all()
    serializer_class = FavouritesSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """Добавление рецепта в избранное."""
        recipe_id = self.kwargs['pk']
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        user = request.user

        if Favourites.objects.filter(recipe=recipe, user=user).exists():
            return Response(
                {'message': 'Рецепт уже добавлен в избранное!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = Favourites.objects.create(recipe=recipe, user=user)
        serializer = FavouritesSerializer(result)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, *args, **kwargs):
        """Удаляет рецепт из избранного."""
        recipe_id = self.kwargs['pk']
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        user = request.user
        result = Favourites.objects.create(recipe=recipe, user=user)
        result.delete()
        return Response(
            {'message': 'Рецепт удален из избранного!'},
            status=status.HTTP_204_NO_CONTENT
        )
