# ruff: noqa: F841
"""
Test suite for EmailFolder API endpoints.

This module contains tests for the EmailFolderViewSet which provides
list, retrieve, tree, and subfolders endpoints for email folders.
"""

from http import HTTPStatus

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from django_overtuned.emails.tests.factories import EmailAccountFactory
from django_overtuned.emails.tests.factories import EmailFactory
from django_overtuned.emails.tests.factories import EmailFolderFactory
from django_overtuned.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestEmailFolderViewSet:
    """Test suite for EmailFolderViewSet."""

    def test_list_folders_authenticated(self, api_client_authenticated, user):
        """Test listing email folders as authenticated user."""
        account = EmailAccountFactory(user=user)
        folder1 = EmailFolderFactory(account=account, base_name="Inbox")
        folder2 = EmailFolderFactory(account=account, base_name="Sent")

        # Create folder for another user (should not be included)
        other_user = UserFactory()
        other_account = EmailAccountFactory(user=other_user)
        EmailFolderFactory(account=other_account, base_name="Other Inbox")

        url = reverse("api:emailfolder-list")
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 2  # noqa: PLR2004
        folder_names = [folder["base_name"] for folder in response.data]
        assert "Inbox" in folder_names
        assert "Sent" in folder_names
        assert "Other Inbox" not in folder_names

    def test_list_folders_unauthenticated(self):
        """Test that unauthenticated users cannot list folders."""
        client = APIClient()
        url = reverse("api:emailfolder-list")
        response = client.get(url)

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_retrieve_folder_authenticated(self, api_client_authenticated, user):
        """Test retrieving a specific folder."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account, base_name="Inbox")

        url = reverse("api:emailfolder-detail", kwargs={"pk": folder.pk})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.data["id"] == folder.id
        assert response.data["base_name"] == "Inbox"
        assert response.data["account"] == account.id
        # Detail view includes statistics
        assert "email_count" in response.data
        assert "unread_count" in response.data
        assert "subfolder_count" in response.data

    def test_retrieve_folder_with_statistics(self, api_client_authenticated, user):
        """Test that retrieve includes email and subfolder counts."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account, base_name="Inbox")

        # Create subfolders
        EmailFolderFactory(account=account, parent=folder, base_name="Projects")
        EmailFolderFactory(account=account, parent=folder, base_name="Archive")

        # Create emails
        EmailFactory(folder=folder, is_read=True)
        EmailFactory(folder=folder, is_read=False)
        EmailFactory(folder=folder, is_read=False)

        url = reverse("api:emailfolder-detail", kwargs={"pk": folder.pk})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.data["email_count"] == 3  # noqa: PLR2004
        assert response.data["unread_count"] == 2  # noqa: PLR2004
        assert response.data["subfolder_count"] == 2  # noqa: PLR2004

    def test_retrieve_other_user_folder_forbidden(
        self,
        api_client_authenticated,
        user,
    ):
        """Test that users cannot retrieve other users' folders."""
        other_user = UserFactory()
        other_account = EmailAccountFactory(user=other_user)
        other_folder = EmailFolderFactory(account=other_account)

        url = reverse("api:emailfolder-detail", kwargs={"pk": other_folder.pk})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_filter_by_account(self, api_client_authenticated, user):
        """Test filtering folders by account."""
        # Users can only have one account (OneToOne relationship)
        account1 = EmailAccountFactory(user=user, name="Account 1")

        # Create another user with their own account
        other_user = UserFactory()
        account2 = EmailAccountFactory(user=other_user, name="Account 2")

        folder1 = EmailFolderFactory(account=account1, base_name="Inbox 1")
        folder2 = EmailFolderFactory(account=account2, base_name="Inbox 2")

        url = reverse("api:emailfolder-list")
        response = api_client_authenticated.get(url, {"account": account1.id})

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert response.data[0]["base_name"] == "Inbox 1"

    def test_filter_by_parent_null(self, api_client_authenticated, user):
        """Test filtering for top-level folders (parent=null)."""
        account = EmailAccountFactory(user=user)

        # Top-level folders
        folder1 = EmailFolderFactory(account=account, base_name="Inbox", parent=None)
        folder2 = EmailFolderFactory(account=account, base_name="Sent", parent=None)

        # Subfolder
        subfolder = EmailFolderFactory(
            account=account,
            base_name="Archive",
            parent=folder1,
        )

        url = reverse("api:emailfolder-list")
        response = api_client_authenticated.get(url, {"parent": "null"})

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 2  # noqa: PLR2004
        folder_names = [folder["base_name"] for folder in response.data]
        assert "Inbox" in folder_names
        assert "Sent" in folder_names
        assert "Archive" not in folder_names

    def test_filter_by_parent_id(self, api_client_authenticated, user):
        """Test filtering folders by parent folder ID."""
        account = EmailAccountFactory(user=user)
        parent = EmailFolderFactory(account=account, base_name="Inbox")

        # Subfolders of parent
        subfolder1 = EmailFolderFactory(
            account=account,
            base_name="Projects",
            parent=parent,
        )
        subfolder2 = EmailFolderFactory(
            account=account,
            base_name="Archive",
            parent=parent,
        )

        # Another top-level folder
        other_folder = EmailFolderFactory(account=account, base_name="Sent")

        url = reverse("api:emailfolder-list")
        response = api_client_authenticated.get(url, {"parent": parent.id})

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 2  # noqa: PLR2004
        folder_names = [folder["base_name"] for folder in response.data]
        assert "Projects" in folder_names
        assert "Archive" in folder_names
        assert "Sent" not in folder_names

    def test_search_folders(self, api_client_authenticated, user):
        """Test searching folders by name."""
        account = EmailAccountFactory(user=user)
        EmailFolderFactory(account=account, base_name="Work Projects")
        EmailFolderFactory(account=account, base_name="Personal Projects")
        EmailFolderFactory(account=account, base_name="Archive")

        url = reverse("api:emailfolder-list")
        response = api_client_authenticated.get(url, {"search": "projects"})

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 2  # noqa: PLR2004
        folder_names = [folder["base_name"] for folder in response.data]
        assert "Work Projects" in folder_names
        assert "Personal Projects" in folder_names
        assert "Archive" not in folder_names

    def test_search_case_insensitive(self, api_client_authenticated, user):
        """Test that search is case-insensitive."""
        account = EmailAccountFactory(user=user)
        EmailFolderFactory(account=account, base_name="Important")

        url = reverse("api:emailfolder-list")
        response = api_client_authenticated.get(url, {"search": "IMPORTANT"})

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert response.data[0]["base_name"] == "Important"

    def test_folders_ordered_by_name(self, api_client_authenticated, user):
        """Test that folders are ordered alphabetically by name."""
        account = EmailAccountFactory(user=user)
        EmailFolderFactory(account=account, base_name="Sent")
        EmailFolderFactory(account=account, base_name="Archive")
        EmailFolderFactory(account=account, base_name="Inbox")

        url = reverse("api:emailfolder-list")
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        folder_names = [folder["base_name"] for folder in response.data]
        assert folder_names == ["Archive", "Inbox", "Sent"]

    def test_tree_action(self, api_client_authenticated, user):
        """Test the tree action returns hierarchical folder structure."""
        account = EmailAccountFactory(user=user)

        # Top-level folders
        inbox = EmailFolderFactory(account=account, base_name="Inbox")
        sent = EmailFolderFactory(account=account, base_name="Sent")

        # Subfolders
        projects = EmailFolderFactory(
            account=account,
            base_name="Projects",
            parent=inbox,
        )
        archive = EmailFolderFactory(
            account=account,
            base_name="Archive",
            parent=inbox,
        )

        # Nested subfolder
        old_projects = EmailFolderFactory(
            account=account,
            base_name="Old",
            parent=projects,
        )

        url = reverse("api:emailfolder-tree")
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 2  # noqa: PLR2004 - Only top-level folders

        # Find the Inbox folder in response
        inbox_data = next(f for f in response.data if f["base_name"] == "Inbox")
        assert "subfolders" in inbox_data
        assert len(inbox_data["subfolders"]) == 2  # noqa: PLR2004

        # Check nested subfolders
        projects_data = next(
            f for f in inbox_data["subfolders"] if f["base_name"] == "Projects"
        )
        assert len(projects_data["subfolders"]) == 1
        assert projects_data["subfolders"][0]["base_name"] == "Old"

    def test_tree_action_filter_by_account(self, api_client_authenticated, user):
        """Test tree action with account filter."""
        # Users can only have one account (OneToOne relationship)
        account1 = EmailAccountFactory(user=user, name="Account 1")

        # Create another user with their own account
        other_user = UserFactory()
        account2 = EmailAccountFactory(user=other_user, name="Account 2")

        folder1 = EmailFolderFactory(account=account1, base_name="Inbox 1")
        folder2 = EmailFolderFactory(account=account2, base_name="Inbox 2")

        url = reverse("api:emailfolder-tree")
        response = api_client_authenticated.get(url, {"account": account1.id})

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert response.data[0]["base_name"] == "Inbox 1"

    def test_tree_action_empty(self, api_client_authenticated, user):
        """Test tree action when user has no folders."""
        url = reverse("api:emailfolder-tree")
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 0

    def test_subfolders_action(self, api_client_authenticated, user):
        """Test the subfolders action returns direct child folders."""
        account = EmailAccountFactory(user=user)
        parent = EmailFolderFactory(account=account, base_name="Inbox")

        # Direct subfolders
        subfolder1 = EmailFolderFactory(
            account=account,
            base_name="Projects",
            parent=parent,
        )
        subfolder2 = EmailFolderFactory(
            account=account,
            base_name="Archive",
            parent=parent,
        )

        # Nested subfolder (should not be in direct subfolders)
        nested = EmailFolderFactory(
            account=account,
            base_name="Old",
            parent=subfolder1,
        )

        url = reverse("api:emailfolder-subfolders", kwargs={"pk": parent.pk})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 2  # noqa: PLR2004 - Only direct children
        folder_names = [folder["base_name"] for folder in response.data]
        assert "Projects" in folder_names
        assert "Archive" in folder_names

        # But nested subfolders should be included in the subfolders field
        projects_data = next(f for f in response.data if f["base_name"] == "Projects")
        assert "subfolders" in projects_data
        assert len(projects_data["subfolders"]) == 1
        assert projects_data["subfolders"][0]["base_name"] == "Old"

    def test_subfolders_action_no_children(self, api_client_authenticated, user):
        """Test subfolders action for folder with no children."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account, base_name="Inbox")

        url = reverse("api:emailfolder-subfolders", kwargs={"pk": folder.pk})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 0

    def test_list_returns_basic_serializer(self, api_client_authenticated, user):
        """Test that list view returns basic serializer without statistics."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        url = reverse("api:emailfolder-list")
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        # List view should not include statistics
        assert "email_count" not in response.data[0]
        assert "unread_count" not in response.data[0]
        assert "subfolder_count" not in response.data[0]

    def test_folder_hierarchy(self, api_client_authenticated, user):
        """Test that folder parent-child relationships work correctly."""
        account = EmailAccountFactory(user=user)
        parent = EmailFolderFactory(account=account, base_name="Parent")
        child = EmailFolderFactory(
            account=account,
            base_name="Child",
            parent=parent,
        )

        url = reverse("api:emailfolder-detail", kwargs={"pk": child.pk})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.data["parent"] == parent.id

    def test_empty_folder_list(self, api_client_authenticated):
        """Test listing folders when user has no folders."""
        url = reverse("api:emailfolder-list")
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 0

    def test_retrieve_nonexistent_folder(self, api_client_authenticated):
        """Test retrieving a non-existent folder returns 404."""
        url = reverse("api:emailfolder-detail", kwargs={"pk": 99999})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_read_only_viewset(self, api_client_authenticated, user):
        """Test that the viewset is read-only (no create, update, delete)."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        # Test POST (create)
        url = reverse("api:emailfolder-list")
        response = api_client_authenticated.post(
            url,
            {"base_name": "New Folder", "account": account.id},
        )
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

        # Test PUT (update)
        url = reverse("api:emailfolder-detail", kwargs={"pk": folder.pk})
        response = api_client_authenticated.put(
            url,
            {"base_name": "Updated"},
        )
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

        # Test PATCH (partial update)
        response = api_client_authenticated.patch(url, {"base_name": "Updated"})
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

        # Test DELETE
        response = api_client_authenticated.delete(url)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_combined_filters(self, api_client_authenticated, user):
        """Test combining multiple filters."""
        account = EmailAccountFactory(user=user)

        # Top-level folders
        inbox = EmailFolderFactory(account=account, base_name="Work Inbox")
        sent = EmailFolderFactory(account=account, base_name="Personal Sent")

        # Subfolder
        archive = EmailFolderFactory(
            account=account,
            base_name="Work Archive",
            parent=inbox,
        )

        url = reverse("api:emailfolder-list")
        response = api_client_authenticated.get(
            url,
            {"account": account.id, "parent": "null", "search": "work"},
        )

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert response.data[0]["base_name"] == "Work Inbox"

    def test_folder_with_no_emails(self, api_client_authenticated, user):
        """Test retrieving folder with no emails shows zero counts."""
        account = EmailAccountFactory(user=user)
        folder = EmailFolderFactory(account=account)

        url = reverse("api:emailfolder-detail", kwargs={"pk": folder.pk})
        response = api_client_authenticated.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.data["email_count"] == 0
        assert response.data["unread_count"] == 0
