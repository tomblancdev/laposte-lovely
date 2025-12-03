# ruff: noqa: F841
"""
Test suite for Email Personalization API endpoints.

This module contains tests for EmailPersonalizationViewSet and
EmailFolderPersonalizationViewSet which provide CRUD operations
for personalizing emails and folders.
"""

from http import HTTPStatus

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from django_overtuned.emails.tests.factories import EmailAccountFactory
from django_overtuned.emails.tests.factories import EmailFactory
from django_overtuned.emails.tests.factories import EmailFolderFactory
from django_overtuned.emails.tests.factories import EmailFolderPersonalizationFactory
from django_overtuned.emails.tests.factories import EmailPersonalizationFactory
from django_overtuned.user_tags.models import UserTag
from django_overtuned.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestEmailPersonalizationViewSet:
    """Test suite for EmailPersonalizationViewSet."""

    def test_list_personalizations_authenticated(self, api_client_authenticated, user):
        """Test listing email personalizations as authenticated user."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        email1 = EmailFactory(folder=folder, subject="Email 1")
        email2 = EmailFactory(folder=folder, subject="Email 2")

        pers1 = EmailPersonalizationFactory(email=email1, notes="Important")
        pers2 = EmailPersonalizationFactory(email=email2, notes="Follow up")

        # Create personalization for another user (should not be included)
        other_user = UserFactory()
        other_account = EmailAccountFactory(user=other_user)
        other_folder = EmailFolderFactory(account=other_account)
        other_email = EmailFactory(folder=other_folder)
        EmailPersonalizationFactory(email=other_email)

        url = reverse("api:emailpersonalization-list")
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 2  # noqa: PLR2004
        notes = [p["notes"] for p in response.data]
        assert "Important" in notes
        assert "Follow up" in notes

    def test_list_personalizations_unauthenticated(self):
        """Test that unauthenticated users cannot list personalizations."""
        client = APIClient()
        url = reverse("api:emailpersonalization-list")
        response = client.get(url)

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_create_personalization(self, api_client_authenticated, user):
        """Test creating a new email personalization."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)
        email = EmailFactory(folder=folder)

        url = reverse("api:emailpersonalization-list")
        data = {
            "email": email.pk,  # Use pk, not message_id
            "notes": "Important email",
            "importance_level": 5,
            "tags": ["urgent", "work"],
        }
        response = api_client_authenticated.post(url, data, format="json")

        assert response.status_code == HTTPStatus.CREATED
        assert response.data["email"] == email.pk
        assert response.data["notes"] == "Important email"
        assert response.data["importance_level"] == 5  # noqa: PLR2004
        assert set(response.data["tags"]) == {"urgent", "work"}

    def test_create_personalization_creates_user_tags(
        self,
        api_client_authenticated,
        user,
    ):
        """Test that creating personalization creates user-specific tags."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)
        email = EmailFactory(folder=folder)

        url = reverse("api:emailpersonalization-list")
        data = {
            "email": email.pk,  # Use pk, not message_id
            "tags": ["new-tag", "another-tag"],
        }
        response = api_client_authenticated.post(url, data, format="json")

        assert response.status_code == HTTPStatus.CREATED

        # Verify tags were created for this user
        user_tags = UserTag.objects.filter(user=user)
        tag_names = [tag.name for tag in user_tags]
        assert "new-tag" in tag_names
        assert "another-tag" in tag_names

    def test_retrieve_personalization(self, api_client_authenticated, user):
        """Test retrieving a specific personalization."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)
        email = EmailFactory(folder=folder)
        pers = EmailPersonalizationFactory(
            email=email,
            notes="Test notes",
            importance_level=3,
        )

        url = reverse("api:emailpersonalization-detail", kwargs={"pk": pers.pk})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.data["id"] == pers.id
        assert response.data["notes"] == "Test notes"
        assert response.data["importance_level"] == 3  # noqa: PLR2004

    def test_update_personalization(self, api_client_authenticated, user):
        """Test updating an email personalization."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)
        email = EmailFactory(folder=folder)
        pers = EmailPersonalizationFactory(
            email=email,
            notes="Original notes",
            importance_level=3,
        )

        url = reverse("api:emailpersonalization-detail", kwargs={"pk": pers.pk})
        data = {
            "email": email.pk,  # Use pk, not message_id
            "notes": "Updated notes",
            "importance_level": 5,
            "tags": ["updated"],
        }
        response = api_client_authenticated.put(url, data, format="json")

        assert response.status_code == HTTPStatus.OK
        assert response.data["notes"] == "Updated notes"
        assert response.data["importance_level"] == 5  # noqa: PLR2004
        assert response.data["tags"] == ["updated"]

    def test_partial_update_personalization(self, api_client_authenticated, user):
        """Test partially updating an email personalization."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)
        email = EmailFactory(folder=folder)
        pers = EmailPersonalizationFactory(
            email=email,
            notes="Original notes",
            importance_level=3,
        )

        url = reverse("api:emailpersonalization-detail", kwargs={"pk": pers.pk})
        data = {"notes": "Partially updated notes"}
        response = api_client_authenticated.patch(url, data, format="json")

        assert response.status_code == HTTPStatus.OK
        assert response.data["notes"] == "Partially updated notes"
        assert response.data["importance_level"] == 3  # noqa: PLR2004 - unchanged

    def test_delete_personalization(self, api_client_authenticated, user):
        """Test deleting an email personalization."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)
        email = EmailFactory(folder=folder)
        pers = EmailPersonalizationFactory(email=email)

        url = reverse("api:emailpersonalization-detail", kwargs={"pk": pers.pk})
        response = api_client_authenticated.delete(url)

        assert response.status_code == HTTPStatus.NO_CONTENT

    def test_filter_by_email(self, api_client_authenticated, user):
        """Test filtering personalizations by email."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        email1 = EmailFactory(folder=folder)
        email2 = EmailFactory(folder=folder)

        pers1 = EmailPersonalizationFactory(email=email1)
        pers2 = EmailPersonalizationFactory(email=email2)

        url = reverse("api:emailpersonalization-list")
        response = api_client_authenticated.get(url, {"email": email1.message_id})

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert response.data[0]["email"] == email1.message_id

    def test_filter_by_tags(self, api_client_authenticated, user):
        """Test filtering personalizations by tags."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        email1 = EmailFactory(folder=folder)
        email2 = EmailFactory(folder=folder)

        # Create personalizations with tags
        url = reverse("api:emailpersonalization-list")

        data1 = {"email": email1.pk, "tags": ["urgent", "work"]}
        api_client_authenticated.post(url, data1, format="json")

        data2 = {"email": email2.pk, "tags": ["personal"]}
        api_client_authenticated.post(url, data2, format="json")  # Filter by tag
        response = api_client_authenticated.get(url, {"tags": "urgent"})

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert "urgent" in response.data[0]["tags"]

    def test_filter_by_multiple_tags(self, api_client_authenticated, user):
        """Test filtering by multiple tags."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        email1 = EmailFactory(folder=folder)

        url = reverse("api:emailpersonalization-list")
        data = {"email": email1.pk, "tags": ["urgent", "work"]}
        api_client_authenticated.post(url, data, format="json")

        # Filter by multiple tags
        response = api_client_authenticated.get(url, {"tags": "urgent,work"})

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert "urgent" in response.data[0]["tags"]
        assert "work" in response.data[0]["tags"]

    def test_filter_by_has_notes(self, api_client_authenticated, user):
        """Test filtering personalizations by presence of notes."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        email1 = EmailFactory(folder=folder)
        email2 = EmailFactory(folder=folder)

        pers1 = EmailPersonalizationFactory(email=email1, notes="Has notes")
        pers2 = EmailPersonalizationFactory(email=email2, notes="")

        url = reverse("api:emailpersonalization-list")

        # Filter for entries with notes
        response = api_client_authenticated.get(url, {"has_notes": "true"})
        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert response.data[0]["notes"] == "Has notes"

        # Filter for entries without notes
        response = api_client_authenticated.get(url, {"has_notes": "false"})
        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert response.data[0]["notes"] == ""

    def test_filter_by_min_importance(self, api_client_authenticated, user):
        """Test filtering by minimum importance level."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        email1 = EmailFactory(folder=folder)
        email2 = EmailFactory(folder=folder)
        email3 = EmailFactory(folder=folder)

        pers1 = EmailPersonalizationFactory(email=email1, importance_level=5)
        pers2 = EmailPersonalizationFactory(email=email2, importance_level=3)
        pers3 = EmailPersonalizationFactory(email=email3, importance_level=1)

        url = reverse("api:emailpersonalization-list")
        response = api_client_authenticated.get(url, {"min_importance": "3"})

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 2  # noqa: PLR2004
        importance_levels = [p["importance_level"] for p in response.data]
        assert 5 in importance_levels  # noqa: PLR2004
        assert 3 in importance_levels  # noqa: PLR2004
        assert 1 not in importance_levels

    def test_retrieve_other_user_personalization_forbidden(
        self,
        api_client_authenticated,
        user,
    ):
        """Test that users cannot retrieve other users' personalizations."""
        other_user = UserFactory()
        other_account = EmailAccountFactory(user=other_user)
        other_folder = EmailFolderFactory(account=other_account)
        other_email = EmailFactory(folder=other_folder)
        other_pers = EmailPersonalizationFactory(email=other_email)

        url = reverse("api:emailpersonalization-detail", kwargs={"pk": other_pers.pk})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_empty_personalization_list(self, api_client_authenticated):
        """Test listing personalizations when user has none."""
        url = reverse("api:emailpersonalization-list")
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 0


