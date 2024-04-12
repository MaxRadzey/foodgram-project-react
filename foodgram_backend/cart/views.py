from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import RecipeForUserSerializer
from cart.models import Cart
from recipes.models import Recipe


class CartAPI(APIView):

    permission_classes = permissions.IsAuthenticated,
    serializer_class = RecipeForUserSerializer

    def post(self, request, **kwargs):
        recipe_id = self.kwargs['pk']
        recipe = Recipe.objects.filter(pk=recipe_id).first()
        user = request.user
        if not recipe:
            return Response(
                {'message': 'Такого рецепта нет!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if user.cart.filter(recipe=recipe).exists():
            return Response(
                {'message': 'Рецепт уже добавлен!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Cart.objects.create(recipe=recipe, user=user)
        serialazer = RecipeForUserSerializer(recipe)
        return Response(
            serialazer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, **kwargs):
        recipe_id = self.kwargs['pk']
        recipe = Recipe.objects.filter(pk=recipe_id).first()
        user = request.user
        result = user.cart.filter(recipe=recipe)
        if not recipe:
            return Response(
                {'message': 'Такого рецепта нет!'},
                status=status.HTTP_404_NOT_FOUND
            )
        if result.exists():
            result.delete()
            return Response(
                {'message': 'Рецепт удален из избранного!'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'message': 'Рецепта нет!'},
            status=status.HTTP_400_BAD_REQUEST
        )
