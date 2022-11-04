from modeltranslation.translator import TranslationOptions, register

from recipes.models import Ingredient, IngredientRecipe, Tag, Recipe


@register(Recipe)
class RecipeTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)


@register(Ingredient)
class IngredientTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(IngredientRecipe)
class IngredientRecipeTranslationOptions(TranslationOptions):
    fields = ('amount_type',)


@register(Tag)
class TagTranslationOptions(TranslationOptions):
    fields = ('name',)
