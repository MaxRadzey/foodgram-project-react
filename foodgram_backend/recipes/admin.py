from django.contrib import admin

from recipes.models import Tags, Ingredients, Recipes, RecipesIngredientsValue


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'color', 'slug'
    )


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'unit'
    )


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
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


@admin.register(RecipesIngredientsValue)
class RecipesIngredientsValueAdmin(admin.ModelAdmin):
    list_display = (
        'recipes', 'ingredients', 'value'
    )
