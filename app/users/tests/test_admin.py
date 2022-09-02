"""
Test for Django admin modifications.
"""

from core.tests.helpers.fake_user import FakeUser
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class UserAdminSiteTests(TestCase):
    """Tests for User on Django admin."""

    def setUp(self):
        """Create user and client."""
        self.client = Client()
        fake_client = FakeUser()
        self.admin_user = get_user_model().objects.create_superuser(
            **fake_client.as_dict(name_needed=False)
        )
        self.client.force_login(self.admin_user)
        fake_user = FakeUser()
        self.user = get_user_model().objects.create_user(
            **fake_user.as_dict()
        )

    def test_users_list(self):
        """Test that users are listed on page."""
        url = reverse('admin:users_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test the edit page works."""
        url = reverse('admin:users_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test the create user page works."""
        url = reverse('admin:users_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)


class ProfileAdminSiteTest(TestCase):
    """Tests for Profile on Django admin."""

    def setUp(self):
        """Create user and client."""
        self.client = Client()
        fake_client = FakeUser()
        self.admin_user = get_user_model().objects.create_superuser(
            **fake_client.as_dict(name_needed=False)
        )
        self.client.force_login(self.admin_user)
        fake_user = FakeUser()
        self.user = get_user_model().objects.create_user(
            **fake_user.as_dict()
        )

    def test_profile_list(self):
        """Test that profiles are listed on page."""
        url = reverse('admin:users_profile_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.id)

    def test_edit_user_page(self):
        """Test the edit profile works."""
        url = reverse('admin:users_profile_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
