from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from recipes.models import Tag
from recipes.serializers import TagSerializer
from users.tests.test_user_api import create_user

from core.tests.helpers.faker import faker
from core.tests.helpers.fake_user import FakeUser


TAGS_URL = reverse('recipes:tag-list')


class TagModelTests(TestCase):
    """Tests for tag model."""

    def test_create_tag(self):
        """Test creating a tag is successful."""
        user = create_user(**FakeUser().as_dict())
        tag = Tag.objects.create(user=user, name=faker.word())

        self.assertEqual(str(tag), tag.name)


class PublicTagsAPITest(TestCase):
    """Test unathenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPITest(TestCase):
    """Test authenticated request for tag API."""

    def setUp(self):
        self.fake_user = create_user(**FakeUser().as_dict())
        self.client = APIClient()
        self.client.force_authenticate(self.fake_user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags."""
        Tag.objects.create(user=self.fake_user, name=faker.word())
        Tag.objects.create(user=self.fake_user, name=faker.word())

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of  tags is limited to authenticated user."""
        new_fake_user = create_user(**FakeUser().as_dict())
        Tag.objects.create(user=new_fake_user, name=faker.word())

        tag = Tag.objects.create(user=self.fake_user, name=faker.word())

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0].get('name'), tag.name)
        self.assertEqual(res.data[0].get('id'), tag.id)

    def test_update_tag(self):
        """Test updatinf a tag."""
        tag = Tag.objects.create(user=self.fake_user, name=faker.word())

        update_tag = {'name': faker.word()}
        res = self.client.patch(
            reverse('recipes:tag-detail', args=[tag.id]),
            update_tag
        )

        tag.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(tag.name, update_tag.get('name'))

    def test_delete_tag(self):
        """Test deleting a tag."""
        tag = Tag.objects.create(user=self.fake_user, name=faker.word())

        res = self.client.delete(
            reverse('recipes:tag-detail', args=[tag.id]),
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(user=self.fake_user).exists())
