from core.tests.helpers.fake_user import FakeUser
from core.tests.helpers.faker import faker

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from users.models import Profile

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


class PrivateUserApiTests(TestCase):
    """Test API requesta that require authentication"""

    def setUp(self):
        self.fake_user = get_user_model().objects.create_user(
            **FakeUser().as_dict()
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.fake_user)
        profile = Profile.objects.get(user_id=self.fake_user.id)
        self.profile_url = reverse(
            'user:profile',
            kwargs={'pk': profile.id}
        )

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged user."""
        res = self.client.get(self.profile_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'bio': '',
            'image': None,
            'short_desc': '',
        })

    def test_post_profile_not_allowed(self):
        """Test POST is not allowed for the profile endpoint"""
        res = self.client.post(self.profile_url, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_profile(self):
        """Test updating the user profile for the authenticated user."""
        updated_user = {
            'bio': faker.paragraph(nb_sentences=5),
            'short_desc': faker.sentence(nb_words=10),
        }
        res = self.client.patch(self.profile_url, updated_user)

        user_profile = Profile.objects.get(pk=self.fake_user.id)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(user_profile.bio, updated_user.get('bio'))
        self.assertEqual(
            user_profile.short_desc,
            updated_user.get('short_desc')
        )
