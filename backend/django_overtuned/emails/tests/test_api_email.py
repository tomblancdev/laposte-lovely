# ruff: noqa: F841
"""
Test suite for Email API endpoints.

This module contains tests for the EmailViewSet which provides
list, retrieve, and thread endpoints for emails.
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


class TestEmailViewSet:
    """Test suite for EmailViewSet."""

    def test_list_emails_authenticated(self, api_client_authenticated, user):
        """Test listing emails as authenticated user."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        email1 = EmailFactory(folder=folder, subject="Test Email 1")
        email2 = EmailFactory(folder=folder, subject="Test Email 2")

        # Create email for another user (should not be included)
        other_user = UserFactory()
        other_account = EmailAccountFactory(user=other_user)
        other_folder = EmailFolderFactory(account=other_account)
        EmailFactory(folder=other_folder, subject="Other Email")

        url = reverse("api:email-list")
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 2  # noqa: PLR2004
        subjects = [email["subject"] for email in response.data]
        assert "Test Email 1" in subjects
        assert "Test Email 2" in subjects
        assert "Other Email" not in subjects

    def test_list_emails_unauthenticated(self):
        """Test that unauthenticated users cannot list emails."""
        client = APIClient()
        url = reverse("api:email-list")
        response = client.get(url)

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_retrieve_email_authenticated(self, api_client_authenticated, user):
        """Test retrieving a specific email."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)
        email = EmailFactory(
            folder=folder,
            subject="Test Subject",
            body_text="Test body text",
            body_html="<p>Test body html</p>",
        )

        url = reverse("api:email-detail", kwargs={"message_id": email.message_id})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.data["message_id"] == email.message_id
        assert response.data["subject"] == "Test Subject"
        assert response.data["body_text"] == "Test body text"
        assert response.data["body_html"] == "<p>Test body html</p>"
        # Detail view includes full content
        assert "from_address" in response.data
        assert "to_addresses" in response.data

    def test_retrieve_other_user_email_forbidden(
        self,
        api_client_authenticated,
        user,
    ):
        """Test that users cannot retrieve other users' emails."""
        other_user = UserFactory()
        other_account = EmailAccountFactory(user=other_user)
        other_folder = EmailFolderFactory(account=other_account)
        other_email = EmailFactory(folder=other_folder)

        url = reverse("api:email-detail", kwargs={"message_id": other_email.message_id})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_filter_by_folder(self, api_client_authenticated, user):
        """Test filtering emails by folder."""
        account = EmailAccountFactory(user=user)
        folder1 = EmailFolderFactory(account=account, base_name="Inbox")
        folder2 = EmailFolderFactory(account=account, base_name="Sent")

        email1 = EmailFactory(folder=folder1, subject="Inbox Email")
        email2 = EmailFactory(folder=folder2, subject="Sent Email")

        url = reverse("api:email-list")
        response = api_client_authenticated.get(url, {"folder": folder1.id})

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert response.data[0]["subject"] == "Inbox Email"

    def test_filter_by_read_status(self, api_client_authenticated, user):
        """Test filtering emails by read status."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        email1 = EmailFactory(folder=folder, is_read=True, subject="Read Email")
        email2 = EmailFactory(folder=folder, is_read=False, subject="Unread Email")

        url = reverse("api:email-list")

        # Filter for unread emails
        response = api_client_authenticated.get(url, {"is_read": "false"})
        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert response.data[0]["subject"] == "Unread Email"

        # Filter for read emails
        response = api_client_authenticated.get(url, {"is_read": "true"})
        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert response.data[0]["subject"] == "Read Email"

    def test_filter_by_from_address(self, api_client_authenticated, user):
        """Test filtering emails by sender address."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        addr1 = EmailAddressesFactory(address="sender1@example.com")
        addr2 = EmailAddressesFactory(address="sender2@example.com")

        email1 = EmailFactory(folder=folder, from_address=addr1, subject="Email 1")
        email2 = EmailFactory(folder=folder, from_address=addr2, subject="Email 2")

        url = reverse("api:email-list")
        response = api_client_authenticated.get(url, {"from_address": addr1.id})

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert response.data[0]["subject"] == "Email 1"

    def test_search_in_subject(self, api_client_authenticated, user):
        """Test searching emails in subject field."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        email1 = EmailFactory(folder=folder, subject="Meeting tomorrow")
        email2 = EmailFactory(folder=folder, subject="Report deadline")
        email3 = EmailFactory(folder=folder, subject="Meeting next week")

        url = reverse("api:email-list")
        response = api_client_authenticated.get(url, {"search": "meeting"})

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 2  # noqa: PLR2004
        subjects = [email["subject"] for email in response.data]
        assert "Meeting tomorrow" in subjects
        assert "Meeting next week" in subjects
        assert "Report deadline" not in subjects

    def test_search_in_body_text(self, api_client_authenticated, user):
        """Test searching emails in body text."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        email1 = EmailFactory(
            folder=folder,
            subject="Email 1",
            body_text="This contains important information",
        )
        email2 = EmailFactory(
            folder=folder,
            subject="Email 2",
            body_text="Regular content here",
        )

        url = reverse("api:email-list")
        response = api_client_authenticated.get(url, {"search": "important"})

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert response.data[0]["subject"] == "Email 1"

    def test_search_case_insensitive(self, api_client_authenticated, user):
        """Test that search is case-insensitive."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)
        email = EmailFactory(folder=folder, subject="Meeting Tomorrow")

        url = reverse("api:email-list")
        response = api_client_authenticated.get(url, {"search": "MEETING"})

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert response.data[0]["subject"] == "Meeting Tomorrow"

    def test_ordering_by_date_received(self, api_client_authenticated, user):
        """Test ordering emails by date_received."""
        from datetime import timedelta

        from django.utils import timezone

        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        now = timezone.now()
        email1 = EmailFactory(
            folder=folder,
            subject="Oldest",
            date_received=now - timedelta(days=2),
        )
        email2 = EmailFactory(
            folder=folder,
            subject="Newest",
            date_received=now,
        )
        email3 = EmailFactory(
            folder=folder,
            subject="Middle",
            date_received=now - timedelta(days=1),
        )

        url = reverse("api:email-list")

        # Descending order (newest first) - default
        response = api_client_authenticated.get(url, {"ordering": "-date_received"})
        assert response.status_code == HTTPStatus.OK
        subjects = [email["subject"] for email in response.data]
        assert subjects == ["Newest", "Middle", "Oldest"]

        # Ascending order (oldest first)
        response = api_client_authenticated.get(url, {"ordering": "date_received"})
        assert response.status_code == HTTPStatus.OK
        subjects = [email["subject"] for email in response.data]
        assert subjects == ["Oldest", "Middle", "Newest"]

    def test_ordering_by_subject(self, api_client_authenticated, user):
        """Test ordering emails by subject."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        EmailFactory(folder=folder, subject="Charlie")
        EmailFactory(folder=folder, subject="Alice")
        EmailFactory(folder=folder, subject="Bob")

        url = reverse("api:email-list")
        response = api_client_authenticated.get(url, {"ordering": "subject"})

        assert response.status_code == HTTPStatus.OK
        subjects = [email["subject"] for email in response.data]
        assert subjects == ["Alice", "Bob", "Charlie"]

    def test_default_ordering(self, api_client_authenticated, user):
        """Test that emails are ordered by date_received descending by default."""
        from datetime import timedelta

        from django.utils import timezone

        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        now = timezone.now()
        email1 = EmailFactory(
            folder=folder,
            subject="Old",
            date_received=now - timedelta(days=1),
        )
        email2 = EmailFactory(folder=folder, subject="New", date_received=now)

        url = reverse("api:email-list")
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        # Newest first by default
        assert response.data[0]["subject"] == "New"
        assert response.data[1]["subject"] == "Old"

    def test_pagination_with_limit_and_offset(self, api_client_authenticated, user):
        """Test pagination using limit and offset parameters."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        # Create 5 emails
        for i in range(5):
            EmailFactory(folder=folder, subject=f"Email {i}")

        url = reverse("api:email-list")

        # Get first 2 emails
        response = api_client_authenticated.get(url, {"limit": "2", "offset": "0"})
        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 2  # noqa: PLR2004

        # Get next 2 emails
        response = api_client_authenticated.get(url, {"limit": "2", "offset": "2"})
        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 2  # noqa: PLR2004

    def test_list_returns_list_serializer(self, api_client_authenticated, user):
        """Test that list view returns list serializer without body content."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)
        email = EmailFactory(
            folder=folder,
            body_text="Body text",
            body_html="<p>Body HTML</p>",
        )

        url = reverse("api:email-list")
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        # List view should not include body content
        assert "body_text" not in response.data[0]
        assert "body_html" not in response.data[0]

    def test_thread_action(self, api_client_authenticated, user):
        """Test the thread action returns email with thread context."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        original = EmailFactory(folder=folder, subject="Original Email")
        reply1 = EmailFactory(folder=folder, in_reply_to=original, subject="Reply 1")
        reply2 = EmailFactory(folder=folder, in_reply_to=original, subject="Reply 2")

        url = reverse("api:email-thread", kwargs={"message_id": original.message_id})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.data["message_id"] == original.message_id
        assert response.data["replies_count"] == 2  # noqa: PLR2004
        assert response.data["has_replies"] is True

    def test_thread_action_no_replies(self, api_client_authenticated, user):
        """Test thread action for email with no replies."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)
        email = EmailFactory(folder=folder)

        url = reverse("api:email-thread", kwargs={"message_id": email.message_id})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.data["replies_count"] == 0
        assert response.data["has_replies"] is False

    def test_email_with_multiple_to_addresses(self, api_client_authenticated, user):
        """Test retrieving email with multiple recipients."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        addr1 = EmailAddressesFactory(address="recipient1@example.com")
        addr2 = EmailAddressesFactory(address="recipient2@example.com")

        email = EmailFactory(folder=folder)
        email.to_addresses.clear()  # Clear default address added by factory
        email.to_addresses.add(addr1, addr2)

        url = reverse("api:email-detail", kwargs={"message_id": email.message_id})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert len(response.data["to_addresses"]) == 2  # noqa: PLR2004
        to_addresses = [addr["address"] for addr in response.data["to_addresses"]]
        assert "recipient1@example.com" in to_addresses
        assert "recipient2@example.com" in to_addresses

    def test_email_with_reply_to_address(self, api_client_authenticated, user):
        """Test retrieving email with reply-to address."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        reply_to = EmailAddressesFactory(address="replyto@example.com")
        email = EmailFactory(folder=folder, reply_to_address=reply_to)

        url = reverse("api:email-detail", kwargs={"message_id": email.message_id})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.data["reply_to_address"]["address"] == "replyto@example.com"

    def test_empty_email_list(self, api_client_authenticated):
        """Test listing emails when user has no emails."""
        url = reverse("api:email-list")
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 0

    def test_retrieve_nonexistent_email(self, api_client_authenticated):
        """Test retrieving a non-existent email returns 404."""
        url = reverse("api:email-detail", kwargs={"message_id": "nonexistent-id"})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_read_only_viewset(self, api_client_authenticated, user):
        """Test that the viewset is read-only (no create, update, delete)."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)
        email = EmailFactory(folder=folder)

        # Test POST (create)
        url = reverse("api:email-list")
        response = api_client_authenticated.post(url, {"subject": "New Email"})
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

        # Test PUT (update)
        url = reverse("api:email-detail", kwargs={"message_id": email.message_id})
        response = api_client_authenticated.put(url, {"subject": "Updated"})
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

        # Test PATCH (partial update)
        response = api_client_authenticated.patch(url, {"subject": "Updated"})
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

        # Test DELETE
        response = api_client_authenticated.delete(url)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_combined_filters(self, api_client_authenticated, user):
        """Test combining multiple filters."""
        account = EmailAccountFactory(user=user)
        folder1 = EmailFolderFactory(account=account, base_name="Inbox")
        folder2 = EmailFolderFactory(account=account, base_name="Sent")

        email1 = EmailFactory(
            folder=folder1,
            is_read=False,
            subject="Unread Inbox Email",
        )
        email2 = EmailFactory(
            folder=folder1,
            is_read=True,
            subject="Read Inbox Email",
        )
        email3 = EmailFactory(
            folder=folder2,
            is_read=False,
            subject="Unread Sent Email",
        )

        url = reverse("api:email-list")
        response = api_client_authenticated.get(
            url,
            {"folder": folder1.id, "is_read": "false", "search": "inbox"},
        )

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert response.data[0]["subject"] == "Unread Inbox Email"
