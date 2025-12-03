"""
EmailAccount Serializer

This module provides serializers for the EmailAccount model.
EmailAccount represents an email account associated with a user (Gmail, Outlook, etc).
"""

from rest_framework import serializers

from django_overtuned.emails.models import Email
from django_overtuned.emails.models import EmailAccount


class EmailAccountSerializer(serializers.ModelSerializer[EmailAccount]):
    """
    Serializer for EmailAccount model.

    This serializer handles the serialization and deserialization of EmailAccount instances.
    It provides read-only access to account information including:
    - id: The unique identifier for the account
    - name: The display name of the email account
    - user: The user who owns this account (read-only)

    Fields:
        id: Primary key (read-only)
        name: Account name (e.g., "Work Gmail", "Personal Outlook")
        user: Associated user ID (read-only, automatically set from request)

    Note:
        The user field is read-only as it should be automatically set
        from the authenticated user making the request.
    """  # noqa: E501

    class Meta:
        model = EmailAccount
        fields = ["id", "name", "user"]
        read_only_fields = ["id", "user"]


class EmailAccountDetailSerializer(EmailAccountSerializer):
    """
    Detailed serializer for EmailAccount model.

    Extends EmailAccountSerializer to include additional computed fields
    such as folder count and total email count for the account.
    Use this serializer when retrieving a single account to provide
    more context about the account's contents.

    Additional Fields:
        folder_count: Number of folders in this account
        email_count: Total number of emails across all folders
    """

    folder_count = serializers.SerializerMethodField()
    email_count = serializers.SerializerMethodField()

    class Meta(EmailAccountSerializer.Meta):
        fields = [*EmailAccountSerializer.Meta.fields, "folder_count", "email_count"]

    def get_folder_count(self, obj: EmailAccount) -> int:
        """
        Calculate the total number of folders for this account.

        Args:
            obj: The EmailAccount instance

        Returns:
            int: Count of folders associated with this account
        """
        return obj.email_folders.count()

    def get_email_count(self, obj: EmailAccount) -> int:
        """
        Calculate the total number of emails across all folders.

        Args:
            obj: The EmailAccount instance

        Returns:
            int: Total count of emails in all folders of this account
        """

        # Get all folder IDs for this account
        folder_ids = obj.email_folders.values_list("id", flat=True)

        # Count emails in those folders
        return Email.objects.filter(folder_id__in=folder_ids).count()


__all__ = [
    "EmailAccountDetailSerializer",
    "EmailAccountSerializer",
]
