"""
Email API Serializers

This module exports all serializers for the emails app.
Serializers are organized by model for better code organization.

Serializers Available:
    - EmailAccountSerializer: Basic account info
    - EmailAccountDetailSerializer: Account with statistics
    - EmailAddressesSerializer: Email address records
    - EmailAddressesDetailSerializer: Address with usage stats
    - EmailListSerializer: Lightweight email list view
    - EmailDetailSerializer: Full email details
    - EmailThreadSerializer: Email with thread context
    - EmailFolderSerializer: Basic folder info
    - EmailFolderTreeSerializer: Folder with nested subfolders
    - EmailFolderDetailSerializer: Folder with statistics
    - EmailPersonalizationSerializer: User metadata for emails
    - EmailFolderPersonalizationSerializer: User metadata for folders

Usage:
    from django_overtuned.emails.api.serializers import (
        EmailAccountSerializer,
        EmailDetailSerializer,
    )
"""

# Account serializers
from .account import EmailAccountDetailSerializer
from .account import EmailAccountSerializer

# Address serializers
from .address import EmailAddressesDetailSerializer
from .address import EmailAddressesSerializer

# Email serializers
from .email import EmailDetailSerializer
from .email import EmailListSerializer
from .email import EmailThreadSerializer

# Folder serializers
from .folder import EmailFolderDetailSerializer
from .folder import EmailFolderSerializer
from .folder import EmailFolderTreeSerializer

# Personalization serializers
from .personalization import EmailFolderPersonalizationSerializer
from .personalization import EmailPersonalizationSerializer

__all__ = [
    "EmailAccountDetailSerializer",
    "EmailAccountSerializer",
    "EmailAddressesDetailSerializer",
    "EmailAddressesSerializer",
    "EmailDetailSerializer",
    "EmailFolderDetailSerializer",
    "EmailFolderPersonalizationSerializer",
    "EmailFolderSerializer",
    "EmailFolderTreeSerializer",
    "EmailListSerializer",
    "EmailPersonalizationSerializer",
    "EmailThreadSerializer",
]
