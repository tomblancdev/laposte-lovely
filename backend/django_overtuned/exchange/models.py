from __future__ import annotations

import os
from typing import TYPE_CHECKING

from cryptography.fernet import Fernet
from django.db import models
from django.utils.translation import gettext_lazy as _
from exchangelib import DELEGATE
from exchangelib import Account
from exchangelib import Configuration
from exchangelib import Credentials

from django_overtuned.emails.models.account import EmailAccount
from django_overtuned.emails.models.folder import EmailFolder

if TYPE_CHECKING:
    from django_overtuned.emails.models.email import Email

cipher_suite = Fernet(os.environ.get("FERNET_KEY"))


class UnconnectedExchangeAccountError(ConnectionError):
    """
    Exception raised when an Exchange account is not connected.
    """

    message = _("The Exchange account is not connected.")
    code = "exchange_account_unconnected"
    status_code = 401
    details = _("Connect the Exchange account before performing this action.")


class ExchangeConnectionError(ConnectionError):
    """
    Exception raised when there is a connection error with the Exchange server.
    """

    message = _("Failed to connect to the Exchange server.")
    code = "exchange_connection_error"
    status_code = 503
    details = _("Please check the server address and your network connection.")


class ExchangeAccount(models.Model):
    """
    Represents an Exchange email account.
    """

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

    # Reverse relations
    email_account: ExchangeEmailAccount | None = None

    class Meta:
        verbose_name = _("Exchange Account")
        verbose_name_plural = _("Exchange Accounts")

    def __str__(self):
        return f"Exchange Account: {self.email_address} ({self.server_address})"

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

    def connect(self) -> bool:
        try:
            creds = Credentials(
                username=self.username,
                password=self.password,
            )
            config = Configuration(
                server=self.server_address,
                credentials=creds,
            )
            self._account = Account(
                access_type=DELEGATE,
                credentials=creds,
                config=config,
                autodiscover=False,
                primary_smtp_address=self.email_address,
            )
        except (ConnectionError, TimeoutError, ValueError, AttributeError):
            # Log the exception as needed
            return False
        else:
            return True

    def retrieve_folders(self, folder_type: str | None = None):
        """Retrieve folders from the Exchange account.
        Args:
            folder_type (str | None): The type of folders to retrieve. Can be "email", "calendar", or None for all folders.
        Returns:
            A list of folders from the Exchange account.
        """  # noqa: E501
        if not self.connect():
            raise UnconnectedExchangeAccountError
        # Retrieve only email folders from the Exchange account
        if folder_type == "email":
            return self._account.inbox.walk()
        if folder_type == "calendar":
            return self._account.calendar.walk()
        return self._account.root.walk()

    def retrieve_emails(self):
        """Retrieve emails from the Exchange account.
        Returns:
            A list of emails from the Exchange account.
        """
        if not self.connect():
            raise UnconnectedExchangeAccountError
        inbox = self._account.inbox
        return inbox.all()


class ExchangeEmailAccount(EmailAccount):
    """
    Represents an Exchange email account linked to a user.
    """

    exchange_account: models.ForeignKey[ExchangeAccount] = models.OneToOneField(
        ExchangeAccount,
        on_delete=models.CASCADE,
        verbose_name=_("Exchange Account"),
        help_text=_("The linked Exchange account."),
        editable=False,
        related_name="email_account",
    )

    class Meta:
        verbose_name = _("Exchange Email Account")
        verbose_name_plural = _("Exchange Email Accounts")

    def __str__(self):
        return f"Exchange Account: {self.exchange_account.email_address} ({self.user})"

    @property
    def account(self) -> ExchangeAccount:
        return self.exchange_account

    def connect(self) -> bool:
        return self.exchange_account.connect()

    def retrieve_folders(self) -> list[EmailFolder]:
        """
        Retrieve folders from Exchange and create/update EmailFolder instances.

        Returns:
            list[EmailFolder]: A list of EmailFolder model instances.
        """
        exchange_folders = self.exchange_account.retrieve_folders(folder_type="email")
        created_folders: list[EmailFolder] = []
        folder_map: dict[str, EmailFolder] = {}

        # First pass: Create or update all folders without parent relationships
        for exchange_folder in exchange_folders:
            folder_name = exchange_folder.name

            # Create or update the EmailFolder
            email_folder, _ = EmailFolder.objects.update_or_create(
                account=self,
                base_name=folder_name,
                defaults={
                    "parent": None,  # Will be set in second pass
                },
            )

            folder_map[folder_name] = email_folder
            created_folders.append(email_folder)

        # Second pass: Establish parent-child relationships
        for exchange_folder in exchange_folders:
            folder_name = exchange_folder.name
            email_folder = folder_map.get(folder_name)

            if email_folder and exchange_folder.parent:
                parent_name = exchange_folder.parent.name
                parent_folder = folder_map.get(parent_name)

                if parent_folder and email_folder.parent != parent_folder:
                    email_folder.parent = parent_folder
                    email_folder.save(update_fields=["parent"])

        return created_folders

    def retrieve_emails(self) -> list[Email]:
        return self.exchange_account.retrieve_emails()


__all__ = ["ExchangeAccount", "ExchangeEmailAccount"]
