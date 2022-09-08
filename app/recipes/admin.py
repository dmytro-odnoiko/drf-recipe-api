from django.contrib import admin
from recipes.models import Recipe, Tag


# Register your models here.
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass
