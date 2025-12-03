"""
EmailFolder Views

This module provides API views for the EmailFolder model.
EmailFolder views allow users to list and retrieve their email folders.
"""

from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from django_overtuned.emails.api.serializers.folder import EmailFolderDetailSerializer
from django_overtuned.emails.api.serializers.folder import EmailFolderSerializer
from django_overtuned.emails.api.serializers.folder import EmailFolderTreeSerializer
from django_overtuned.emails.models import EmailAccount
from django_overtuned.emails.models import EmailFolder


class EmailFolderViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    """
    ViewSet for EmailFolder model.

    Provides read-only endpoints for accessing email folders. Folders are
    synced from email servers and organized in a hierarchical structure.

    Endpoints:
        GET /api/email-folders/ - List all folders
        GET /api/email-folders/{id}/ - Retrieve specific folder with stats
        GET /api/email-folders/tree/ - Get hierarchical folder structure
        GET /api/email-folders/{id}/subfolders/ - Get direct subfolders

    Permissions:
        - User must be authenticated
        - Users can only access folders in their own accounts

    Serializers:
        - List: EmailFolderSerializer (basic info)
        - Retrieve: EmailFolderDetailSerializer (includes statistics)
        - Tree: EmailFolderTreeSerializer (recursive subfolder structure)

    Query Parameters (list):
        - account: Filter by email account ID
        - parent: Filter by parent folder ID (use 'null' for top-level)
        - search: Search in folder name (case-insensitive)

    Folder Hierarchy:
        Folders support parent-child relationships for organizing emails.
        Use the 'tree' action to get the full hierarchy in one request.

    Example Usage:
        # List all folders for an account
        GET /api/email-folders/?account=1

        # List top-level folders only
        GET /api/email-folders/?parent=null

        # Get folder with statistics
        GET /api/email-folders/5/

        # Get full folder tree
        GET /api/email-folders/tree/?account=1

        # Get subfolders of a specific folder
        GET /api/email-folders/5/subfolders/

        # Search folders
        GET /api/email-folders/?search=inbox
    """

    permission_classes = [IsAuthenticated]
    queryset = EmailFolder.objects.all()

    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.

        - retrieve: Returns detailed serializer with statistics
        - tree: Returns tree serializer with nested subfolders
        - subfolders: Returns tree serializer for hierarchy
        - list/default: Returns basic serializer

        Returns:
            Serializer class appropriate for the current action
        """
        if self.action == "retrieve":
            return EmailFolderDetailSerializer
        if self.action in ["tree", "subfolders"]:
            return EmailFolderTreeSerializer
        return EmailFolderSerializer

    def get_queryset(self):
        """
        Filter queryset to return only folders from user's accounts.

        Applies filters based on query parameters:
        - account: Filter by email account ID
        - parent: Filter by parent folder ID
        - search: Search in folder name

        Returns:
            Filtered QuerySet of EmailFolder objects
        """
        # Ensure user is authenticated
        assert isinstance(self.request.user.id, int)

        # Get all email accounts for this user
        user_accounts = EmailAccount.objects.filter(user=self.request.user)

        # Base queryset: folders in user's accounts
        queryset = self.queryset.filter(account__in=user_accounts)

        # Select related to optimize queries
        queryset = queryset.select_related("account", "parent")

        # Filter by account if provided
        account_id = self.request.GET.get("account", None)
        if account_id:
            queryset = queryset.filter(account_id=account_id)

        # Filter by parent folder if provided
        parent_id = self.request.GET.get("parent", None)
        if parent_id == "null":
            # Get top-level folders (no parent)
            queryset = queryset.filter(parent__isnull=True)
        elif parent_id:
            queryset = queryset.filter(parent_id=parent_id)

        # Search in folder name if provided
        search = self.request.GET.get("search", None)
        if search:
            queryset = queryset.filter(base_name__icontains=search)

        # Order by name for consistency
        return queryset.order_by("base_name")

    @action(detail=False, methods=["get"])
    def tree(self, request):
        """
        Get hierarchical folder tree structure.

        Returns all top-level folders with recursively nested subfolders.
        Useful for building folder navigation UI components.

        Args:
            request: The HTTP request object

        Returns:
            Response with nested folder structure

        Query Parameters:
            account: Filter tree to specific account

        Example:
            GET /api/email-folders/tree/?account=1

            Response:
            [
                {
                    "id": 1,
                    "base_name": "Inbox",
                    "account": 1,
                    "parent": null,
                    "subfolders": [
                        {
                            "id": 2,
                            "base_name": "Projects",
                            "account": 1,
                            "parent": 1,
                            "subfolders": [...]
                        }
                    ]
                }
            ]

        Note:
            Only returns top-level folders in the root array.
            All nested folders are included in the 'subfolders' field.
        """
        # Get only top-level folders (parent is null)
        queryset = self.get_queryset().filter(parent__isnull=True)

        serializer = EmailFolderTreeSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def subfolders(self, request, pk=None):
        """
        Get direct subfolders of a specific folder.

        Returns only the immediate child folders (not recursive).
        Each subfolder includes its own nested subfolders.

        Args:
            request: The HTTP request object
            pk: Primary key of the parent folder

        Returns:
            Response with list of subfolders

        Example:
            GET /api/email-folders/1/subfolders/

            Returns all folders where parent_id = 1

        Use Case:
            Use this for lazy-loading folder trees where you load
            subfolders on demand when a user expands a folder.
        """
        folder = self.get_object()
        subfolders = folder.subfolders.all().order_by("base_name")

        serializer = EmailFolderTreeSerializer(
            subfolders,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)


__all__ = ["EmailFolderViewSet"]
