from django.contrib.auth import get_user_model
from django.db import models

from recipes.constants import (COLOR_MAX_LENGTH, NAME_MAX_LENGTH,
                               SYMBOL_LIMIT, UNIT_CHOICES, GR)


User = get_user_model()


class Tags(models.Model):

    name = models.CharField(
        'Название тега',
        max_length=NAME_MAX_LENGTH,
        unique=True
    )
    color = models.CharField(max_length=COLOR_MAX_LENGTH)
    slug = models.SlugField('Слаг', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name[:SYMBOL_LIMIT]


class Ingredients(models.Model):

    name = models.CharField(
        'Название ингредиента',
        max_length=NAME_MAX_LENGTH,
        unique=True
    )
    unit = models.CharField(
        'Единицы измерения',
        max_length=COLOR_MAX_LENGTH,
        choices=UNIT_CHOICES,
        default=GR,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name[:SYMBOL_LIMIT]


class Recipes(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        'Название рецепта',
        max_length=NAME_MAX_LENGTH,
        unique=True
    )
    image = models.ImageField(
        upload_to='static/',
        null=True,
        default=None
    )
    text = models.TextField('Описание рецепта', blank=True)
    ingredients = models.ManyToManyField(
        Ingredients, verbose_name='Ингредиент'
    )
    tag = models.ManyToManyField(Tags, verbose_name='Тег')
    time = models.PositiveSmallIntegerField(
        'Время проготовления',
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('pub_date',)

    def __str__(self):
        return self.name[:SYMBOL_LIMIT]


class RecipesIngredientsValue(models.Model):

    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Id рецепта'
    )
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        verbose_name='Id ингредиента'
    )
    value = models.PositiveSmallIntegerField(
        'Количество продукта',
    )

    # class Meta:
    #     verbose_name = 'Ингредиент'
    #     verbose_name_plural = 'Ингредиенты'

    # def __str__(self):
    #     return f'{self.value} {self.unit}'


# class RecipesTags(models.Model):

#     recipes = models.ForeignKey(
#         Recipes,
#         on_delete=models.CASCADE,
#         verbose_name='Id рецепта'
#     )
#     tags = models.ForeignKey(
#         Tags,
#         on_delete=models.CASCADE,
#         verbose_name='Id тега'
#     )
