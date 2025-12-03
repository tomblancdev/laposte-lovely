from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

from .address import EmailAddresses
from .folder import EmailFolder

if TYPE_CHECKING:
    from .personalization import EmailPersonalization

__all__ = ["Email"]


class Email(models.Model):
    """
    Email model.

    Represents an email message.
    This model stores raw information about emails.
    """

    message_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        null=False,
        primary_key=True,
        verbose_name=_("Message ID"),
        help_text=_("The unique message ID of the email."),
    )
    json_data = models.JSONField(
        null=False,
        editable=False,
    )

    # addresses related to this email
    from_address: models.ForeignKey[EmailAddresses] = models.ForeignKey(
        EmailAddresses,
        on_delete=models.SET_NULL,
        related_name="emails_from",
        editable=False,
        null=True,
        verbose_name=_("From Address"),
        help_text=_("The email address of the sender."),
    )
    to_addresses = models.ManyToManyField(
        EmailAddresses,
        related_name="emails_to",
        editable=False,
        verbose_name=_("To Addresses"),
        help_text=_("The email addresses of the primary recipients."),
    )

    in_reply_to: models.ForeignKey[Email] = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replies",
        editable=False,
        verbose_name=_("In-Reply-To"),
        help_text=_("The email this message is replying to."),
    )

    date_received = models.DateTimeField(
        null=False,
        editable=False,
        verbose_name=_("Date Received"),
        help_text=_("The date and time the email was received."),
    )
    date_sent = models.DateTimeField(
        null=False,
        editable=False,
        verbose_name=_("Date Sent"),
        help_text=_("The date and time the email was sent."),
    )

    body_text = models.TextField(
        blank=True,
        editable=False,
        default="",
        verbose_name=_("Body Text"),
        help_text=_("The plain text body of the email."),
    )

    body_html = models.TextField(
        blank=True,
        editable=False,
        verbose_name=_("Body HTML"),
        help_text=_("The HTML body of the email."),
        default="",
    )

    reply_to_address: models.ForeignKey[EmailAddresses] = models.ForeignKey(
        EmailAddresses,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="emails_reply_to",
        editable=False,
        verbose_name=_("Reply-To Address"),
        help_text=_("The email address to reply to."),
    )

    is_read = models.BooleanField(
        default=False,
        editable=False,
        verbose_name=_("Is Read"),
        help_text=_("Whether the email has been read."),
    )
    folder: models.ForeignKey[EmailFolder] = models.ForeignKey(
        EmailFolder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="emails",
        editable=False,
        verbose_name=_("Folder"),
        help_text=_("The folder the email is stored in."),
    )
    priority = models.IntegerField(
        null=True,
        blank=True,
        editable=False,
        verbose_name=_("Priority"),
        help_text=_("The priority of the email."),
    )
    subject = models.CharField(
        max_length=255,
        null=False,
        editable=False,
        verbose_name=_("Subject"),
        help_text=_("The subject of the email."),
    )

    # Reverse relations
    replies: models.QuerySet[Email]
    personalization: EmailPersonalization | None

    class Meta:
        verbose_name = _("Email")
        verbose_name_plural = _("Emails")

    def __str__(self):
        return f"[{self.message_id}] {self.subject}"
