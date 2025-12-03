"""
EmailAccount Views

This module provides API views for the EmailAccount model.
EmailAccount views allow users to list and retrieve their email accounts.
"""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from django_overtuned.emails.api.serializers.account import EmailAccountDetailSerializer
from django_overtuned.emails.api.serializers.account import EmailAccountSerializer
from django_overtuned.emails.models import EmailAccount


@extend_schema(tags=["Email Accounts"])
class EmailAccountViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    """
    ViewSet for EmailAccount model.

    Provides endpoints for listing and retrieving email accounts.
    Users can only access their own email accounts.

    Endpoints:
        GET /api/email-accounts/ - List all email accounts for current user
        GET /api/email-accounts/{id}/ - Retrieve specific email account details

    Permissions:
        - User must be authenticated
        - Users can only access their own accounts

    Serializers:
        - List: EmailAccountSerializer (lightweight)
        - Retrieve: EmailAccountDetailSerializer (includes statistics)

    Query Parameters (list):
        - search: Filter accounts by name (case-insensitive contains)

    Example Usage:
        # List all accounts
        GET /api/email-accounts/

        # Get specific account with statistics
        GET /api/email-accounts/1/

        # Search accounts by name
        GET /api/email-accounts/?search=work
    """

    permission_classes = [IsAuthenticated]
    queryset = EmailAccount.objects.all()

    @extend_schema(
        summary="List email accounts",
        description=(
            "Retrieve a list of email accounts owned by the authenticated user."
        ),
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter accounts by name (case-insensitive contains)",
                required=False,
            ),
        ],
        responses={200: EmailAccountSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        """List all email accounts for current user."""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve email account details",
        description=(
            "Get detailed information about a specific email account including "
            "statistics."
        ),
        responses={200: EmailAccountDetailSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve specific email account details."""
        return super().retrieve(request, *args, **kwargs)

    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.

        - retrieve: Returns detailed serializer with statistics
        - list/default: Returns basic serializer for performance

        Returns:
            Serializer class appropriate for the current action
        """
        if self.action == "retrieve":
            return EmailAccountDetailSerializer
        return EmailAccountSerializer

    def get_queryset(self):
        """
        Filter queryset to return only accounts owned by the current user.

        Applies additional filters based on query parameters:
        - search: Filter by account name (case-insensitive)

        Returns:
            Filtered QuerySet of EmailAccount objects
        """
        # Ensure user is authenticated
        assert isinstance(self.request.user.id, int)

        # Base queryset: only user's own accounts
        queryset = self.queryset.filter(user=self.request.user)

        # Apply search filter if provided
        search = self.request.GET.get("search", None)
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset


__all__ = ["EmailAccountViewSet"]
