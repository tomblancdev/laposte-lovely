# ruff: noqa: F841
"""
Test suite for EmailAddresses API endpoints.

This module contains tests for the EmailAddressesViewSet which provides
list and retrieve endpoints for email addresses.
"""

from http import HTTPStatus

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from django_overtuned.emails.tests.factories import EmailAccountFactory
from django_overtuned.emails.tests.factories import EmailAddressesFactory
from django_overtuned.emails.tests.factories import EmailFactory
from django_overtuned.emails.tests.factories import EmailFolderFactory
from django_overtuned.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestEmailAddressesViewSet:
    """Test suite for EmailAddressesViewSet."""

    def test_list_addresses_authenticated(self, api_client_authenticated, user):
        """Test listing email addresses from user's emails."""
        # Create user's account and folder
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        # Create addresses that appear in user's emails
        addr1 = EmailAddressesFactory(address="sender@example.com")
        addr2 = EmailAddressesFactory(address="recipient@example.com")

        # Create emails with these addresses
        email1 = EmailFactory(folder=folder, from_address=addr1)
        email1.to_addresses.add(addr2)

        # Create address for another user (should not be included)
        other_user = UserFactory()
        other_account = EmailAccountFactory(user=other_user)
        other_folder = EmailFolderFactory(account=other_account)
        other_addr = EmailAddressesFactory(address="other@example.com")
        EmailFactory(folder=other_folder, from_address=other_addr)

        url = reverse("api:emailaddresses-list")
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        addresses = [addr["address"] for addr in response.data]
        assert "sender@example.com" in addresses
        assert "recipient@example.com" in addresses
        assert "other@example.com" not in addresses

    def test_list_addresses_unauthenticated(self):
        """Test that unauthenticated users cannot list addresses."""
        client = APIClient()
        url = reverse("api:emailaddresses-list")
        response = client.get(url)

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_retrieve_address_authenticated(self, api_client_authenticated, user):
        """Test retrieving a specific email address."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)
        addr = EmailAddressesFactory(address="test@example.com")
        EmailFactory(folder=folder, from_address=addr)

        url = reverse("api:emailaddresses-detail", kwargs={"pk": addr.pk})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.data["id"] == addr.id
        assert response.data["address"] == "test@example.com"
        # Detail view includes statistics
        assert "emails_sent_count" in response.data
        assert "emails_received_count" in response.data
        assert "emails_reply_to_count" in response.data

    def test_retrieve_address_with_statistics(self, api_client_authenticated, user):
        """Test that retrieve includes usage statistics."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)
        addr = EmailAddressesFactory(address="test@example.com")

        # Create emails with different relationships
        email1 = EmailFactory(folder=folder, from_address=addr)  # sent from
        email2 = EmailFactory(folder=folder)
        email2.to_addresses.add(addr)  # sent to
        email3 = EmailFactory(folder=folder, reply_to_address=addr)  # reply to

        url = reverse("api:emailaddresses-detail", kwargs={"pk": addr.pk})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.data["emails_sent_count"] == 1
        assert response.data["emails_received_count"] == 1
        assert response.data["emails_reply_to_count"] == 1

    def test_retrieve_other_user_address_forbidden(
        self,
        api_client_authenticated,
        user,
    ):
        """Test that users cannot retrieve addresses not in their emails."""
        other_user = UserFactory()
        other_account = EmailAccountFactory(user=other_user)
        other_folder = EmailFolderFactory(account=other_account)
        other_addr = EmailAddressesFactory(address="other@example.com")
        EmailFactory(folder=other_folder, from_address=other_addr)

        url = reverse("api:emailaddresses-detail", kwargs={"pk": other_addr.pk})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_search_addresses(self, api_client_authenticated, user):
        """Test filtering addresses by search parameter."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        addr1 = EmailAddressesFactory(address="john@example.com")
        addr2 = EmailAddressesFactory(address="jane@example.com")
        addr3 = EmailAddressesFactory(address="admin@company.com")

        # Create emails with these addresses (clear default to_addresses)
        email1 = EmailFactory(folder=folder, from_address=addr1)
        email1.to_addresses.clear()
        email2 = EmailFactory(folder=folder, from_address=addr2)
        email2.to_addresses.clear()
        email3 = EmailFactory(folder=folder, from_address=addr3)
        email3.to_addresses.clear()

        url = reverse("api:emailaddresses-list")
        response = api_client_authenticated.get(url, {"search": "example.com"})

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 2  # noqa: PLR2004
        addresses = [addr["address"] for addr in response.data]
        assert "john@example.com" in addresses
        assert "jane@example.com" in addresses
        assert "admin@company.com" not in addresses

    def test_search_addresses_case_insensitive(self, api_client_authenticated, user):
        """Test that search is case-insensitive."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)
        addr = EmailAddressesFactory(address="John@Example.COM")
        EmailFactory(folder=folder, from_address=addr)

        url = reverse("api:emailaddresses-list")
        response = api_client_authenticated.get(url, {"search": "john"})

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert response.data[0]["address"] == "John@Example.COM"

    def test_limit_results(self, api_client_authenticated, user):
        """Test limiting number of results with limit parameter."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        # Create multiple addresses
        for i in range(5):
            addr = EmailAddressesFactory(address=f"user{i}@example.com")
            EmailFactory(folder=folder, from_address=addr)

        url = reverse("api:emailaddresses-list")
        response = api_client_authenticated.get(url, {"limit": "3"})

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 3  # noqa: PLR2004

    def test_limit_with_invalid_value(self, api_client_authenticated, user):
        """Test that invalid limit parameter is ignored."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)
        addr = EmailAddressesFactory()
        EmailFactory(folder=folder, from_address=addr)

        url = reverse("api:emailaddresses-list")
        response = api_client_authenticated.get(url, {"limit": "invalid"})

        assert response.status_code == HTTPStatus.OK
        # Should return all results when limit is invalid
        assert len(response.data) >= 1

    def test_addresses_from_to_field(self, api_client_authenticated, user):
        """Test that addresses in to_addresses field are included."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        to_addr = EmailAddressesFactory(address="recipient@example.com")
        email = EmailFactory(folder=folder)
        email.to_addresses.add(to_addr)

        url = reverse("api:emailaddresses-list")
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        addresses = [addr["address"] for addr in response.data]
        assert "recipient@example.com" in addresses

    def test_addresses_from_reply_to_field(self, api_client_authenticated, user):
        """Test that addresses in reply_to field are included."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        reply_to_addr = EmailAddressesFactory(address="replyto@example.com")
        EmailFactory(folder=folder, reply_to_address=reply_to_addr)

        url = reverse("api:emailaddresses-list")
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        addresses = [addr["address"] for addr in response.data]
        assert "replyto@example.com" in addresses

    def test_list_returns_basic_serializer(self, api_client_authenticated, user):
        """Test that list view returns basic serializer without statistics."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)
        addr = EmailAddressesFactory()
        EmailFactory(folder=folder, from_address=addr)

        url = reverse("api:emailaddresses-list")
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) >= 1
        # List view should not include statistics
        assert "emails_sent_count" not in response.data[0]
        assert "emails_received_count" not in response.data[0]
        assert "emails_reply_to_count" not in response.data[0]

    def test_empty_address_list(self, api_client_authenticated):
        """Test listing addresses when user has no emails."""
        url = reverse("api:emailaddresses-list")
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 0

    def test_addresses_ordered_by_address(self, api_client_authenticated, user):
        """Test that addresses are ordered alphabetically."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        addr1 = EmailAddressesFactory(address="charlie@example.com")
        addr2 = EmailAddressesFactory(address="alice@example.com")
        addr3 = EmailAddressesFactory(address="bob@example.com")

        EmailFactory(folder=folder, from_address=addr1)
        EmailFactory(folder=folder, from_address=addr2)
        EmailFactory(folder=folder, from_address=addr3)

        url = reverse("api:emailaddresses-list")
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        addresses = [addr["address"] for addr in response.data]
        assert addresses == sorted(addresses)

    def test_retrieve_nonexistent_address(self, api_client_authenticated):
        """Test retrieving a non-existent address returns 404."""
        url = reverse("api:emailaddresses-detail", kwargs={"pk": 99999})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_read_only_viewset(self, api_client_authenticated, user):
        """Test that the viewset is read-only (no create, update, delete)."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)
        addr = EmailAddressesFactory()
        EmailFactory(folder=folder, from_address=addr)

        # Test POST (create)
        url = reverse("api:emailaddresses-list")
        response = api_client_authenticated.post(
            url,
            {"address": "new@example.com"},
        )
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

        # Test PUT (update)
        url = reverse("api:emailaddresses-detail", kwargs={"pk": addr.pk})
        response = api_client_authenticated.put(url, {"address": "updated@example.com"})
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

        # Test PATCH (partial update)
        response = api_client_authenticated.patch(
            url,
            {"address": "updated@example.com"},
        )
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

        # Test DELETE
        response = api_client_authenticated.delete(url)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_address_appears_in_multiple_emails(self, api_client_authenticated, user):
        """Test address statistics with multiple emails."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)
        addr = EmailAddressesFactory(address="common@example.com")

        # Create multiple emails with this address
        for _ in range(3):
            EmailFactory(folder=folder, from_address=addr)

        url = reverse("api:emailaddresses-detail", kwargs={"pk": addr.pk})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.data["emails_sent_count"] == 3  # noqa: PLR2004
