from rest_framework.views import exception_handler
from rest_framework import status

from recipes.models import RecipeIngredientValue


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response:
        if response.status_code == status.HTTP_404_NOT_FOUND:
            response.data['detail'] = 'Ошибка 404 - страница не найдена!'

    return response


def create_relation_ingredient_and_value(ingredients_list, recipe):
    """Добавляет рецепту ингредиенты и значения."""
    list_to_add = []
    for ingredient in ingredients_list:
        list_to_add.append(RecipeIngredientValue(
            ingredients=ingredient.get('id'),
            recipe=recipe,
            amount=ingredient.get('amount')
        ))
    RecipeIngredientValue.objects.bulk_create(list_to_add)
