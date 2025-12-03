from unittest.mock import Mock
from unittest.mock import patch

import pytest

from django_overtuned.emails.models import EmailFolder
from django_overtuned.exchange.models import ExchangeAccount
from django_overtuned.exchange.models import ExchangeConnectionError
from django_overtuned.exchange.models import ExchangeEmailAccount
from django_overtuned.exchange.models import UnconnectedExchangeAccountError
from django_overtuned.exchange.tests.factories import ExchangeAccountFactory
from django_overtuned.exchange.tests.factories import ExchangeEmailAccountFactory
from django_overtuned.users.tests.factories import UserFactory


class TestExchangeAccount:
    """Test suite for ExchangeAccount model."""

    def test_str_method(self, exchange_account: ExchangeAccount):
        """Test string representation of ExchangeAccount."""
        expected = f"Exchange Account: {exchange_account.email_address} ({exchange_account.server_address})"  # noqa: E501
        assert str(exchange_account) == expected

    def test_server_address_field(self, exchange_account: ExchangeAccount):
        """Test server_address field."""
        assert exchange_account.server_address
        assert len(exchange_account.server_address) <= 255  # noqa: PLR2004

    def test_username_field(self, exchange_account: ExchangeAccount):
        """Test username field."""
        assert exchange_account.username
        assert len(exchange_account.username) <= 255  # noqa: PLR2004

    def test_email_address_field(self, exchange_account: ExchangeAccount):
        """Test email_address field."""
        assert exchange_account.email_address
        assert "@" in exchange_account.email_address

    def test_password_encryption(self, db):
        """Test that password is encrypted when stored."""
        account = ExchangeAccountFactory()
        raw_password = "test_password_123"  # noqa: S105
        account.password = raw_password
        account.save()

        # Refresh from database
        account.refresh_from_db()

        # Check that password_encrypted is binary and not the raw password
        assert isinstance(account.password_encrypted, bytes)
        assert account.password_encrypted != raw_password.encode()

    def test_password_decryption(self, db):
        """Test that password is correctly decrypted."""
        account = ExchangeAccountFactory()
        raw_password = "my_secure_password_456"  # noqa: S105
        account.password = raw_password
        account.save()

        # Refresh from database
        account.refresh_from_db()

        # Check that decrypted password matches original
        assert account.password == raw_password

    def test_password_property_getter(self, exchange_account: ExchangeAccount):
        """Test password property getter returns decrypted password."""
        decrypted = exchange_account.password
        assert isinstance(decrypted, str)
        assert len(decrypted) > 0

    def test_password_property_setter(self, db):
        """Test password property setter encrypts password."""
        account = ExchangeAccountFactory()
        new_password = "new_password_789"  # noqa: S105

        account.password = new_password
        account.save()
        account.refresh_from_db()

        assert account.password == new_password
        assert account.password_encrypted != new_password.encode()

    @patch("django_overtuned.exchange.models.Account")
    @patch("django_overtuned.exchange.models.Configuration")
    @patch("django_overtuned.exchange.models.Credentials")
    def test_connect_success(
        self,
        mock_creds,
        mock_config,
        mock_account,
        exchange_account,
    ):
        """Test successful connection to Exchange server."""
        mock_creds.return_value = Mock()
        mock_config.return_value = Mock()
        mock_account.return_value = Mock()

        result = exchange_account.connect()

        assert result is True
        mock_creds.assert_called_once_with(
            username=exchange_account.username,
            password=exchange_account.password,
        )

    @patch("django_overtuned.exchange.models.Credentials")
    def test_connect_failure(self, mock_creds, exchange_account):
        """Test connection failure to Exchange server."""
        mock_creds.side_effect = ConnectionError("Connection failed")

        result = exchange_account.connect()

        assert result is False

    @patch("django_overtuned.exchange.models.Credentials")
    def test_connect_timeout(self, mock_creds, exchange_account):
        """Test connection timeout to Exchange server."""
        mock_creds.side_effect = TimeoutError("Connection timeout")

        result = exchange_account.connect()

        assert result is False

    @patch.object(ExchangeAccount, "connect")
    def test_retrieve_folders_not_connected(self, mock_connect, exchange_account):
        """Test retrieve_folders raises error when not connected."""
        mock_connect.return_value = False

        with pytest.raises(UnconnectedExchangeAccountError):
            exchange_account.retrieve_folders()

    @patch.object(ExchangeAccount, "connect")
    def test_retrieve_folders_email_type(self, mock_connect, exchange_account):
        """Test retrieve_folders with email folder_type."""
        mock_connect.return_value = True
        mock_inbox = Mock()
        mock_inbox.walk.return_value = ["folder1", "folder2"]
        exchange_account._account = Mock(inbox=mock_inbox)  # noqa: SLF001

        result = exchange_account.retrieve_folders(folder_type="email")

        assert result == ["folder1", "folder2"]
        mock_inbox.walk.assert_called_once()

    @patch.object(ExchangeAccount, "connect")
    def test_retrieve_folders_calendar_type(self, mock_connect, exchange_account):
        """Test retrieve_folders with calendar folder_type."""
        mock_connect.return_value = True
        mock_calendar = Mock()
        mock_calendar.walk.return_value = ["cal1", "cal2"]
        exchange_account._account = Mock(calendar=mock_calendar)  # noqa: SLF001

        result = exchange_account.retrieve_folders(folder_type="calendar")

        assert result == ["cal1", "cal2"]
        mock_calendar.walk.assert_called_once()

    @patch.object(ExchangeAccount, "connect")
    def test_retrieve_folders_all_types(self, mock_connect, exchange_account):
        """Test retrieve_folders with no folder_type (all folders)."""
        mock_connect.return_value = True
        mock_root = Mock()
        mock_root.walk.return_value = ["all_folder1", "all_folder2"]
        exchange_account._account = Mock(root=mock_root)  # noqa: SLF001

        result = exchange_account.retrieve_folders()

        assert result == ["all_folder1", "all_folder2"]
        mock_root.walk.assert_called_once()

    @patch.object(ExchangeAccount, "connect")
    def test_retrieve_emails_not_connected(self, mock_connect, exchange_account):
        """Test retrieve_emails raises error when not connected."""
        mock_connect.return_value = False

        with pytest.raises(UnconnectedExchangeAccountError):
            exchange_account.retrieve_emails()

    @patch.object(ExchangeAccount, "connect")
    def test_retrieve_emails_success(self, mock_connect, exchange_account):
        """Test successful email retrieval."""
        mock_connect.return_value = True
        mock_inbox = Mock()
        mock_emails = ["email1", "email2", "email3"]
        mock_inbox.all.return_value = mock_emails
        exchange_account._account = Mock(inbox=mock_inbox)  # noqa: SLF001

        result = exchange_account.retrieve_emails()

        assert result == mock_emails
        mock_inbox.all.assert_called_once()

    def test_reverse_relation_email_account(self, db):
        """Test reverse relation to ExchangeEmailAccount."""
        exchange_account = ExchangeAccountFactory()
        email_account = ExchangeEmailAccountFactory(exchange_account=exchange_account)

        assert exchange_account.email_account == email_account


