from __future__ import annotations

import os

from cryptography.fernet import Fernet
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

User = get_user_model()
cipher_suite = Fernet(os.environ.get("FERNET_KEY"))


class EmailAccount(models.Model):
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

    _content_type = models.ForeignKey[ContentType] = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("Content Type"),
        help_text=_("The content type of the email account."),
    )

    _configured_instance: EmailAccount = GenericForeignKey(
        "_content_type",
        "pk",
    )

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
        # Placeholder method to connect to the email server
        msg = "This method should be implemented to connect to the email server."
        raise NotImplementedError(msg)

    def retrieve_folders(self):
        # Placeholder method to retrieve folders from the email server
        msg = "This method should be implemented to retrieve folders from the email server."  # noqa: E501
        raise NotImplementedError(msg)

    def retrieve_emails(self):
        # Placeholder method to retrieve emails from the email server
        msg = "This method should be implemented to retrieve emails from the email server."  # noqa: E501
        raise NotImplementedError(msg)


class ExchangeEmailAccount(EmailAccount):
    server_address = models.CharField(
        max_length=255,
        null=False,
        verbose_name=_("Server Address"),
        help_text=_("The address of the Exchange server."),
    )
    username = models.CharField(
        max_length=255,
        null=False,
        verbose_name=_("Username"),
        help_text=_("The username for the Exchange account."),
    )
    email_address = models.EmailField(
        null=False,
        verbose_name=_("Email Address"),
        help_text=_("The email address associated with the Exchange account."),
    )
    password_encrypted = models.BinaryField(
        null=False,
        verbose_name=_("Encrypted Password"),
        help_text=_("The encrypted password for the Exchange account."),
        editable=False,
    )

    class Meta:
        verbose_name = _("Exchange Email Account")
        verbose_name_plural = _("Exchange Email Accounts")

    def __str__(self):
        return f"Exchange Account: {self.email_address} ({self.user})"

    @property
    def password(self) -> str:
        # Decrypt the password before returning it
        decrypted_password = cipher_suite.decrypt(self.password_encrypted)
        return decrypted_password.decode()

    @password.setter
    def password(self, raw_password: str):
        # Encrypt the password before storing it
        encrypted_password = cipher_suite.encrypt(raw_password.encode())
        self.password_encrypted = encrypted_password
        # Optionally, you can clear the raw password from memory
        raw_password = None


class EmailAddresses(models.Model):
    address = models.EmailField(
        null=False,
        unique=True,
        db_index=True,
    )

    class Meta:
        verbose_name = _("Email Address")
        verbose_name_plural = _("Email Addresses")

    def __str__(self):
        return self.address


class EmailFolder(models.Model):
    user: models.ForeignKey[User] = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        help_text=_("The user associated with this email folder."),
        editable=False,
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

    class Meta:
        verbose_name = _("Email Folder")
        verbose_name_plural = _("Email Folders")

    def __str__(self):
        return self.base_name


class Email(models.Model):
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

    class Meta:
        verbose_name = _("Email")
        verbose_name_plural = _("Emails")

    def __str__(self):
        return f"[{self.message_id}] {self.subject}"


class EmailPersonalization(models.Model):
    email: models.OneToOneField[Email] = models.OneToOneField(
        Email,
        on_delete=models.CASCADE,
        verbose_name=_("Email"),
        help_text=_("The email associated with this personalization."),
        editable=False,
    )

    tags = TaggableManager(
        blank=True,
        verbose_name=_("Tags"),
        help_text=_("Tags associated with this email."),
    )

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


class EmailFolderPersonalizations(models.Model):
    folder: models.OneToOneField[EmailFolder] = models.OneToOneField(
        EmailFolder,
        on_delete=models.CASCADE,
        verbose_name=_("Email Folder"),
        help_text=_("The email folder associated with this personalization."),
        editable=False,
    )

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
        blank=True,
        verbose_name=_("Tags"),
        help_text=_("Tags associated with this email folder."),
    )

    class Meta:
        verbose_name = _("Email Folder Personalization")
        verbose_name_plural = _("Email Folder Personalizations")

    def __str__(self):
        return f"Personalization for Folder [{self.folder}]"
