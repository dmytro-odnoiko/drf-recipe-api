from random import randint

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from recipes.models import Ingredient, IngredientRecipe, Recipe
from recipes.serializers import IngredientSerializer, RecipeSerializer

from recipes.tests.test_recipe import create_recipe
from recipes.tests.helpers.fake_ingredient import FakeIngredient
from recipes.tests.helpers.fake_recipe import FakeRecipe
from recipes.tests.test_recipe import RECIPES_URL

from core.tests.helpers.fake_user import FakeUser
from core.tests.helpers.faker import faker
from users.tests.test_user_api import create_user

INGREDIENTS_URL = reverse('recipes:ingredient-list')


class IngredientModelTests(TestCase):
    """Test ingredient model."""
    def test_create_ingredient(self):
        """Test creating ingredient is successful."""
        user = create_user(**FakeUser().as_dict())
        ingredient = Ingredient.objects.create(
            user=user,
            name=faker.word()
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_create_recipe_ingredient(self):
        """Test creating creating recipe with ingredient weight."""
        user = create_user(**FakeUser().as_dict())
        ingredient = Ingredient.objects.create(
            user=user,
            name=faker.word()
        )
        recipe = Recipe.objects.create(
            **FakeRecipe(user=user).__dict__
        )
        ingredient_recipe = IngredientRecipe.objects.create(
            **FakeIngredient(
                fields={'ingredient': ingredient, 'recipe': recipe}
            ).__dict__
        )

        self.assertEqual(
            str(ingredient_recipe),
            ingredient_recipe.ingredient.name
        )


class PublicIngredientAPITests(TestCase):
    """Test unathenticated API requests."""

    def test_auth_required(self):
        """Test auth is required for retrieving ingredients."""
        client = APIClient()
        res = client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.fake_user = create_user(**FakeUser().as_dict())
        self.client = APIClient()
        self.client.force_authenticate(self.fake_user)

    def test_retrieve_indredients(self):
        """Test retrieving a list of ingredients."""
        Ingredient.objects.create(user=self.fake_user, name=faker.word())
        Ingredient.objects.create(user=self.fake_user, name=faker.word())

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        seriallizer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, seriallizer.data)

    def test_ingredient_limited_to_user(self):
        """Test list of ingredients is limited to auth users."""
        new_fake_user = create_user(**FakeUser().as_dict())
        Ingredient.objects.create(user=new_fake_user, name=faker.word())
        ingredient = Ingredient.objects.create(
            user=self.fake_user,
            name=faker.word()
        )

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0].get('name'), ingredient.name)
        self.assertEqual(res.data[0].get('id'), ingredient.id)

    def test_update_ingredient(self):
        """Test updating an ingredient."""
        ingredient = Ingredient.objects.create(
            user=self.fake_user,
            name=faker.word()
        )

        updated_ingredient = {'name': faker.word()}
        res = self.client.patch(
            reverse('recipes:ingredient-detail', args=[ingredient.id]),
            updated_ingredient,
        )

        ingredient.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredient.name, updated_ingredient.get('name'))

    def test_delete_ingredient(self):
        """Test deleting an ingredient."""
        ingredient = Ingredient.objects.create(
            user=self.fake_user,
            name=faker.word()
        )

        res = self.client.delete(
            reverse('recipes:ingredient-detail', args=[ingredient.id]),
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Ingredient.objects.filter(user=self.fake_user).exists()
        )

    def test_create_recipe_with_new_ingredients(self):
        """Test creating a recipe with new ingredients."""
        new_recipe = FakeRecipe(with_ingredients=True).__dict__
        res = self.client.post(RECIPES_URL, new_recipe, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.fake_user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]

        self.assertAlmostEqual(recipe.ingredients.count(), 2)
        for ingredient in new_recipe.get('ingredientrecipe_set'):
            ing_obj = Ingredient.objects.get(
                name=ingredient.get('ingredient').get('name'),
                user=self.fake_user
            )
            self.assertTrue(
                IngredientRecipe.objects.filter(
                    recipe=recipe,
                    ingredient=ing_obj,
                    amount=ingredient.get('amount'),
                    amount_type=ingredient.get('amount_type'),
                ).exists()
            )

    def test_create_recipe_with_existing_ingredient(self):
        """Test creating a recipe with existing ingredients."""
        ingredient = Ingredient.objects.create(
            user=self.fake_user,
            name=faker.word()
        )

        new_recipe = FakeRecipe(with_ingredients=True).__dict__
        new_recipe['ingredientrecipe_set'].append(
            {
                'ingredient': {'name': ingredient.name},
                'amount': randint(5, 150),
                'amount_type': faker.word(),
            }
        )
        res = self.client.post(RECIPES_URL, new_recipe, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.fake_user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertAlmostEqual(recipe.ingredients.count(), 3)

        for ingredient in new_recipe.get('ingredientrecipe_set'):
            ing_obj = Ingredient.objects.get(
                name=ingredient.get('ingredient').get('name'),
                user=self.fake_user
            )
            self.assertTrue(
                IngredientRecipe.objects.filter(
                    recipe=recipe,
                    ingredient=ing_obj,
                    amount=ingredient.get('amount'),
                    amount_type=ingredient.get('amount_type'),
                ).exists()
            )

    def test_create_ingredient_on_update(self):
        """Test creating an ingredient when updating recipe"""
        recipe = Recipe.objects.create(
            **FakeRecipe(user=self.fake_user).__dict__
        )

        new_ingredient = {
            'ingredientrecipe_set': [
                {
                    'ingredient': {'name': faker.word()},
                    'amount': randint(5, 150),
                    'amount_type': faker.word(),
                }
            ]
        }

        res = self.client.patch(
            reverse('recipes:recipe-detail', args=[recipe.id]),
            new_ingredient,
            format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ing_obj = Ingredient.objects.filter(
                name=new_ingredient.get('ingredientrecipe_set')[0].
                get('ingredient').get('name'),
                user=self.fake_user,
            ).first()
        ingredient_recipe = IngredientRecipe.objects.filter(
            recipe=recipe,
            ingredient=ing_obj,
            amount=new_ingredient.get('ingredientrecipe_set')[0].get('amount'),
            amount_type=new_ingredient.get('ingredientrecipe_set')[0].
            get('amount_type'),
        )
        self.assertTrue(ingredient_recipe.exists())

    def test_update_recipe_assign_ingredient(self):
        """Test assigning an exinsting ingredient when updating recipe"""
        ingredient = Ingredient.objects.create(
            user=self.fake_user,
            name=faker.word()
        )

        recipe = Recipe.objects.create(
            **FakeRecipe(user=self.fake_user).__dict__
        )
        IngredientRecipe.objects.create(
            **FakeIngredient(
                fields={'ingredient': ingredient, 'recipe': recipe},
            ).__dict__
        )

        new_ingredient = Ingredient.objects.create(
            user=self.fake_user,
            name=faker.word()
        )

        new_ingredient_recipe = {
            'ingredientrecipe_set': [
                {
                    'ingredient': {'name': new_ingredient.name},
                    'amount': randint(5, 150),
                    'amount_type': faker.word(),
                }
            ]
        }

        res = self.client.patch(
            reverse('recipes:recipe-detail', args=[recipe.id]),
            new_ingredient_recipe,
            format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(new_ingredient, recipe.ingredients.all())
        self.assertNotIn(ingredient, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """Test clearing a recipe ingredient."""
        ingredient = Ingredient.objects.create(
            user=self.fake_user,
            name=faker.word()
        )

        recipe = Recipe.objects.create(
            **FakeRecipe(user=self.fake_user).__dict__
        )
        IngredientRecipe.objects.create(
            **FakeIngredient(
                fields={'ingredient': ingredient, 'recipe': recipe}
            ).__dict__
        )

        update_ingredients = {'ingredientrecipe_set': []}
        res = self.client.patch(
            reverse('recipes:recipe-detail', args=[recipe.id]),
            update_ingredients,
            format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_filter_by_tags(self):
        """Test filtering recipes by ingredients."""
        r1 = create_recipe(user=self.fake_user)
        r2 = create_recipe(user=self.fake_user)
        in1 = Ingredient.objects.create(user=self.fake_user, name=faker.word())
        in2 = Ingredient.objects.create(user=self.fake_user, name=faker.word())
        IngredientRecipe.objects.create(
            **FakeIngredient(
                fields={'ingredient': in1, 'recipe': r1}
            ).__dict__
        )
        IngredientRecipe.objects.create(
            **FakeIngredient(
                fields={'ingredient': in2, 'recipe': r2}
            ).__dict__
        )
        r3 = create_recipe(user=self.fake_user)

        res = self.client.get(
            RECIPES_URL,
            {'ingredients': f'{in1.id},{in2.id}'},
        )

        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)

        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)
