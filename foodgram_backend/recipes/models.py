from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from recipes.constants import (COLOR_MAX_LENGTH, NAME_MAX_LENGTH,
                               SYMBOL_LIMIT, UNIT_MAX_LENGTH,
                               MIN_COOKING_TIME, MAX_COOKING_TIME,
                               MIN_AMOUNT, MAX_AMOUNT)

User = get_user_model()


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        'Название тега',
        max_length=NAME_MAX_LENGTH,
        unique=True,
    )
    color = models.CharField(
        max_length=COLOR_MAX_LENGTH,
        unique=True,
    )
    slug = models.SlugField(
        'Слаг',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name[:SYMBOL_LIMIT]


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        'Название ингредиента',
        max_length=NAME_MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=UNIT_MAX_LENGTH,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit',
            ),
        )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Моедь рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='author_recipes',
    )
    name = models.CharField(
        'Название рецепта',
        max_length=NAME_MAX_LENGTH,
    )
    image = models.ImageField(
        upload_to='recipes/',
        null=True,
        default=None
    )
    text = models.TextField(
        'Описание рецепта',
        blank=True
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиент',
        related_name='ingredients_recipes',
        through='RecipeIngredientValue',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время проготовления',
        validators=[
            MinValueValidator(MIN_COOKING_TIME),
            MaxValueValidator(MAX_COOKING_TIME)
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name[:SYMBOL_LIMIT]


class RecipeIngredientValue(models.Model):
    """Модель рецепта-ингредиентов."""

    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Id ингредиента',
        related_name='recipe',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Id рецепта',
        related_name='ingredient',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество продукта',
        validators=[
            MinValueValidator(MIN_AMOUNT),
            MaxValueValidator(MAX_AMOUNT)
        ]
    )

    class Meta:
        verbose_name = 'Рецепты - ингредиенты'
        verbose_name_plural = 'Рецепты - ингредиенты'
        ordering = ('recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=['ingredients', 'recipe'],
                name='not_uniq_ingredient_in_recipe'
            ),
        ]

    def __str__(self):
        return f'{self.ingredients} - {self.amount}'


class Favourite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        User,
        related_name='fav_recipes',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='fav_recipes',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='recipe_has_already_been_in_fav'
            ),
        ]

    def __str__(self):
        return f'Избранные рецепты {self.user}'