class TestExchangeEmailAccount:
    """Test suite for ExchangeEmailAccount model."""

    def test_str_method(self, exchange_email_account: ExchangeEmailAccount):
        """Test string representation of ExchangeEmailAccount."""
        expected = f"Exchange Account: {exchange_email_account.exchange_account.email_address} ({exchange_email_account.user})"  # noqa: E501
        assert str(exchange_email_account) == expected

    def test_user_relationship(self, exchange_email_account: ExchangeEmailAccount):
        """Test user relationship."""
        assert exchange_email_account.user is not None
        from django_overtuned.users.models import User

        assert isinstance(exchange_email_account.user, User)

    def test_exchange_account_relationship(
        self,
        exchange_email_account: ExchangeEmailAccount,
    ):
        """Test exchange_account relationship."""
        assert exchange_email_account.exchange_account is not None
        assert isinstance(exchange_email_account.exchange_account, ExchangeAccount)

    def test_one_to_one_with_user(self, db):
        """Test one-to-one relationship with user."""
        user = UserFactory()
        account1 = ExchangeEmailAccountFactory(user=user)

        # django_get_or_create should return the same account
        account2 = ExchangeEmailAccountFactory(user=user)

        assert account1.pk == account2.pk

    def test_account_property(self, exchange_email_account: ExchangeEmailAccount):
        """Test account property returns exchange_account."""
        assert exchange_email_account.account == exchange_email_account.exchange_account

    @patch.object(ExchangeAccount, "connect")
    def test_connect_delegates_to_exchange_account(
        self,
        mock_connect,
        exchange_email_account,
    ):
        """Test connect method delegates to exchange_account."""
        mock_connect.return_value = True

        result = exchange_email_account.connect()

        assert result is True
        mock_connect.assert_called_once()

    @patch.object(ExchangeAccount, "retrieve_folders")
    @patch.object(ExchangeAccount, "connect")
    def test_retrieve_folders_creates_email_folders(
        self,
        mock_connect,
        mock_retrieve,
        exchange_email_account,
    ):
        """Test retrieve_folders creates EmailFolder instances."""
        mock_connect.return_value = True

        # Create mock Exchange folders
        mock_folder1 = Mock()
        mock_folder1.name = "Inbox"
        mock_folder1.parent = None

        mock_folder2 = Mock()
        mock_folder2.name = "Sent Items"
        mock_folder2.parent = None

        mock_retrieve.return_value = [mock_folder1, mock_folder2]

        result = exchange_email_account.retrieve_folders()

        assert len(result) == 2  # noqa: PLR2004
        assert all(isinstance(folder, EmailFolder) for folder in result)

        # Check that folders were created in database
        assert EmailFolder.objects.filter(account=exchange_email_account).count() == 2  # noqa: PLR2004

    @patch.object(ExchangeAccount, "retrieve_folders")
    @patch.object(ExchangeAccount, "connect")
    def test_retrieve_folders_with_parent_child(
        self,
        mock_connect,
        mock_retrieve,
        exchange_email_account,
    ):
        """Test retrieve_folders handles parent-child relationships."""
        mock_connect.return_value = True

        # Create mock parent folder
        mock_parent = Mock()
        mock_parent.name = "Inbox"
        mock_parent.parent = None

        # Create mock child folder
        mock_child = Mock()
        mock_child.name = "Subfolder"
        mock_child.parent = mock_parent

        mock_retrieve.return_value = [mock_parent, mock_child]

        result = exchange_email_account.retrieve_folders()

        assert len(result) == 2  # noqa: PLR2004

        # Get the folders from database
        parent_folder = EmailFolder.objects.get(
            account=exchange_email_account,
            base_name="Inbox",
        )
        child_folder = EmailFolder.objects.get(
            account=exchange_email_account,
            base_name="Subfolder",
        )

        assert child_folder.parent == parent_folder

    @patch.object(ExchangeAccount, "retrieve_folders")
    @patch.object(ExchangeAccount, "connect")
    def test_retrieve_folders_updates_existing(
        self,
        mock_connect,
        mock_retrieve,
        exchange_email_account,
    ):
        """Test retrieve_folders updates existing folders."""
        mock_connect.return_value = True

        # Create an existing folder
        existing_folder = EmailFolder.objects.create(
            account=exchange_email_account,
            base_name="Inbox",
        )

        mock_folder = Mock()
        mock_folder.name = "Inbox"
        mock_folder.parent = None

        mock_retrieve.return_value = [mock_folder]

        result = exchange_email_account.retrieve_folders()

        # Should still be only one folder
        assert EmailFolder.objects.filter(account=exchange_email_account).count() == 1
        assert len(result) == 1

        # Folder ID should remain the same
        assert result[0].pk == existing_folder.pk

    @patch.object(ExchangeAccount, "retrieve_emails")
    def test_retrieve_emails_delegates_to_exchange_account(
        self,
        mock_retrieve,
        exchange_email_account,
    ):
        """Test retrieve_emails delegates to exchange_account."""
        mock_emails = ["email1", "email2"]
        mock_retrieve.return_value = mock_emails

        result = exchange_email_account.retrieve_emails()

        assert result == mock_emails
        mock_retrieve.assert_called_once()

    def test_name_field(self, exchange_email_account: ExchangeEmailAccount):
        """Test name field is inherited from EmailAccount."""
        assert exchange_email_account.name
        assert len(exchange_email_account.name) <= 255  # noqa: PLR2004

    def test_inherits_from_email_account(self, exchange_email_account):
        """Test that ExchangeEmailAccount inherits from EmailAccount."""
        from django_overtuned.emails.models import EmailAccount

        assert isinstance(exchange_email_account, EmailAccount)


class TestExchangeExceptions:
    """Test suite for Exchange exception classes."""

    def test_unconnected_exchange_account_error(self):
        """Test UnconnectedExchangeAccountError attributes."""
        error = UnconnectedExchangeAccountError()
        assert hasattr(error, "message")
        assert hasattr(error, "code")
        assert hasattr(error, "status_code")
        assert hasattr(error, "details")
        assert error.status_code == 401  # noqa: PLR2004
        assert error.code == "exchange_account_unconnected"

    def test_exchange_connection_error(self):
        """Test ExchangeConnectionError attributes."""
        error = ExchangeConnectionError()
        assert hasattr(error, "message")
        assert hasattr(error, "code")
        assert hasattr(error, "status_code")
        assert hasattr(error, "details")
        assert error.status_code == 503  # noqa: PLR2004
        assert error.code == "exchange_connection_error"
