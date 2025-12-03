"""
EmailAddresses Serializer

This module provides serializers for the EmailAddresses model.
EmailAddresses stores unique email addresses that appear in emails
(from, to, reply-to fields).
"""

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from django_overtuned.emails.models import EmailAddresses


class EmailAddressesSerializer(serializers.ModelSerializer[EmailAddresses]):
    """
    Serializer for EmailAddresses model.

    This serializer handles email address records. Each address is stored
    once in the database and can be referenced by multiple emails.

    Fields:
        id: Primary key (auto-generated, read-only)
        address: The email address string (validated as email format)

    Validation:
        - Email format is automatically validated by Django's EmailField
        - Address must be unique (enforced at model level)

    Example:
        {
            "id": 1,
            "address": "user@example.com"
        }
    """

    class Meta:
        model = EmailAddresses
        fields = ["id", "address"]
        read_only_fields = ["id"]


class EmailAddressesDetailSerializer(EmailAddressesSerializer):
    """
    Detailed serializer for EmailAddresses with usage statistics.

    Extends the basic EmailAddressesSerializer to include counts of
    how many emails use this address in different contexts (from, to, reply-to).
    Useful for analytics and understanding email patterns.

    Additional Fields:
        emails_sent_count: Number of emails sent from this address
        emails_received_count: Number of emails sent to this address
        emails_reply_to_count: Number of emails with this as reply-to address
    """

    emails_sent_count = serializers.SerializerMethodField()
    emails_received_count = serializers.SerializerMethodField()
    emails_reply_to_count = serializers.SerializerMethodField()

    class Meta(EmailAddressesSerializer.Meta):
        fields = [
            *EmailAddressesSerializer.Meta.fields,
            "emails_sent_count",
            "emails_received_count",
            "emails_reply_to_count",
        ]

    @extend_schema_field(
        {
            "type": "integer",
            "description": "Number of emails sent from this address",
            "readOnly": True,
        },
    )
    def get_emails_sent_count(self, obj: EmailAddresses) -> int:
        """
        Count emails where this address is the sender (from_address).

        Args:
            obj: The EmailAddresses instance

        Returns:
            int: Number of emails sent from this address
        """
        return obj.emails_from.count()

    @extend_schema_field(
        {
            "type": "integer",
            "description": "Number of emails sent to this address",
            "readOnly": True,
        },
    )
    def get_emails_received_count(self, obj: EmailAddresses) -> int:
        """
        Count emails where this address is a recipient (to_addresses).

        Args:
            obj: The EmailAddresses instance

        Returns:
            int: Number of emails sent to this address
        """
        return obj.emails_to.count()

    @extend_schema_field(
        {
            "type": "integer",
            "description": "Number of emails with this as reply-to address",
            "readOnly": True,
        },
    )
    def get_emails_reply_to_count(self, obj: EmailAddresses) -> int:
        """
        Count emails where this address is the reply-to address.

        Args:
            obj: The EmailAddresses instance

        Returns:
            int: Number of emails with this as reply-to
        """
        return obj.emails_reply_to.count()


__all__ = ["EmailAddressesDetailSerializer", "EmailAddressesSerializer"]
