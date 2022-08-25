"""
Tests for models.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase

from core.tests.helpers.faker import faker
from core.tests.helpers.fake_user import FakeUser


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        fake_user = FakeUser()
        user = get_user_model().objects.create_user(
            **fake_user.as_dict(name_needed=False)
        )

        self.assertEqual(user.email, fake_user.email)
        self.assertTrue(user.check_password(fake_user.password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email,
                                                        faker.password()
                                                        )
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        fake_user = FakeUser()
        user = get_user_model().objects.create_superuser(
            **fake_user.as_dict(name_needed=False)
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