class TestEmailFolderPersonalizationViewSet:
    """Test suite for EmailFolderPersonalizationViewSet."""

    def test_list_folder_personalizations_authenticated(
        self,
        api_client_authenticated,
        user,
    ):
        """Test listing folder personalizations as authenticated user."""
        account = EmailAccountFactory(user=user)

        folder1 = EmailFolderFactory(account=account, base_name="Inbox")
        folder2 = EmailFolderFactory(account=account, base_name="Sent")

        pers1 = EmailFolderPersonalizationFactory(
            folder=folder1,
            display_name="My Inbox",
        )
        pers2 = EmailFolderPersonalizationFactory(
            folder=folder2,
            display_name="My Sent",
        )

        # Create personalization for another user
        other_user = UserFactory()
        other_account = EmailAccountFactory(user=other_user)
        other_folder = EmailFolderFactory(account=other_account)
        EmailFolderPersonalizationFactory(folder=other_folder)

        url = reverse("api:emailfolderpersonalization-list")
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 2  # noqa: PLR2004
        display_names = [p["display_name"] for p in response.data]
        assert "My Inbox" in display_names
        assert "My Sent" in display_names

    def test_list_folder_personalizations_unauthenticated(self):
        """Test that unauthenticated users cannot list folder personalizations."""
        client = APIClient()
        url = reverse("api:emailfolderpersonalization-list")
        response = client.get(url)

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_create_folder_personalization(self, api_client_authenticated, user):
        """Test creating a new folder personalization."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account, base_name="Inbox")

        url = reverse("api:emailfolderpersonalization-list")
        data = {
            "folder": folder.id,
            "display_name": "Work Inbox",
            "display_color": "#3498db",
            "tags": ["work", "important"],
        }
        response = api_client_authenticated.post(url, data, format="json")

        assert response.status_code == HTTPStatus.CREATED
        assert response.data["folder"] == folder.id
        assert response.data["display_name"] == "Work Inbox"
        assert response.data["display_color"] == "#3498db"
        assert set(response.data["tags"]) == {"work", "important"}

    def test_create_folder_personalization_with_rgb_color(
        self,
        api_client_authenticated,
        user,
    ):
        """Test creating folder personalization with RGB-like color (as HEX)."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        url = reverse("api:emailfolderpersonalization-list")
        data = {
            "folder": folder.id,
            "display_color": "#3498db",  # Equivalent to rgb(52, 152, 219)
        }
        response = api_client_authenticated.post(url, data, format="json")

        assert response.status_code == HTTPStatus.CREATED
        assert response.data["display_color"] == "#3498db"

    def test_create_folder_personalization_with_named_color(
        self,
        api_client_authenticated,
        user,
    ):
        """Test creating folder personalization with named-like color (as HEX)."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        url = reverse("api:emailfolderpersonalization-list")
        data = {
            "folder": folder.id,
            "display_color": "#ff0000",  # Red
        }
        response = api_client_authenticated.post(url, data, format="json")

        assert response.status_code == HTTPStatus.CREATED
        assert response.data["display_color"] == "#ff0000"

    def test_retrieve_folder_personalization(self, api_client_authenticated, user):
        """Test retrieving a specific folder personalization."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)
        pers = EmailFolderPersonalizationFactory(
            folder=folder,
            display_name="Custom Name",
            display_color="#ff0000",
        )

        url = reverse("api:emailfolderpersonalization-detail", kwargs={"pk": pers.pk})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.data["id"] == pers.id
        assert response.data["display_name"] == "Custom Name"
        assert response.data["display_color"] == "#ff0000"

    def test_update_folder_personalization(self, api_client_authenticated, user):
        """Test updating a folder personalization."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)
        pers = EmailFolderPersonalizationFactory(
            folder=folder,
            display_name="Original",
            display_color="#000000",
        )

        url = reverse("api:emailfolderpersonalization-detail", kwargs={"pk": pers.pk})
        data = {
            "folder": folder.id,
            "display_name": "Updated",
            "display_color": "#ffffff",
            "tags": ["new-tag"],
        }
        response = api_client_authenticated.put(url, data, format="json")

        assert response.status_code == HTTPStatus.OK
        assert response.data["display_name"] == "Updated"
        assert response.data["display_color"] == "#ffffff"
        assert response.data["tags"] == ["new-tag"]

    def test_partial_update_folder_personalization(
        self,
        api_client_authenticated,
        user,
    ):
        """Test partially updating a folder personalization."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)
        pers = EmailFolderPersonalizationFactory(
            folder=folder,
            display_name="Original",
            display_color="#000000",
        )

        url = reverse("api:emailfolderpersonalization-detail", kwargs={"pk": pers.pk})
        data = {"display_color": "#ff00ff"}
        response = api_client_authenticated.patch(url, data, format="json")

        assert response.status_code == HTTPStatus.OK
        assert response.data["display_color"] == "#ff00ff"
        assert response.data["display_name"] == "Original"  # unchanged

    def test_delete_folder_personalization(self, api_client_authenticated, user):
        """Test deleting a folder personalization."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)
        pers = EmailFolderPersonalizationFactory(folder=folder)

        url = reverse("api:emailfolderpersonalization-detail", kwargs={"pk": pers.pk})
        response = api_client_authenticated.delete(url)

        assert response.status_code == HTTPStatus.NO_CONTENT

    def test_filter_by_folder(self, api_client_authenticated, user):
        """Test filtering folder personalizations by folder."""
        account = EmailAccountFactory(user=user)

        folder1 = EmailFolderFactory(account=account)
        folder2 = EmailFolderFactory(account=account)

        pers1 = EmailFolderPersonalizationFactory(folder=folder1)
        pers2 = EmailFolderPersonalizationFactory(folder=folder2)

        url = reverse("api:emailfolderpersonalization-list")
        response = api_client_authenticated.get(url, {"folder": folder1.id})

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert response.data[0]["folder"] == folder1.id

    def test_filter_by_tags(self, api_client_authenticated, user):
        """Test filtering folder personalizations by tags."""
        account = EmailAccountFactory(user=user)

        folder1 = EmailFolderFactory(account=account)
        folder2 = EmailFolderFactory(account=account)

        url = reverse("api:emailfolderpersonalization-list")

        resp1 = api_client_authenticated.post(
            url,
            {"folder": folder1.id, "tags": ["work", "important"]},
            format="json",
        )
        assert resp1.status_code == HTTPStatus.CREATED

        resp2 = api_client_authenticated.post(
            url,
            {"folder": folder2.id, "tags": ["personal"]},
            format="json",
        )
        assert resp2.status_code == HTTPStatus.CREATED

        # Filter by tag
        response = api_client_authenticated.get(url, {"tags": "work"})

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) >= 1
        # Check that at least one item has the work tag
        work_items = [item for item in response.data if "work" in item["tags"]]
        assert len(work_items) >= 1

    def test_filter_by_has_display_name(self, api_client_authenticated, user):
        """Test filtering by presence of custom display name."""
        account = EmailAccountFactory(user=user)

        folder1 = EmailFolderFactory(account=account)
        folder2 = EmailFolderFactory(account=account)

        pers1 = EmailFolderPersonalizationFactory(
            folder=folder1,
            display_name="Custom Name",
        )
        pers2 = EmailFolderPersonalizationFactory(folder=folder2, display_name="")

        url = reverse("api:emailfolderpersonalization-list")

        # Filter for entries with display name
        response = api_client_authenticated.get(url, {"has_display_name": "true"})
        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert response.data[0]["display_name"] == "Custom Name"

        # Filter for entries without display name
        response = api_client_authenticated.get(url, {"has_display_name": "false"})
        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert response.data[0]["display_name"] == ""

    def test_retrieve_other_user_folder_personalization_forbidden(
        self,
        api_client_authenticated,
        user,
    ):
        """Test that users cannot retrieve other users' folder personalizations."""
        other_user = UserFactory()
        other_account = EmailAccountFactory(user=other_user)
        other_folder = EmailFolderFactory(account=other_account)
        other_pers = EmailFolderPersonalizationFactory(folder=other_folder)

        url = reverse(
            "api:emailfolderpersonalization-detail",
            kwargs={"pk": other_pers.pk},
        )
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_empty_folder_personalization_list(self, api_client_authenticated):
        """Test listing folder personalizations when user has none."""
        url = reverse("api:emailfolderpersonalization-list")
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 0

    def test_color_validation(self, api_client_authenticated, user):
        """Test that invalid colors are rejected."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        url = reverse("api:emailfolderpersonalization-list")
        data = {
            "folder": folder.id,
            "display_color": "invalid-color",
        }
        response = api_client_authenticated.post(url, data, format="json")

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert "display_color" in response.data
