"""
Email API Views

This module exports all viewsets for the emails app.
ViewSets are organized by model for better code organization.

ViewSets Available:
    - EmailAccountViewSet: List/retrieve accounts, trigger sync
    - EmailAddressesViewSet: List/retrieve email addresses
    - EmailViewSet: List/retrieve emails with search and filtering
    - EmailFolderViewSet: List/retrieve folders, tree view
    - EmailPersonalizationViewSet: CRUD for email metadata
    - EmailFolderPersonalizationViewSet: CRUD for folder metadata

Usage:
    from django_overtuned.emails.api.views import (
        EmailAccountViewSet,
        EmailViewSet,
    )
"""

# Account views
from .account import EmailAccountViewSet

# Address views
from .address import EmailAddressesViewSet

# Email views
from .email import EmailViewSet

# Folder views
from .folder import EmailFolderViewSet

# Personalization views
from .personalization import EmailFolderPersonalizationViewSet
from .personalization import EmailPersonalizationViewSet

__all__ = [
    "EmailAccountViewSet",
    "EmailAddressesViewSet",
    "EmailFolderPersonalizationViewSet",
    "EmailFolderViewSet",
    "EmailPersonalizationViewSet",
    "EmailViewSet",
]
