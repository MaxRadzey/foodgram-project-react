import base64

import webcolors
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import ValidationError

from recipes.models import Ingredient, Recipe, RecipeIngredientValue, Tag


User = get_user_model()


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


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
        read_only_fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = 'id', 'name', 'measurement_unit', 'amount'
        read_only_fields = 'id', 'name', 'measurement_unit'


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = 'id', 'name', 'color', 'slug'
        read_only_fields = '__all__'


class UserRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода автора-владельца рецепта."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        )
        read_only_fields = '__all__'

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymos or user == obj:
            return False
        return user.followers.filter(author=obj).exists()


class RecipeSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True)
    author = UserRecipeSerializer(many=False)
    ingredients = IngredientAmountSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = (
            'tags', 'author', 'is_favorited', 'is_in_shopping_cart'
        )

    def validate_cooking_time(self, value):
        if value < 1:
            raise ValidationError(
                'Время готовки не может быть меньше минуты!'
            )
        return value

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymos:
            return False
        return user.fav_recipes.filter(recipe=obj).exists()
        return

    def get_is_in_shopping_cart(self):
        user = self.context.get('request').user
        if user.is_anonymos:
            return False
        return False

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient, amount in ingredients:
            RecipeIngredientValue.objects.create(
                ingredient=ingredient, recipe=recipe, amount=amount
            )
        for tag in tags:
            recipe.tag_recipes.create(tags)
        return recipe

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class RecipeForUserSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов эндпоинта подписок"""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )
        read_only_fields = '__all___'


class UserSubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок пользователя"""

    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeForUserSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )
        read_only_fields = '__all__'

    def get_is_favorited(self, obj):
        return True

    def get_recipes_count(self, obj):
        return obj.author_recipes.count()
