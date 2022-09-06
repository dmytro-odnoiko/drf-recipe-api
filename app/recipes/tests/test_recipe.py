from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from recipes.models import Recipe, Tag
from recipes.serializers import RecipeSerializer, RecipeDetailSerializer

from user.tests.test_user_api import create_user

from core.tests.helpers.faker import faker
from core.tests.helpers.fake_user import FakeUser
from recipes.tests.helpers.fake_recipe import FakeRecipe


RECIPES_URL = reverse('recipes:recipe-list')


def create_recipe(user, **params):
    """Create and return a sample recipe"""
    recipe = FakeRecipe().__dict__
    recipe.update({'user': user})
    recipe.update(**params)
    recipe = Recipe.objects.create(
        **recipe
    )
    return recipe


class RecipeModelTests(TestCase):
    """Tests for recipe model."""
    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        user = get_user_model().objects.create_user(**FakeUser().as_dict())
        recipe = FakeRecipe().__dict__
        recipe.update({'user': user})
        recipe = Recipe.objects.create(
            **recipe
        )
        self.assertEqual(str(recipe), recipe.title)


class PublicRecipeAPITests(TestCase):
    """Tests unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.fake_user = get_user_model().objects.create_user(
            **FakeUser().as_dict()
        )
        self.client.force_authenticate(self.fake_user)

    def test_retrive_recipes(self):
        """Test retrieving a list of recipes."""
        create_recipe(user=self.fake_user)
        create_recipe(user=self.fake_user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        fake_user = get_user_model().objects.create_user(
            **FakeUser().as_dict()
        )
        create_recipe(user=fake_user)
        create_recipe(user=self.fake_user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.fake_user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        recipe = create_recipe(user=self.fake_user)
        res = self.client.get(
            reverse('recipes:recipe-detail', args=[recipe.id])
        )
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe."""
        new_recipe = FakeRecipe().__dict__
        res = self.client.post(RECIPES_URL, new_recipe)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data.get('id'))
        for key, value in new_recipe.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.fake_user)

    def test_partical_update(self):
        """Test partical update of a recipe."""
        recipe = create_recipe(self.fake_user)

        recipe_new_title = {'title': faker.sentence()}
        res = self.client.patch(
            reverse('recipes:recipe-detail', args=[recipe.id]),
            recipe_new_title,
        )
        recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, recipe_new_title.get('title'))
        self.assertEqual(recipe.user, self.fake_user)

    def test_full_update(self):
        """Test full update of a recipe."""
        recipe = create_recipe(self.fake_user)

        recipe_update = FakeRecipe().__dict__
        res = self.client.put(
            reverse('recipes:recipe-detail', args=[recipe.id]),
            recipe_update,
        )
        recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for key, value in recipe_update.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.fake_user)

    def test_error_update(self):
        """Test changing recipe user result in an error."""
        new_user = create_user(**FakeUser().as_dict())
        recipe = create_recipe(user=self.fake_user)

        recipe_change_user = {'user': new_user.id}
        self.client.patch(
            reverse('recipes:recipe-detail', args=[recipe.id]),
            recipe_change_user,
        )
        recipe.refresh_from_db()

        self.assertEqual(recipe.user, self.fake_user)

    def test_delete_recipe(self):
        """Test deleting a recipe successful."""
        recipe = create_recipe(user=self.fake_user)

        res = self.client.delete(
            reverse('recipes:recipe-detail', args=[recipe.id]),
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_users_recipe_error(self):
        """Test trying to delete other users recipe gives error."""
        new_user = create_user(**FakeUser().as_dict())
        recipe = create_recipe(user=new_user)

        res = self.client.delete(
            reverse('recipes:recipe-detail', args=[recipe.id]),
        )

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_tags(self):
        """Test creating recie with new tags."""
        new_recipe = FakeRecipe().__dict__
        new_recipe.update(
            {'tags': [{'name': faker.word()} for i in range(2)]}
        )

        res = self.client.post(RECIPES_URL, new_recipe, format='json')

        recipes = Recipe.objects.filter(user=self.fake_user)
        recipe = recipes[0]
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(recipes.count(), 1)
        self.assertEqual(recipe.tags.count(), 2)
        for tag in new_recipe.get('tags'):
            self.assertTrue(
                recipe.tags.filter(name=tag.get('name'), user=self.fake_user).
                exists()
            )

    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tag."""
        new_tag = Tag.objects.create(user=self.fake_user, name=faker.word())
        new_recipe = FakeRecipe().__dict__
        new_recipe.update(
            {'tags': [{'name': new_tag.name}, {'name': faker.word()}]}
        )
        res = self.client.post(RECIPES_URL, new_recipe, format='json')

        recipes = Recipe.objects.filter(user=self.fake_user)
        recipe = recipes[0]
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(recipes.count(), 1)
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(new_tag, recipe.tags.all())
        for tag in new_recipe.get('tags'):
            self.assertTrue(
                recipe.tags.filter(name=tag.get('name'), user=self.fake_user).
                exists()
            )

    def test_create_tag_on_update(self):
        """Test creating tag when updating a recipe."""
        recipe = create_recipe(user=self.fake_user)

        new_tag = {'tags': [{'name': faker.word()}]}

        res = self.client.patch(
            reverse('recipes:recipe-detail', args=[recipe.id]),
            new_tag,
            format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag = Tag.objects.get(user=self.fake_user)
        self.assertIn(tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe."""
        recipe = create_recipe(user=self.fake_user)
        new_tag = Tag.objects.create(user=self.fake_user, name=faker.word())
        recipe.tags.add(new_tag)

        additional_tag = Tag.objects.create(
            user=self.fake_user,
            name=faker.word()
        )
        res = self.client.patch(
            reverse('recipes:recipe-detail', args=[recipe.id]),
            {'tags': [{'name': additional_tag.name}]},
            format='json',
        )

        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(additional_tag, recipe.tags.all())
        self.assertNotIn(new_tag, recipe.tags.all())

    def test_clear_recipe_tag(self):
        """Test clearing a recipe tags."""
        recipe = create_recipe(user=self.fake_user)
        new_tag = Tag.objects.create(user=self.fake_user, name=faker.word())
        recipe.tags.add(new_tag)

        res = self.client.patch(
            reverse('recipes:recipe-detail', args=[recipe.id]),
            {'tags': []},
            format='json',
        )

        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)
