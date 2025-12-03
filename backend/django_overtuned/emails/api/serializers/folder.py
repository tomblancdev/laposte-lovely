"""
EmailFolder Serializer

This module provides serializers for the EmailFolder model.
EmailFolder represents folders/labels in email accounts (Inbox, Sent, etc.)
and supports hierarchical folder structures.
"""

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from django_overtuned.emails.models import EmailFolder


class EmailFolderSerializer(serializers.ModelSerializer[EmailFolder]):
    """
    Basic serializer for EmailFolder model.

    This serializer handles email folder data including hierarchical
    relationships (parent/subfolder structure).

    Fields:
        id: Primary key (auto-generated, read-only)
        base_name: The folder name from the email server
        account: ID of the email account this folder belongs to
        parent: ID of the parent folder (null for top-level folders)

    Hierarchy:
        Folders can be nested in a parent-child relationship.
        For example: Inbox -> Projects -> Client A

    Note:
        All fields are read-only as folders are synced from email servers
        and should not be modified directly through the API.
    """

    class Meta:
        model = EmailFolder
        fields = ["id", "base_name", "account", "parent"]
        read_only_fields = fields


class EmailFolderTreeSerializer(EmailFolderSerializer):
    """
    Serializer for EmailFolder with nested subfolder structure.

    Extends EmailFolderSerializer to include recursively nested subfolders,
    allowing you to retrieve the entire folder hierarchy in a single request.
    Useful for building folder tree UI components.

    Additional Fields:
        subfolders: List of child folders (recursively serialized)

    Example Structure:
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

    Warning:
        Deep folder hierarchies may result in large response payloads.
        Consider limiting recursion depth for very large folder structures.
    """

    subfolders = serializers.SerializerMethodField()

    class Meta(EmailFolderSerializer.Meta):
        fields = [*EmailFolderSerializer.Meta.fields, "subfolders"]

    @extend_schema_field(
        {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "readOnly": True},
                    "base_name": {"type": "string", "readOnly": True},
                    "account": {"type": "integer", "readOnly": True},
                    "parent": {
                        "type": "integer",
                        "nullable": True,
                        "readOnly": True,
                    },
                    "subfolders": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "description": "Recursively nested folder structure",
                        },
                        "description": (
                            "Child folders (recursively contains same structure)"
                        ),
                    },
                },
                "required": ["id", "base_name", "account", "subfolders"],
            },
            "description": "List of child folders with recursive subfolder structure",
        },
    )
    def get_subfolders(self, obj: EmailFolder) -> list[dict]:
        """
        Recursively serialize all subfolders.

        Args:
            obj: The EmailFolder instance

        Returns:
            list: Serialized list of subfolder dictionaries
        """
        # Recursively serialize subfolders using the same serializer
        subfolders = obj.subfolders.all()
        return EmailFolderTreeSerializer(
            subfolders,
            many=True,
            context=self.context,
        ).data


class EmailFolderDetailSerializer(EmailFolderSerializer):
    """
    Detailed serializer for EmailFolder with statistics.

    Extends EmailFolderSerializer to include computed fields about
    the folder's contents, such as email counts and read/unread status.

    Additional Fields:
        email_count: Total number of emails in this folder
        unread_count: Number of unread emails in this folder
        subfolder_count: Number of direct subfolders

    Use Case:
        Use this serializer when displaying folder details or building
        folder navigation with email counts (e.g., "Inbox (15 unread)").
    """

    email_count = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    subfolder_count = serializers.SerializerMethodField()

    class Meta(EmailFolderSerializer.Meta):
        fields = [
            *EmailFolderSerializer.Meta.fields,
            "email_count",
            "unread_count",
            "subfolder_count",
        ]

    @extend_schema_field(
        {
            "type": "integer",
            "description": "Total number of emails in this folder",
            "readOnly": True,
        },
    )
    def get_email_count(self, obj: EmailFolder) -> int:
        """
        Count total emails in this folder.

        Args:
            obj: The EmailFolder instance

        Returns:
            int: Number of emails in this folder
        """
        return obj.emails.count()

    @extend_schema_field(
        {
            "type": "integer",
            "description": "Number of unread emails in this folder",
            "readOnly": True,
        },
    )
    def get_unread_count(self, obj: EmailFolder) -> int:
        """
        Count unread emails in this folder.

        Args:
            obj: The EmailFolder instance

        Returns:
            int: Number of unread emails in this folder
        """
        return obj.emails.filter(is_read=False).count()

    @extend_schema_field(
        {
            "type": "integer",
            "description": "Number of direct child folders (non-recursive)",
            "readOnly": True,
        },
    )
    def get_subfolder_count(self, obj: EmailFolder) -> int:
        """
        Count direct subfolders (non-recursive).

        Args:
            obj: The EmailFolder instance

        Returns:
            int: Number of immediate child folders
        """
        return obj.subfolders.count()


__all__ = [
    "EmailFolderDetailSerializer",
    "EmailFolderSerializer",
    "EmailFolderTreeSerializer",
]
