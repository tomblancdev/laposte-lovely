"""
Email Personalization Views

This module provides API views for EmailPersonalization and
EmailFolderPersonalization models. These views allow users to add
and manage personal metadata for emails and folders.
"""

from rest_framework.mixins import CreateModelMixin
from rest_framework.mixins import DestroyModelMixin
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from django_overtuned.emails.api.serializers.personalization import (
    EmailFolderPersonalizationSerializer,
)
from django_overtuned.emails.api.serializers.personalization import (
    EmailPersonalizationSerializer,
)
from django_overtuned.emails.models import Email
from django_overtuned.emails.models import EmailAccount
from django_overtuned.emails.models import EmailFolder
from django_overtuned.emails.models import EmailFolderPersonalization
from django_overtuned.emails.models import EmailPersonalization


class EmailPersonalizationViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    GenericViewSet,
):
    """
    ViewSet for EmailPersonalization model.

    Provides full CRUD operations for email personalization metadata.
    Users can add tags, notes, and importance levels to their emails.

    Endpoints:
        GET /api/email-personalizations/ - List all personalizations
        POST /api/email-personalizations/ - Create new personalization
        GET /api/email-personalizations/{id}/ - Retrieve personalization
        PUT /api/email-personalizations/{id}/ - Update personalization
        PATCH /api/email-personalizations/{id}/ - Partial update
        DELETE /api/email-personalizations/{id}/ - Delete personalization

    Permissions:
        - User must be authenticated
        - Users can only manage personalizations for their own emails

    Query Parameters (list):
        - email: Filter by email message_id
        - tags: Filter by tag name (comma-separated for multiple)
        - has_notes: Filter entries with notes (true/false)
        - min_importance: Filter by minimum importance level

    Tags:
        Tags are user-specific and automatically created when assigned.
        Multiple users can use the same tag name without conflicts.

    Example Usage:
        # Create personalization for an email
        POST /api/email-personalizations/
        {
            "email": "msg-12345@mail.example.com",
            "tags": ["important", "follow-up"],
            "notes": "Needs response by Friday",
            "importance_level": 5
        }

        # Update tags
        PATCH /api/email-personalizations/1/
        {
            "tags": ["important", "urgent", "client"]
        }

        # List all emails tagged as "important"
        GET /api/email-personalizations/?tags=important

        # Delete personalization (removes tags and notes)
        DELETE /api/email-personalizations/1/
    """

    permission_classes = [IsAuthenticated]
    queryset = EmailPersonalization.objects.all()
    serializer_class = EmailPersonalizationSerializer

    def get_queryset(self):
        """
        Filter queryset to return only personalizations for user's emails.

        Applies filters based on query parameters:
        - email: Filter by email message_id
        - tags: Filter by tag name(s)
        - has_notes: Filter entries with notes
        - min_importance: Filter by minimum importance level

        Returns:
            Filtered QuerySet of EmailPersonalization objects
        """
        # Ensure user is authenticated
        assert isinstance(self.request.user.id, int)

        # Get all email accounts for this user
        user_accounts = EmailAccount.objects.filter(user=self.request.user)

        # Get all folders for these accounts
        user_folders = EmailFolder.objects.filter(account__in=user_accounts)

        # Get all emails in these folders
        user_emails = Email.objects.filter(folder__in=user_folders)

        # Base queryset: personalizations for user's emails
        queryset = self.queryset.filter(email__in=user_emails)

        # Select related to optimize queries
        queryset = queryset.select_related("email").prefetch_related("tags")

        # Filter by email if provided
        email_id = self.request.GET.get("email", None)
        if email_id:
            queryset = queryset.filter(email_id=email_id)

        # Filter by tags if provided
        tags = self.request.GET.get("tags", None)
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            for tag_name in tag_list:
                queryset = queryset.filter(tags__name=tag_name)

        # Filter by presence of notes
        has_notes = self.request.GET.get("has_notes", None)
        if has_notes is not None:
            has_notes_bool = has_notes.lower() in ["true", "1", "yes"]
            if has_notes_bool:
                queryset = queryset.exclude(notes="")
            else:
                queryset = queryset.filter(notes="")

        # Filter by minimum importance level
        min_importance = self.request.GET.get("min_importance", None)
        if min_importance:
            try:
                min_importance_int = int(min_importance)
                queryset = queryset.filter(
                    importance_level__gte=min_importance_int,
                )
            except ValueError:
                # Invalid importance level, ignore it
                pass

        return queryset.distinct()

    def perform_create(self, serializer):
        """
        Create personalization with request context for user-specific tags.

        The serializer needs the request context to associate tags with
        the authenticated user.

        Args:
            serializer: The EmailPersonalizationSerializer instance
        """
        serializer.save()


class EmailFolderPersonalizationViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    GenericViewSet,
):
    """
    ViewSet for EmailFolderPersonalization model.

    Provides full CRUD operations for folder personalization metadata.
    Users can customize folder display names, colors, and add tags.

    Endpoints:
        GET /api/email-folder-personalizations/ - List all personalizations
        POST /api/email-folder-personalizations/ - Create personalization
        GET /api/email-folder-personalizations/{id}/ - Retrieve details
        PUT /api/email-folder-personalizations/{id}/ - Update personalization
        PATCH /api/email-folder-personalizations/{id}/ - Partial update
        DELETE /api/email-folder-personalizations/{id}/ - Delete

    Permissions:
        - User must be authenticated
        - Users can only manage personalizations for their own folders

    Query Parameters (list):
        - folder: Filter by folder ID
        - tags: Filter by tag name (comma-separated)
        - has_display_name: Filter by custom display name presence

    Use Cases:
        - Rename folders for personal organization
        - Color-code folders for visual identification
        - Tag folders for cross-cutting organization

    Example Usage:
        # Customize a folder's appearance
        POST /api/email-folder-personalizations/
        {
            "folder": 5,
            "display_name": "Work Stuff",
            "display_color": "#3498db",
            "tags": ["work", "high-priority"]
        }

        # Update folder color
        PATCH /api/email-folder-personalizations/1/
        {
            "display_color": "#e74c3c"
        }

        # List all work-tagged folders
        GET /api/email-folder-personalizations/?tags=work
    """

    permission_classes = [IsAuthenticated]
    queryset = EmailFolderPersonalization.objects.all()
    serializer_class = EmailFolderPersonalizationSerializer

    def get_queryset(self):
        """
        Filter queryset to personalizations for user's folders.

        Applies filters based on query parameters:
        - folder: Filter by folder ID
        - tags: Filter by tag name(s)
        - has_display_name: Filter entries with custom display names

        Returns:
            Filtered QuerySet of EmailFolderPersonalization objects
        """
        # Ensure user is authenticated
        assert isinstance(self.request.user.id, int)

        # Get all email accounts for this user
        user_accounts = EmailAccount.objects.filter(user=self.request.user)

        # Get all folders for these accounts
        user_folders = EmailFolder.objects.filter(account__in=user_accounts)

        # Base queryset: personalizations for user's folders
        queryset = self.queryset.filter(folder__in=user_folders)

        # Select related to optimize queries
        queryset = queryset.select_related("folder").prefetch_related("tags")

        # Filter by folder if provided
        folder_id = self.request.GET.get("folder", None)
        if folder_id:
            queryset = queryset.filter(folder_id=folder_id)

        # Filter by tags if provided
        tags = self.request.GET.get("tags", None)
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            for tag_name in tag_list:
                queryset = queryset.filter(tags__name=tag_name)

        # Filter by presence of display name
        has_display_name = self.request.GET.get("has_display_name", None)
        if has_display_name is not None:
            has_display_name_bool = has_display_name.lower() in [
                "true",
                "1",
                "yes",
            ]
            if has_display_name_bool:
                queryset = queryset.exclude(display_name="")
            else:
                queryset = queryset.filter(display_name="")

        return queryset.distinct()

    def perform_create(self, serializer):
        """
        Create personalization with request context for user-specific tags.

        Args:
            serializer: The EmailFolderPersonalizationSerializer instance
        """
        serializer.save()


__all__ = [
    "EmailFolderPersonalizationViewSet",
    "EmailPersonalizationViewSet",
]
