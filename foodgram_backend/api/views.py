from django.contrib.auth import get_user_model
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.permissions import IsOwnerOrReadOnly
from api.serializers import (FavouriteSerializer, IngredientSerializer,
                             RecipeReadSerializer, RecipeWriteSerializer,
                             TagSerializer)
from recipes.models import (Favourite, Ingredient, Recipe,
                            RecipeIngredientValue, Tag)

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    """Получить список или рецепт с возможностью редакт-я и удаления."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeWriteSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,
    )

    def get_queryset(self):
        queryset = self.queryset
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        if self.request.user.is_anonymous:
            return Recipe.objects.all()

        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited:
            queryset = queryset.filter(fav_recipes__user=self.request.user)

        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        if is_in_shopping_cart == '1':
            queryset = queryset.filter(cart__user=self.request.user)
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
        result = serialazer.save()
        return Response(
            RecipeReadSerializer(result, context={'request': request}).data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        methods=['get'],
    )
    def download_shopping_cart(self, request):
        """Загрузить файл со списком покупок."""
        user = request.user
        amount_result = {}
        ingredients = RecipeIngredientValue.objects.filter(
            recipe__cart__user=user
        ).values_list(
            'ingredients__name',
            'ingredients__measurement_unit',
            'amount'
        )
        for name, m_unit, amount in ingredients:
            if name not in amount_result:
                amount_result[name] = [
                    m_unit, amount
                ]
            else:
                amount_result[name][1] += amount

        filename = f'{user.username}_shopping_list.txt'
        text = [
            'Foodgram\n',
            (f'Список покупок пользователя {user.first_name} '
             f'{user.last_name}\n'),
            '\n'
        ]
        for name, [unit, value] in amount_result.items():
            text.append(f'{name} - {value} {unit}\n')
        response = HttpResponse(
            text, content_type=f'{filename}; charset=utf-8'
        )
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Возвращает ингредиент или список ингредиентов. """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
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
        return queryset


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Возвращает тег или список тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
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
        recipe = Recipe.objects.filter(pk=recipe_id).first()
        user = request.user
        if not recipe:
            return Response(
                {'message': 'Такого рецепта нет!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.fav_recipes.filter(recipe=recipe).exists():
            return Response(
                {'message': 'Рецепт уже добавлен!'},
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
        result = user.fav_recipes.filter(recipe=recipe)
        if not result:
            return Response(
                {'message': 'Рецепта нет!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        result.delete()
        return Response(
            {'message': 'Рецепт удален из избранного!'},
            status=status.HTTP_204_NO_CONTENT
        )
