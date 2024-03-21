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
        'name', 'unit'
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author', 'name', 'image', 'text',
        'time', 'pub_date'
    )

    def display_ingredients(self, obj):
        return ', '.join(
            [ingredients.name for ingredients in obj.ingredients.all()]
        )

    def display_tag(self, obj):
        return ', '.join(
            [tag.name for tag in obj.tag.all()]
        )


@admin.register(RecipeIngredientValue)
class RecipeIngredientValueAdmin(admin.ModelAdmin):
    list_display = (
        'recipe', 'ingredients', 'value'
    )
