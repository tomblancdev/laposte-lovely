"""
Email Serializer

This module provides serializers for the Email model.
Email represents individual email messages with their content, metadata,
and relationships to addresses, folders, and other emails.
"""

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from django_overtuned.emails.models import Email

from .address import EmailAddressesSerializer


class EmailListSerializer(serializers.ModelSerializer[Email]):
    """
    Lightweight serializer for Email model used in list views.

    This serializer provides a minimal representation of emails suitable
    for displaying in email lists or previews. It includes only essential
    information to keep the payload small for performance.

    Fields:
        message_id: Unique message identifier (primary key)
        subject: Email subject line
        from_address: Sender's email address (nested serializer)
        date_sent: When the email was sent
        date_received: When the email was received
        is_read: Whether the email has been read
        folder: ID of the folder containing this email
        priority: Email priority level (if available)

    Note:
        - Body content is excluded for performance in list views
        - Use EmailDetailSerializer to get full email content
    """

    from_address = EmailAddressesSerializer(read_only=True)

    class Meta:
        model = Email
        fields = [
            "message_id",
            "subject",
            "from_address",
            "date_sent",
            "date_received",
            "is_read",
            "folder",
            "priority",
        ]
        read_only_fields = fields  # All fields are read-only for emails


class EmailDetailSerializer(serializers.ModelSerializer[Email]):
    """
    Comprehensive serializer for Email model with full content.

    This serializer includes all email data including body content,
    recipient lists, and reply information. Use this for single email
    retrieval where full details are needed.

    Additional Fields (compared to EmailListSerializer):
        body_text: Plain text email body
        body_html: HTML email body
        to_addresses: List of recipient email addresses
        reply_to_address: Reply-to email address (if specified)
        in_reply_to: Message ID of the email this is replying to
        json_data: Raw JSON data from email server

    Nested Serializers:
        - from_address: Full EmailAddresses object
        - to_addresses: List of EmailAddresses objects
        - reply_to_address: EmailAddresses object (if present)

    Note:
        All fields are read-only as emails are synced from external servers
        and should not be modified through the API.
    """

    from_address = EmailAddressesSerializer(read_only=True)
    to_addresses = EmailAddressesSerializer(many=True, read_only=True)
    reply_to_address = EmailAddressesSerializer(read_only=True)

    class Meta:
        model = Email
        fields = [
            "message_id",
            "subject",
            "from_address",
            "to_addresses",
            "reply_to_address",
            "date_sent",
            "date_received",
            "body_text",
            "body_html",
            "is_read",
            "folder",
            "priority",
            "in_reply_to",
            "json_data",
        ]
        read_only_fields = fields


class EmailThreadSerializer(EmailDetailSerializer):
    """
    Serializer for Email with thread context.

    Extends EmailDetailSerializer to include information about email threads
    (replies and the parent email this is replying to). Useful for displaying
    conversation threads.

    Additional Fields:
        replies_count: Number of direct replies to this email
        has_replies: Boolean indicating if email has any replies

    Note:
        For performance, this doesn't include nested reply objects.
        Use a separate endpoint to fetch the full thread if needed.
    """

    replies_count = serializers.SerializerMethodField()
    has_replies = serializers.SerializerMethodField()

    class Meta(EmailDetailSerializer.Meta):
        fields = [*EmailDetailSerializer.Meta.fields, "replies_count", "has_replies"]

    @extend_schema_field(
        {
            "type": "integer",
            "description": "Number of direct replies to this email",
            "readOnly": True,
        },
    )
    def get_replies_count(self, obj: Email) -> int:
        """
        Count the number of direct replies to this email.

        Args:
            obj: The Email instance

        Returns:
            int: Number of emails that are replies to this email
        """
        return obj.replies.count()

    @extend_schema_field(
        {
            "type": "boolean",
            "description": "Whether this email has any replies",
            "readOnly": True,
        },
    )
    def get_has_replies(self, obj: Email) -> bool:
        """
        Check if this email has any replies.

        Args:
            obj: The Email instance

        Returns:
            bool: True if there are replies, False otherwise
        """
        return obj.replies.exists()


__all__ = [
    "EmailDetailSerializer",
    "EmailListSerializer",
    "EmailThreadSerializer",
]
