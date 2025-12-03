"""
Email Views

This module provides API views for the Email model.
Email views allow users to list, retrieve, and filter their emails.
"""

from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from django_overtuned.emails.api.serializers.email import EmailDetailSerializer
from django_overtuned.emails.api.serializers.email import EmailListSerializer
from django_overtuned.emails.api.serializers.email import EmailThreadSerializer
from django_overtuned.emails.models import Email
from django_overtuned.emails.models import EmailAccount
from django_overtuned.emails.models import EmailFolder


class EmailViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    """
    ViewSet for Email model.

    Provides read-only endpoints for accessing emails. Emails are synced
    from external email servers and should not be modified through this API.

    Endpoints:
        GET /api/emails/ - List emails with filtering and search
        GET /api/emails/{message_id}/ - Retrieve specific email details
        GET /api/emails/{message_id}/thread/ - Get email with thread context

    Permissions:
        - User must be authenticated
        - Users can only access emails in their own accounts

    Serializers:
        - List: EmailListSerializer (lightweight, no body content)
        - Retrieve: EmailDetailSerializer (full email content)
        - Thread: EmailThreadSerializer (includes reply information)

    Query Parameters (list):
        - folder: Filter by folder ID
        - is_read: Filter by read status (true/false)
        - from_address: Filter by sender address ID
        - search: Search in subject and body (case-insensitive)
        - ordering: Order results (date_sent, date_received, subject)
        - limit: Limit number of results
        - offset: Offset for pagination

    Lookup Field:
        Uses message_id instead of id for more semantic URLs

    Example Usage:
        # List all emails in a folder
        GET /api/emails/?folder=1

        # List unread emails
        GET /api/emails/?is_read=false

        # Search emails
        GET /api/emails/?search=meeting

        # Get specific email
        GET /api/emails/msg-12345@mail.example.com/

        # Get email with thread context
        GET /api/emails/msg-12345@mail.example.com/thread/

        # Order by date
        GET /api/emails/?ordering=-date_received
    """

    permission_classes = [IsAuthenticated]
    queryset = Email.objects.all()
    lookup_field = "message_id"

    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.

        - retrieve: Returns detailed serializer with full content
        - thread: Returns serializer with thread context
        - list/default: Returns list serializer (no body content)

        Returns:
            Serializer class appropriate for the current action
        """
        if self.action == "retrieve":
            return EmailDetailSerializer
        if self.action == "thread":
            return EmailThreadSerializer
        return EmailListSerializer

    def get_queryset(self):
        """
        Filter queryset to return only emails from user's accounts.

        Applies various filters based on query parameters:
        - folder: Filter by folder ID
        - is_read: Filter by read status
        - from_address: Filter by sender address ID
        - search: Search in subject and body text
        - ordering: Sort results

        Returns:
            Filtered and ordered QuerySet of Email objects
        """
        # Ensure user is authenticated
        assert isinstance(self.request.user.id, int)

        # Get all email accounts for this user
        user_accounts = EmailAccount.objects.filter(user=self.request.user)

        # Get all folders for these accounts
        user_folders = EmailFolder.objects.filter(account__in=user_accounts)

        # Base queryset: emails in user's folders
        queryset = self.queryset.filter(folder__in=user_folders)

        # Select related to optimize queries
        queryset = queryset.select_related(
            "from_address",
            "reply_to_address",
            "folder",
            "in_reply_to",
        ).prefetch_related("to_addresses")

        # Filter by folder if provided
        folder_id = self.request.GET.get("folder", None)
        if folder_id:
            queryset = queryset.filter(folder_id=folder_id)

        # Filter by read status if provided
        is_read = self.request.GET.get("is_read", None)
        if is_read is not None:
            is_read_bool = is_read.lower() in ["true", "1", "yes"]
            queryset = queryset.filter(is_read=is_read_bool)

        # Filter by sender address if provided
        from_address_id = self.request.GET.get("from_address", None)
        if from_address_id:
            queryset = queryset.filter(from_address_id=from_address_id)

        # Search in subject and body if provided
        search = self.request.GET.get("search", None)
        if search:
            queryset = queryset.filter(
                Q(subject__icontains=search)
                | Q(body_text__icontains=search)
                | Q(body_html__icontains=search),
            )

        # Apply ordering
        ordering = self.request.GET.get("ordering", "-date_received")
        valid_orderings = [
            "date_sent",
            "-date_sent",
            "date_received",
            "-date_received",
            "subject",
            "-subject",
        ]
        if ordering in valid_orderings:
            queryset = queryset.order_by(ordering)
        else:
            # Default ordering
            queryset = queryset.order_by("-date_received")

        # Apply limit if provided
        limit = self.request.GET.get("limit", None)
        if limit:
            try:
                limit_int = int(limit)
                offset = int(self.request.GET.get("offset", 0))
                queryset = queryset[offset : offset + limit_int]
            except ValueError:
                # Invalid limit/offset, ignore it
                pass

        return queryset

    @action(detail=True, methods=["get"])
    def thread(self, request, message_id=None):
        """
        Retrieve email with thread context (replies and parent email).

        This custom action returns an email with additional information
        about its position in a conversation thread.

        Args:
            request: The HTTP request object
            message_id: Message ID of the email

        Returns:
            Response with email data and thread context

        Example:
            GET /api/emails/msg-12345@mail.example.com/thread/

            Response includes:
            - Full email details
            - replies_count: Number of replies
            - has_replies: Boolean flag
            - in_reply_to: Parent email message_id (if applicable)

        Use Case:
            Use this endpoint when displaying an email in a threaded view
            to understand its conversation context.
        """
        email = self.get_object()
        serializer = EmailThreadSerializer(email, context={"request": request})
        return Response(serializer.data)


__all__ = ["EmailViewSet"]
