"""
Tests for the user API
"""

from core.tests.helpers.fake_user import FakeUser
from core.tests.helpers.faker import faker
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse('users:create')
TOKEN_URL = reverse('users:token')
ME_URL = reverse('users:me')


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        self.client = APIClient()

        self.fake_user = FakeUser()

    def test_create_user_success(self):
        """Test creting a user in successful."""
        res = self.client.post(CREATE_USER_URL, self.fake_user.as_dict())

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=self.fake_user.email)
        self.assertTrue(user.check_password(self.fake_user.password))

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        create_user(**self.fake_user.as_dict())
        res = self.client.post(CREATE_USER_URL, self.fake_user.as_dict())

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 5 chars."""
        fake_user = FakeUser(
                pass_parms={
                    'length': 2,
                    'special_chars': False,
                    'upper_case': False
                }
            )

        res = self.client.post(CREATE_USER_URL, fake_user.as_dict())

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=fake_user.email
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""
        fake_user = FakeUser()
        create_user(**fake_user.as_dict())

        res = self.client.post(
            TOKEN_URL,
            fake_user.as_dict(name_needed=False)
        )

        self.assertIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid."""
        fake_user = FakeUser()
        create_user(**fake_user.as_dict(name_needed=False))

        fake_user.password = 'badpass'
        res = self.client.post(
            TOKEN_URL,
            fake_user.as_dict(name_needed=False)
        )

        self.assertNotIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_token_blank_password(self):
        """Test posting a blank password return an error"""
        self.fake_user.password = ''
        res = self.client.post(
            TOKEN_URL,
            self.fake_user.as_dict(name_needed=False)
        )

        self.assertNotIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_anauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requesta that require authentication"""

    def setUp(self):
        self.fake_user = create_user(**FakeUser().as_dict())
        self.client = APIClient()
        self.client.force_authenticate(user=self.fake_user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged user."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.fake_user.name,
            'email': self.fake_user.email,
        })

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user(self):
        """Test updating the user profile for the authenticated user."""
        updated_user = {
            'name': faker.first_name(),
            'password': faker.password(),
        }
        res = self.client.patch(ME_URL, updated_user)

        self.fake_user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.fake_user.name, updated_user.get('name'))
        self.assertTrue(self.fake_user.check_password(
                updated_user.get('password')
            )
        )
