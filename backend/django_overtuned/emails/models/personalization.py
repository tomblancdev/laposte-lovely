from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

from django_overtuned.user_tags.models import UserTaggedItem

from .email import Email
from .folder import EmailFolder

User = get_user_model()

__all__ = ["EmailFolderPersonalization", "EmailPersonalization"]


class EmailPersonalization(models.Model):
    """
    Personalization settings for an email.

    Allows users to set personal tags, notes, and importance levels for individual emails.
    """  # noqa: E501

    email: models.OneToOneField[Email] = models.OneToOneField(
        Email,
        on_delete=models.CASCADE,
        verbose_name=_("Email"),
        help_text=_("The email associated with this personalization."),
        editable=False,
        related_name="personalization",
    )

    tags = TaggableManager(
        through=UserTaggedItem,
        blank=True,
        verbose_name=_("Tags"),
        help_text=_("Tags associated with this email."),
    )

    def get_user(self):
        """Get the user from the email's folder's account."""
        if self.email.folder and self.email.folder.account:
            return self.email.folder.account.user
        return None

    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes"),
        help_text=_("Personal notes about this email."),
        default="",
    )
    importance_level = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("Importance Level"),
        help_text=_("Personal importance level of this email."),
    )

    def __str__(self):
        return f"Personalization for Email [{self.email}]"


class EmailFolderPersonalization(models.Model):
    """
    Personalization settings for an email folder.

    Allows users to set personal tags, notes, and importance levels for individual email folders.

    """  # noqa: E501

    folder: models.OneToOneField[EmailFolder] = models.OneToOneField(
        EmailFolder,
        on_delete=models.CASCADE,
        verbose_name=_("Email Folder"),
        help_text=_("The email folder associated with this personalization."),
        editable=False,
        related_name="personalization",
    )

    def get_user(self):
        """Get the user from the folder's account."""
        if self.folder and self.folder.account:
            return self.folder.account.user
        return None

    display_color = models.CharField(
        max_length=7,
        blank=True,
        verbose_name=_("Display Color"),
        help_text=_("The display color for this email folder in HEX format."),
        default="",
    )

    display_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Display Name"),
        help_text=_("The display name for this email folder."),
        default="",
    )

    tags = TaggableManager(
        through=UserTaggedItem,
        blank=True,
        verbose_name=_("Tags"),
        help_text=_("Tags associated with this email folder."),
    )

    class Meta:
        verbose_name = _("Email Folder Personalization")
        verbose_name_plural = _("Email Folder Personalizations")

    def __str__(self):
        return f"Personalization for Folder [{self.folder}]"
