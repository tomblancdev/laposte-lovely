# ruff: noqa: F841
"""
Test suite for EmailAccount API endpoints.

This module contains tests for the EmailAccountViewSet which provides
list and retrieve endpoints for email accounts.
"""

from http import HTTPStatus

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from django_overtuned.emails.tests.factories import EmailAccountFactory
from django_overtuned.emails.tests.factories import EmailFolderFactory
from django_overtuned.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestEmailAccountViewSet:
    """Test suite for EmailAccountViewSet."""

    def test_list_accounts_authenticated(self, api_client_authenticated, user):
        """Test listing email accounts as authenticated user."""
        # Create account for the authenticated user
        account = EmailAccountFactory(user=user, name="Work Gmail")

        # Create account for another user (should not be included)
        other_user = UserFactory()
        EmailAccountFactory(user=other_user, name="Other Account")

        url = reverse("api:emailaccount-list")
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Work Gmail"

    def test_list_accounts_unauthenticated(self):
        """Test that unauthenticated users cannot list accounts."""
        client = APIClient()
        url = reverse("api:emailaccount-list")
        response = client.get(url)

        # DRF returns 403 Forbidden when IsAuthenticated permission fails
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_retrieve_account_authenticated(self, api_client_authenticated, user):
        """Test retrieving a specific email account."""
        account = EmailAccountFactory(user=user, name="Test Account")

        url = reverse("api:emailaccount-detail", kwargs={"pk": account.pk})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.data["id"] == account.id
        assert response.data["name"] == "Test Account"
        assert response.data["user"] == user.id
        # Detail view includes statistics
        assert "folder_count" in response.data
        assert "email_count" in response.data

    def test_retrieve_account_with_statistics(self, api_client_authenticated, user):
        """Test that retrieve includes folder and email counts."""
        from django_overtuned.emails.tests.factories import EmailFactory

        account = EmailAccountFactory(user=user)
        folder1 = EmailFolderFactory(account=account, base_name="Inbox")
        folder2 = EmailFolderFactory(account=account, base_name="Sent")

        # Create emails in folders
        EmailFactory(folder=folder1)
        EmailFactory(folder=folder1)
        EmailFactory(folder=folder2)

        url = reverse("api:emailaccount-detail", kwargs={"pk": account.pk})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.data["folder_count"] == 2  # noqa: PLR2004
        assert response.data["email_count"] == 3  # noqa: PLR2004

    def test_retrieve_other_user_account_forbidden(
        self,
        api_client_authenticated,
        user,
    ):
        """Test that users cannot retrieve other users' accounts."""
        other_user = UserFactory()
        other_account = EmailAccountFactory(user=other_user)

        url = reverse("api:emailaccount-detail", kwargs={"pk": other_account.pk})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_search_accounts_by_name(self, api_client_authenticated, user):
        """Test filtering accounts by name using search parameter."""
        EmailAccountFactory(user=user, name="Work Gmail")

        # Create another user with an account that shouldn't match
        other_user = UserFactory()
        EmailAccountFactory(user=other_user, name="Personal Outlook")

        url = reverse("api:emailaccount-list")
        response = api_client_authenticated.get(url, {"search": "work"})

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Work Gmail"

    def test_search_accounts_case_insensitive(self, api_client_authenticated, user):
        """Test that search is case-insensitive."""
        EmailAccountFactory(user=user, name="Work Gmail")

        url = reverse("api:emailaccount-list")
        response = api_client_authenticated.get(url, {"search": "WORK"})

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Work Gmail"

    def test_list_returns_basic_serializer(self, api_client_authenticated, user):
        """Test that list view returns basic serializer without statistics."""
        account = EmailAccountFactory(user=user)

        url = reverse("api:emailaccount-list")
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        # List view should not include statistics
        assert "folder_count" not in response.data[0]
        assert "email_count" not in response.data[0]

    def test_user_field_is_read_only(self, api_client_authenticated, user):
        """Test that user field is read-only (implicitly tested)."""
        account = EmailAccountFactory(user=user)

        url = reverse("api:emailaccount-detail", kwargs={"pk": account.pk})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        # User should be set to the account's user, not the authenticated user
        assert response.data["user"] == account.user.id

    def test_empty_account_list(self, api_client_authenticated):
        """Test listing accounts when user has no accounts."""
        url = reverse("api:emailaccount-list")
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 0

    def test_account_with_no_folders(self, api_client_authenticated, user):
        """Test retrieving account with no folders shows zero counts."""
        account = EmailAccountFactory(user=user)

        url = reverse("api:emailaccount-detail", kwargs={"pk": account.pk})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.data["folder_count"] == 0
        assert response.data["email_count"] == 0

    def test_retrieve_nonexistent_account(self, api_client_authenticated):
        """Test retrieving a non-existent account returns 404."""
        url = reverse("api:emailaccount-detail", kwargs={"pk": 99999})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_read_only_viewset(self, api_client_authenticated, user):
        """Test that the viewset is read-only (no create, update, delete)."""
        account = EmailAccountFactory(user=user)

        # Test POST (create)
        url = reverse("api:emailaccount-list")
        response = api_client_authenticated.post(url, {"name": "New Account"})
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

        # Test PUT (update)
        url = reverse("api:emailaccount-detail", kwargs={"pk": account.pk})
        response = api_client_authenticated.put(url, {"name": "Updated"})
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

        # Test PATCH (partial update)
        response = api_client_authenticated.patch(url, {"name": "Updated"})
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

        # Test DELETE
        response = api_client_authenticated.delete(url)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
