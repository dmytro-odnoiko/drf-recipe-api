from django.contrib import admin
from recipes.models import Recipe, Tag, Ingredient, IngredientRecipe


# Register your models here.
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


admin.site.register(Ingredient)
admin.site.register(IngredientRecipe)
