from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from django_overtuned.emails.models import Email
    from django_overtuned.emails.models import EmailFolder

User = get_user_model()


class EmailAccount(models.Model):
    """
    Represents an email account associated with a user.

    This is a base class for different types of email accounts.
    """

    user: models.OneToOneField[User] = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        help_text=_("The user associated with this email account."),
    )

    name = models.CharField(
        max_length=255,
        null=False,
        verbose_name=_("Account Name"),
        help_text=_("The name of the email account."),
    )

    _content_type: models.ForeignKey[ContentType] = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("Content Type"),
        help_text=_("The content type of the email account."),
    )

    _configured_instance: EmailAccount = GenericForeignKey(
        "_content_type",
        "id",
    )

    email_folders: models.Manager[EmailFolder]

    class Meta:
        verbose_name = _("Email Account")
        verbose_name_plural = _("Email Accounts")

    def __str__(self):
        return f"{self.name} ({self.user})"

    def save(
        self,
        *,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        if not self.pk:
            # On creation, set the content type based on the model class
            self._content_type = ContentType.objects.get_for_model(self)

        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    def connect(self) -> bool:
        """
        Connect to the email server.
        Returns:
            bool: True if the connection was successful, False otherwise.
        """
        # Placeholder method to connect to the email server
        msg = "This method should be implemented to connect to the email server."
        raise NotImplementedError(msg)

    def retrieve_folders(self) -> list[EmailFolder]:
        """
        Retrieve folders from the email server.
        Returns:
            list[EmailFolder]: A list of folders from the email server.
        """
        # Placeholder method to retrieve folders from the email server
        msg = "This method should be implemented to retrieve folders from the email server."  # noqa: E501
        raise NotImplementedError(msg)

    def retrieve_emails(self) -> list[Email]:
        """
        Retrieve emails from the email server.
        Returns:
            list[Email]: A list of emails from the email server.
        """
        # Placeholder method to retrieve emails from the email server
        msg = "This method should be implemented to retrieve emails from the email server."  # noqa: E501
        raise NotImplementedError(msg)
