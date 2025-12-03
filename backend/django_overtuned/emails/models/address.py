from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from .email import Email

__all__ = ["EmailAddresses"]


class EmailAddresses(models.Model):
    """
    Email address model.
    """

    address = models.EmailField(
        null=False,
        unique=True,
        db_index=True,
    )

    # Reverse relations
    emails_from: models.Manager[Email]
    emails_to: models.Manager[Email]
    emails_reply_to: models.Manager[Email]

    class Meta:
        verbose_name = _("Email Address")
        verbose_name_plural = _("Email Addresses")

    def __str__(self):
        return self.address
