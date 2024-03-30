from django.contrib.auth import get_user_model
from rest_framework import (generics, viewsets, status,
                            permissions)
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from recipes.models import Ingredient, Recipe, Tag, Favourite
from api.serializers import (IngredientSerializer, RecipeReadSerializer,
                             RecipeWriteSerializer, TagSerializer,
                             FavouriteSerializer)
from api.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    """Получить список или рецепт с возможностью редакт-я и удаления."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeWriteSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly
    )

    def get_queryset(self):
        queryset = self.queryset
        tags = self.request.query_params.get('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        if self.request.user.is_anonymous:
            return queryset

        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited:
            queryset = queryset.filter(is_favorited__user=self.request.user)

        # is_in_shopping_cart = self.request.query_params.get(
        #     'is_in_shopping_cart'
        # )
        # if is_in_shopping_cart:
        #     queryset = queryset.filter(
        #         is_in_shopping_cart__user=self.request.user
        #     )
        return queryset

    def get_serializer_class(self):
        """Получить сериализатор в зафисимости от метода запроса."""
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeReadSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        """Создать рецепт."""
        serialazer = self.get_serializer(data=request.data)
        serialazer.is_valid(raise_exception=True)
        result = serialazer.save(author=self.request.user)
        return Response(
            RecipeReadSerializer(result, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def partial_update(self, request, *args, **kwargs):
        """Редактировать рецепт."""
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
        """Удалить рецепт."""
        recipe_id = self.kwargs['pk']
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        recipe.delete()
        return Response(
            {'message': 'Рецепт удален!'},
            status=status.HTTP_204_NO_CONTENT
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Возвращает ингредиент или список ингредиентов. """

    serializer_class = IngredientSerializer
    permission_classes = IsAdminOrReadOnly,
    pagination_class = None

    def get_queryset(self):
        """Фильтрация ингредиентов."""
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')

        if name:
            queryset_first = queryset.filter(name__istartswith=name)
            queryset_second = queryset.filter(name__icontains=name)
            queryset = set(queryset_first) | set(queryset_second)
        return list(queryset)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Возвращает тег или список тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = IsAdminOrReadOnly,
    pagination_class = None


class FavouritesViewSet(generics.CreateAPIView, generics.DestroyAPIView):
    """Получить рецепт, добавленный в избранное или удалить его."""

    queryset = Favourite.objects.all()
    serializer_class = FavouriteSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None

    def post(self, request, *args, **kwargs):
        """Добавить рецепт в избранное."""
        recipe_id = self.kwargs['pk']
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        user = request.user

        if Favourite.objects.filter(recipe=recipe, user=user).exists():
            return Response(
                {'message': 'Рецепт уже добавлен в избранное!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = Favourite.objects.create(recipe=recipe, user=user)
        serializer = FavouriteSerializer(result)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, *args, **kwargs):
        """Удалить рецепт из избранного."""
        recipe_id = self.kwargs['pk']
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        user = request.user
        result = Favourite.objects.create(recipe=recipe, user=user)
        result.delete()
        return Response(
            {'message': 'Рецепт удален из избранного!'},
            status=status.HTTP_204_NO_CONTENT
        )
