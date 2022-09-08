from django.contrib import admin
from recipes.models import Recipe, Tag, Ingredient, IngredientRecipe

# Register your models here.
admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(IngredientRecipe)
