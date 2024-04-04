import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.models import F
from rest_framework import serializers
from rest_framework.validators import ValidationError, UniqueTogetherValidator

from recipes.models import (Ingredient, Recipe, RecipeIngredientValue,
                            Tag, Favourite)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = 'id', 'name', 'measurement_unit'
        read_only_fields = '__all__',


class Ingred(serializers.Serializer):
    """Сериализатор для ингредиентов при создании рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    amount = serializers.IntegerField()

    def validate_amount(self, value):
        """Валидация количества ингредиента."""
        if value <= 0:
            raise ValidationError(
                'Отсутствует ингредиент!'
            )
        return value


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = 'id', 'name', 'color', 'slug'
        read_only_fields = '__all__',


class RecipeForUserSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов эндпоинта подписок."""

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )
        read_only_fields = '__all___',


class UserRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода автора-владельца рецепта."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        )
        read_only_fields = '__all__',

    def get_is_subscribed(self, obj):
        """Возвращает булевое значение - если ли подписка на пользователя."""
        user = self.context.get('request').user
        if user.is_anonymous or user == obj:
            return False
        return user.following.filter(following_user_id=obj).exists()


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра списка рецептов или рецепта."""

    tags = TagSerializer(many=True)
    author = UserRecipeSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )
        read_only_fields = (
            '__all__',
        )

    def get_ingredients(self, obj):
        """Получение поля ингредиентов."""
        ingrediens = obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )
        return ingrediens

    def get_is_favorited(self, obj):
        """Получение поля в избранном ли товар."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.fav_recipes.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Получение поля в корзине ли товар."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.cart.filter(recipe=obj).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())
    image = Base64ImageField()
    ingredients = Ingred(many=True,)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'ingredients',
            'name', 'image', 'text', 'cooking_time',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('name', 'ingredients')
            )
        ]

    def validate(self, attrs):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        if not tags or not ingredients:
            raise ValidationError('Отсутствуют обязательные поля!')
        validate_ingredients = []
        for ingredient in ingredients:
            if ingredient not in validate_ingredients:
                validate_ingredients.append(ingredient)
        if len(ingredients) != len(validate_ingredients):
            raise ValidationError(
                'Нельзя указывать одинаковые ингредиенты!'
            )
        if len(tags) != len(set(tags)):
            raise ValidationError(
                'Нельзя указывать одинаковые теги!'
            )
        if not self.initial_data.get('text'):
            raise ValidationError(
                'Нельзя создать рецепт без текста!'
            )
        return super().validate(attrs)

    def validate_cooking_time(self, value):
        """Валидация времени приготовления."""
        if value < 1:
            raise ValidationError(
                'Время готовки не может быть меньше минуты!'
            )
        return value

    def create(self, validated_data):
        """Функция слздания рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            RecipeIngredientValue.objects.create(
                ingredients=ingredient.get('id'),
                recipe=recipe,
                amount=ingredient.get('amount')
            )
        return recipe

    def update(self, instance, validated_data):
        """Функция изменения рецепта."""
        ingredients = validated_data.get('ingredients')
        instance.tags.set(validated_data.get('tags'))
        instance.image = validated_data.get('image')
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        if ingredients:
            instance.ingredients.clear()
            for ingredient in ingredients:
                RecipeIngredientValue.objects.create(
                    ingredients=ingredient.get('id'),
                    recipe=instance,
                    amount=ingredient.get('amount')
                )
        instance.save()
        return instance


# Удалить сериализатор.
# class UserSubscriptionsSerializer(serializers.ModelSerializer):
#     """Сериализатор для подписок пользователя"""

#     is_subscribed = serializers.SerializerMethodField()
#     recipes = RecipeForUserSerializer(many=True)
#     recipes_count = serializers.SerializerMethodField()

#     class Meta:
#         model = User
#         fields = (
#             'email', 'id', 'username', 'first_name', 'last_name',
#             'is_subscribed', 'recipes', 'recipes_count'
#         )
#         read_only_fields = '__all__',

#     def get_recipes_count(self, obj):
#         """Получения поля количества рецептов пользователя."""
#         return obj.author_recipes.count()

#     def get_is_subscribed(self, obj):
#         """Возвращает булевое значение - если ли подписка на пользователя."""
#         user = self.context.get('request').user
#         if user.is_anonymous or user == obj:
#             return False
#         return user.followers.filter(author=obj).exists()


class FavouriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных рецептов."""

    id = serializers.IntegerField(source='recipe.id')
    name = serializers.CharField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image')
    cooking_time = serializers.IntegerField(source='recipe.cooking_time')

    class Meta:
        model = Favourite
        fields = (
            'id', 'name', 'image', 'cooking_time',
        )
        read_only_fields = '__all__',
