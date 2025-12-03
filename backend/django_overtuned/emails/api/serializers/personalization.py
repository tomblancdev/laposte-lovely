"""
Email Personalization Serializers

This module provides serializers for EmailPersonalization and
EmailFolderPersonalization models. These models allow users to add
personal metadata to emails and folders (tags, notes, colors, etc.)
without modifying the original email data.
"""

from libs.db.serializers import ColorFieldSerializer
from rest_framework import serializers

from django_overtuned.emails.models import Email
from django_overtuned.emails.models import EmailFolder
from django_overtuned.emails.models import EmailFolderPersonalization
from django_overtuned.emails.models import EmailPersonalization
from django_overtuned.user_tags.api.serializers import UserTaggitSerializer
from django_overtuned.user_tags.api.serializers import UserTagListSerializerField


class EmailPersonalizationSerializer(
    UserTaggitSerializer,
    serializers.ModelSerializer[EmailPersonalization],
):
    """
    Serializer for EmailPersonalization model.

    This serializer handles user-specific metadata for individual emails.
    It extends UserTaggitSerializer to support user-specific tags and adds
    support for notes and importance levels.

    Fields:
        id: Primary key (auto-generated, read-only)
        email: Message ID of the associated email (write-once)
        tags: User-specific tags (handled by UserTagListSerializerField)
        notes: Personal notes about the email
        importance_level: Personal importance rating (integer)

    Tag Behavior:
        - Tags are user-specific (same tag name for different users are separate)
        - Tags are created automatically when assigned to an email
        - Requires authenticated user in request context

    Example:
        {
            "id": 1,
            "email": "msg-12345@mail.example.com",
            "tags": ["important", "follow-up"],
            "notes": "Needs response by Friday",
            "importance_level": 5
        }

    Note:
        The email field should only be set on creation and cannot be changed
        after the personalization record is created.
    """

    tags = UserTagListSerializerField(required=False)
    email = serializers.PrimaryKeyRelatedField(
        queryset=Email.objects.all(),
        help_text="Primary key of the email to personalize",
    )

    class Meta:
        model = EmailPersonalization
        fields = ["id", "email", "tags", "notes", "importance_level"]
        read_only_fields = ["id"]

    def create(self, validated_data: dict) -> EmailPersonalization:
        """
        Create a new EmailPersonalization instance.

        Extracts tag data and creates the instance, then saves tags
        using the UserTaggitSerializer's _save_tags method which
        handles user-specific tag creation.

        Args:
            validated_data: Validated data from the serializer

        Returns:
            EmailPersonalization: The created instance with tags
        """
        # Extract tags from validated data
        tags_data = validated_data.pop("tags", [])

        # Create the personalization instance
        instance = EmailPersonalization.objects.create(**validated_data)

        # Save tags using the parent class method
        self._save_tags(instance, tags_data)

        return instance

    def update(
        self,
        instance: EmailPersonalization,
        validated_data: dict,
    ) -> EmailPersonalization:
        """
        Update an existing EmailPersonalization instance.

        Updates all fields and handles tag updates through the
        UserTaggitSerializer's _save_tags method.

        Args:
            instance: The EmailPersonalization instance to update
            validated_data: Validated data from the serializer

        Returns:
            EmailPersonalization: The updated instance
        """
        # Extract tags from validated data
        tags_data = validated_data.pop("tags", None)

        # Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update tags if provided
        if tags_data is not None:
            self._save_tags(instance, tags_data)

        return instance


class EmailFolderPersonalizationSerializer(
    UserTaggitSerializer,
    serializers.ModelSerializer[EmailFolderPersonalization],
):
    """
    Serializer for EmailFolderPersonalization model.

    This serializer handles user-specific metadata for email folders.
    It allows users to customize folder appearance and organization
    with display names, colors, and tags.

    Fields:
        id: Primary key (auto-generated, read-only)
        folder: ID of the associated email folder (write-once)
        display_name: Custom display name for the folder
        display_color: Color in multiple formats (HEX, RGB, RGBA, HSL, HSLA, named)
        tags: User-specific tags for organization

    Display Customization:
        - display_name: Override the folder's base_name with a custom label
        - display_color: Set a color for visual identification in UI
          Supported formats: #RRGGBB, rgb(r,g,b), rgba(r,g,b,a), hsl(h,s%,l%),
          hsla(h,s%,l%,a), or CSS named colors (e.g., "red", "blue")
        - tags: Organize folders with user-specific tags

    Example:
        {
            "id": 1,
            "folder": 5,
            "display_name": "Work Stuff",
            "display_color": "#3498db",  // or "rgb(52, 152, 219)"
            "tags": ["work", "high-priority"]
        }

    Color Validation:
        The display_color field uses ColorFieldSerializer which automatically
        validates and normalizes color values. All supported formats are
        validated for correctness (value ranges, syntax, etc.).
    """

    tags = UserTagListSerializerField(required=False)
    display_color = ColorFieldSerializer(required=False, allow_blank=True)
    folder = serializers.PrimaryKeyRelatedField(
        queryset=EmailFolder.objects.all(),
        help_text="Primary key of the email folder to personalize",
    )

    class Meta:
        model = EmailFolderPersonalization
        fields = ["id", "folder", "display_name", "display_color", "tags"]
        read_only_fields = ["id"]

    def create(self, validated_data: dict) -> EmailFolderPersonalization:
        """
        Create a new EmailFolderPersonalization instance.

        Args:
            validated_data: Validated data from the serializer

        Returns:
            EmailFolderPersonalization: The created instance with tags
        """
        # Extract tags from validated data
        tags_data = validated_data.pop("tags", [])

        # Create the personalization instance
        instance = EmailFolderPersonalization.objects.create(**validated_data)

        # Save tags using the parent class method
        self._save_tags(instance, tags_data)

        return instance

    def update(
        self,
        instance: EmailFolderPersonalization,
        validated_data: dict,
    ) -> EmailFolderPersonalization:
        """
        Update an existing EmailFolderPersonalization instance.

        Args:
            instance: The EmailFolderPersonalization instance to update
            validated_data: Validated data from the serializer

        Returns:
            EmailFolderPersonalization: The updated instance
        """
        # Extract tags from validated data
        tags_data = validated_data.pop("tags", None)

        # Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update tags if provided
        if tags_data is not None:
            self._save_tags(instance, tags_data)

        return instance


__all__ = [
    "EmailFolderPersonalizationSerializer",
    "EmailPersonalizationSerializer",
]
