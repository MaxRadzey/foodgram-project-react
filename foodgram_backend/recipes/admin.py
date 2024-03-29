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


class RecipeIngredientValueAdmin(admin.TabularInline):
    model = RecipeIngredientValue


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author', 'name', 'image', 'text',
        'cooking_time', 'pub_date'
    )
    inlines = [RecipeIngredientValueAdmin]

    def display_tags(self, obj):
        return ', '.join(
            [tag.name for tag in obj.tags.all()]
        )
