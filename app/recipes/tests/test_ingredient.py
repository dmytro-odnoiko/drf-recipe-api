from decimal import Decimal
from random import randint

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from recipes.models import Ingredient, IngredientRecipe
from recipes.serializers import IngredientSerializer, \
    IngredientRecipeSerializer
from user.tests.test_user_api import create_user
from recipes.tests.test_recipe import create_recipe

from core.tests.helpers.faker import faker
from core.tests.helpers.fake_user import FakeUser


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
        recipe = create_recipe(user=user)
        ingredient_recipe = IngredientRecipe.objects.create(
            ingredient=ingredient,
            recipe=recipe,
            measure=Decimal(randint(5, 999999)),
            measure_type=faker.word()
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

    def test_create_recipe_with_new_recipe(self):
        """Test creating a recipe with new ingredients."""
        new_recipe = create_recipe(
            user=self.fake_user,
            params={'ingredients': []}
        )
        res = self.client.post()