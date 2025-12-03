"""
EmailAddresses Views

This module provides API views for the EmailAddresses model.
EmailAddresses views allow users to list and retrieve email addresses
that appear in their emails.
"""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from django_overtuned.emails.api.serializers.address import (
    EmailAddressesDetailSerializer,
)
from django_overtuned.emails.api.serializers.address import EmailAddressesSerializer
from django_overtuned.emails.models import Email
from django_overtuned.emails.models import EmailAccount
from django_overtuned.emails.models import EmailAddresses
from django_overtuned.emails.models import EmailFolder


@extend_schema(tags=["Email Addresses"])
class EmailAddressesViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    """
    ViewSet for EmailAddresses model.

    Provides read-only endpoints for email addresses that appear in the
    user's emails. Email addresses are automatically extracted from
    incoming emails and stored once for efficient querying.

    Endpoints:
        GET /api/email-addresses/ - List all email addresses
        GET /api/email-addresses/{id}/ - Retrieve specific address with stats

    Permissions:
        - User must be authenticated
        - Users can only see addresses from their own emails

    Serializers:
        - List: EmailAddressesSerializer (basic info)
        - Retrieve: EmailAddressesDetailSerializer (includes usage statistics)

    Query Parameters (list):
        - search: Filter by email address (case-insensitive contains)
        - limit: Limit number of results (default: no limit)

    Use Cases:
        - Autocomplete for email composition
        - Contact list building
        - Email analytics and statistics

    Example Usage:
        # List all addresses
        GET /api/email-addresses/

        # Search for specific addresses
        GET /api/email-addresses/?search=@example.com

        # Get address with usage statistics
        GET /api/email-addresses/1/

        # Limit results for autocomplete
        GET /api/email-addresses/?search=john&limit=10
    """

    permission_classes = [IsAuthenticated]
    queryset = EmailAddresses.objects.all()

    @extend_schema(
        summary="List email addresses",
        description=(
            "Retrieve a list of email addresses that appear in the user's "
            "emails. Useful for autocomplete and contact list features."
        ),
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by email address (case-insensitive contains)",
                required=False,
            ),
            OpenApiParameter(
                name="limit",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Limit number of results (useful for autocomplete)",
                required=False,
            ),
        ],
        responses={200: EmailAddressesSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        """List all email addresses from user's emails."""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve email address details",
        description=(
            "Get detailed information about a specific email address including "
            "usage statistics."
        ),
        responses={200: EmailAddressesDetailSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve specific email address with statistics."""
        return super().retrieve(request, *args, **kwargs)

    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.

        - retrieve: Returns detailed serializer with usage statistics
        - list/default: Returns basic serializer for performance

        Returns:
            Serializer class appropriate for the current action
        """
        if self.action == "retrieve":
            return EmailAddressesDetailSerializer
        return EmailAddressesSerializer

    def get_queryset(self):
        """
        Filter queryset to return only addresses from user's emails.

        This ensures users only see email addresses that appear in their
        own email accounts (as sender, recipient, or reply-to).

        Applies additional filters based on query parameters:
        - search: Filter by address (case-insensitive contains)
        - limit: Limit number of results

        Returns:
            Filtered QuerySet of EmailAddresses objects
        """
        # Ensure user is authenticated
        assert isinstance(self.request.user.id, int)

        # Get all email accounts for this user
        user_accounts = EmailAccount.objects.filter(user=self.request.user)

        # Get all folders for these accounts
        user_folders = EmailFolder.objects.filter(account__in=user_accounts)

        # Get all emails in these folders
        user_emails = Email.objects.filter(folder__in=user_folders)

        # Get all unique addresses from these emails
        address_ids = set()

        # Addresses from "from" field
        from_address_ids = user_emails.filter(
            from_address__isnull=False,
        ).values_list("from_address_id", flat=True)
        address_ids.update(from_address_ids)

        # Addresses from "to" field
        to_address_ids = user_emails.values_list(
            "to_addresses",
            flat=True,
        ).distinct()
        address_ids.update(addr_id for addr_id in to_address_ids if addr_id is not None)

        # Addresses from "reply_to" field
        reply_to_address_ids = user_emails.filter(
            reply_to_address__isnull=False,
        ).values_list("reply_to_address_id", flat=True)
        address_ids.update(reply_to_address_ids)

        # Filter to these addresses
        queryset = self.queryset.filter(id__in=address_ids)

        # Apply search filter if provided
        search = self.request.GET.get("search", None)
        if search:
            queryset = queryset.filter(address__icontains=search)

        # Order by address for consistency
        queryset = queryset.order_by("address")

        # Apply limit if provided
        limit = self.request.GET.get("limit", None)
        if limit:
            try:
                limit_int = int(limit)
                queryset = queryset[:limit_int]
            except ValueError:
                # Invalid limit, ignore it
                pass

        return queryset


__all__ = ["EmailAddressesViewSet"]
