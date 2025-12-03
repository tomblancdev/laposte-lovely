"""
Email models module.

This module contains all email-related models organized by functionality.
"""

from .account import EmailAccount
from .address import EmailAddresses
from .email import Email
from .folder import EmailFolder
from .personalization import EmailFolderPersonalization
from .personalization import EmailPersonalization

__all__ = [
    "Email",
    "EmailAccount",
    "EmailAddresses",
    "EmailFolder",
    "EmailFolderPersonalization",
    "EmailPersonalization",
]
