from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from .account import EmailAccount

if TYPE_CHECKING:
    from .email import Email
    from .personalization import EmailFolderPersonalization

User = get_user_model()

__all__ = ["EmailFolder"]


class EmailFolder(models.Model):
    """
    Email folder model.

    This model is used to keep raw information about email folders.
    """

    account: models.ForeignKey[User] = models.ForeignKey(
        EmailAccount,
        on_delete=models.CASCADE,
        verbose_name=_("Email Account"),
        help_text=_("The email account associated with this folder."),
        editable=False,
        related_name="email_folders",
    )

    base_name = models.CharField(
        max_length=255,
        null=False,
        unique=True,
        db_index=True,
        editable=False,
    )
    parent: models.ForeignKey[EmailFolder] = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subfolders",
        editable=False,
    )

    # Reverse relations
    subfolders: models.QuerySet[EmailFolder]
    emails: models.QuerySet[Email]
    personalization: EmailFolderPersonalization | None

    class Meta:
        verbose_name = _("Email Folder")
        verbose_name_plural = _("Email Folders")

    def __str__(self):
        return self.base_name
