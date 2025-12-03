"""
Email API Module

This module provides a complete REST API for the emails app.
It includes serializers and viewsets for all email-related models.

Architecture:
    The API is organized following Django REST Framework best practices:

    - serializers/: Contains serializer classes organized by model
    - views/: Contains viewset classes organized by model

    Each model has its own file with related serializers/viewsets,
    making the codebase maintainable and easy to navigate.

Models Covered:
    1. EmailAccount: User's email accounts (Gmail, Outlook, etc.)
    2. EmailAddresses: Email address records (from, to, reply-to)
    3. Email: Individual email messages with content
    4. EmailFolder: Hierarchical folder structure
    5. EmailPersonalization: User-specific email metadata (tags, notes)
    6. EmailFolderPersonalization: User-specific folder metadata (colors, names)

Usage:
    # Import serializers
    from django_overtuned.emails.api import (
        EmailAccountSerializer,
        EmailDetailSerializer,
    )

    # Import viewsets
    from django_overtuned.emails.api import (
        EmailAccountViewSet,
        EmailViewSet,
    )

    # Or import from submodules
    from django_overtuned.emails.api.serializers import EmailListSerializer
    from django_overtuned.emails.api.views import EmailFolderViewSet

Router Configuration:
    To register these viewsets with Django REST Framework router:

    from rest_framework.routers import DefaultRouter
    from django_overtuned.emails.api import (
        EmailAccountViewSet,
        EmailAddressesViewSet,
        EmailViewSet,
        EmailFolderViewSet,
        EmailPersonalizationViewSet,
        EmailFolderPersonalizationViewSet,
    )

    router = DefaultRouter()
    router.register(r'email-accounts', EmailAccountViewSet, basename='emailaccount')
    router.register(r'email-addresses', EmailAddressesViewSet, basename='emailaddresses')
    router.register(r'emails', EmailViewSet, basename='email')
    router.register(r'email-folders', EmailFolderViewSet, basename='emailfolder')
    router.register(r'email-personalizations', EmailPersonalizationViewSet, basename='emailpersonalization')
    router.register(r'email-folder-personalizations', EmailFolderPersonalizationViewSet, basename='emailfolderpersonalization')

API Endpoints Overview:

    Email Accounts:
        GET    /api/email-accounts/              - List accounts
        GET    /api/email-accounts/{id}/          - Retrieve account details
        POST   /api/email-accounts/{id}/sync/     - Trigger sync

    Email Addresses:
        GET    /api/email-addresses/              - List addresses
        GET    /api/email-addresses/{id}/         - Retrieve address details

    Emails:
        GET    /api/emails/                       - List emails
        GET    /api/emails/{message_id}/          - Retrieve email details
        GET    /api/emails/{message_id}/thread/   - Get email with thread context

    Email Folders:
        GET    /api/email-folders/                - List folders
        GET    /api/email-folders/{id}/           - Retrieve folder details
        GET    /api/email-folders/tree/           - Get hierarchical tree
        GET    /api/email-folders/{id}/subfolders/ - Get subfolders

    Email Personalizations:
        GET    /api/email-personalizations/       - List personalizations
        POST   /api/email-personalizations/       - Create personalization
        GET    /api/email-personalizations/{id}/  - Retrieve details
        PUT    /api/email-personalizations/{id}/  - Update personalization
        PATCH  /api/email-personalizations/{id}/  - Partial update
        DELETE /api/email-personalizations/{id}/  - Delete personalization

    Email Folder Personalizations:
        GET    /api/email-folder-personalizations/       - List personalizations
        POST   /api/email-folder-personalizations/       - Create personalization
        GET    /api/email-folder-personalizations/{id}/  - Retrieve details
        PUT    /api/email-folder-personalizations/{id}/  - Update personalization
        PATCH  /api/email-folder-personalizations/{id}/  - Partial update
        DELETE /api/email-folder-personalizations/{id}/  - Delete personalization

Permission Model:
    All endpoints require authentication. Users can only access their own data:
    - Email accounts they own
    - Emails in their accounts
    - Folders in their accounts
    - Their own personalizations

    This is enforced at the queryset level in each viewset's get_queryset() method.

Query Features:
    Most list endpoints support:
    - Filtering by related objects
    - Search in text fields
    - Ordering by multiple fields
    - Pagination (limit/offset)

    See individual viewset docstrings for specific query parameters.
"""  # noqa: E501

# Import all serializers
from .serializers import EmailAccountDetailSerializer
from .serializers import EmailAccountSerializer
from .serializers import EmailAddressesDetailSerializer
from .serializers import EmailAddressesSerializer
from .serializers import EmailDetailSerializer
from .serializers import EmailFolderDetailSerializer
from .serializers import EmailFolderPersonalizationSerializer
from .serializers import EmailFolderSerializer
from .serializers import EmailFolderTreeSerializer
from .serializers import EmailListSerializer
from .serializers import EmailPersonalizationSerializer
from .serializers import EmailThreadSerializer

# Import all viewsets
from .views import EmailAccountViewSet
from .views import EmailAddressesViewSet
from .views import EmailFolderPersonalizationViewSet
from .views import EmailFolderViewSet
from .views import EmailPersonalizationViewSet
from .views import EmailViewSet

__all__ = [
    "EmailAccountDetailSerializer",
    "EmailAccountSerializer",
    "EmailAccountViewSet",
    "EmailAddressesDetailSerializer",
    "EmailAddressesSerializer",
    "EmailAddressesViewSet",
    "EmailDetailSerializer",
    "EmailFolderDetailSerializer",
    "EmailFolderPersonalizationSerializer",
    "EmailFolderPersonalizationViewSet",
    "EmailFolderSerializer",
    "EmailFolderTreeSerializer",
    "EmailFolderViewSet",
    "EmailListSerializer",
    "EmailPersonalizationSerializer",
    "EmailPersonalizationViewSet",
    "EmailThreadSerializer",
    "EmailViewSet",
]
