from django.contrib import admin

from recipes.models import Tag, Ingredient, Recipe, RecipeIngredientValue


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'color', 'slug'
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'measurement_unit'
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author', 'name', 'image', 'text',
        'cooking_time', 'pub_date'
    )

    def display_ingredients(self, obj):
        return ', '.join(
            [ingredients.name for ingredients in obj.ingredients.all()]
        )

    def display_tags(self, obj):
        return ', '.join(
            [tag.name for tag in obj.tags.all()]
        )


@admin.register(RecipeIngredientValue)
class RecipeIngredientValueAdmin(admin.ModelAdmin):
    list_display = (
        'recipe', 'ingredients', 'value'
    )
