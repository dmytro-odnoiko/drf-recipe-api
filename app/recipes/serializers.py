from rest_framework import serializers

from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""
    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe ingredients."""
    ingredient = IngredientSerializer(many=False, required=True)

    class Meta:
        model = IngredientRecipe
        fields = ['amount', 'amount_type', 'ingredient']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    tags = TagSerializer(many=True, required=False)
    ingredientrecipe_set = IngredientRecipeSerializer(
        many=True,
        required=False,
    )

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'time_minutes', 'price', 'link', 'image', 'tags',
            'ingredientrecipe_set',
        ]
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']

    def _get_or_create_tags(self, tags, recipe):
        """Handle creating or getting tags are needed."""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    def _get_or_create_recipe_ingredients(self, ingredients, recipe):
        """Handle creating or getting ingredients needed."""
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ing_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient.get('ingredient')
            )
            IngredientRecipe.objects.create(
                amount=ingredient.get('amount'),
                amount_type=ingredient.get('amount_type'),
                ingredient=ing_obj,
                recipe=recipe,
            )

    def create(self, validated_data):
        """Create a recipe."""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredientrecipe_set', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_recipe_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Update recipe."""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredientrecipe_set', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_recipe_ingredients(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
