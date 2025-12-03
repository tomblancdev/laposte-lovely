import pytest
from rest_framework.test import APIClient

from django_overtuned.emails.models import Email
from django_overtuned.emails.models import EmailAccount
from django_overtuned.emails.models import EmailAddresses
from django_overtuned.emails.models import EmailFolder
from django_overtuned.emails.models import EmailFolderPersonalization
from django_overtuned.emails.models import EmailPersonalization
from django_overtuned.emails.tests.factories import EmailAccountFactory
from django_overtuned.emails.tests.factories import EmailAddressesFactory
from django_overtuned.emails.tests.factories import EmailFactory
from django_overtuned.emails.tests.factories import EmailFolderFactory
from django_overtuned.emails.tests.factories import EmailFolderPersonalizationFactory
from django_overtuned.emails.tests.factories import EmailPersonalizationFactory
from django_overtuned.users.models import User
from django_overtuned.users.tests.factories import UserFactory


@pytest.fixture
def email_account(db) -> EmailAccount:
    """Fixture for creating an EmailAccount instance."""
    return EmailAccountFactory()


@pytest.fixture
def email_address(db) -> EmailAddresses:
    """Fixture for creating an EmailAddresses instance."""
    return EmailAddressesFactory()


@pytest.fixture
def email_folder(db, email_account) -> EmailFolder:
    """Fixture for creating an EmailFolder instance."""
    return EmailFolderFactory(account=email_account)


@pytest.fixture
def email(db, email_address, email_folder) -> Email:
    """Fixture for creating an Email instance."""
    return EmailFactory(from_address=email_address, folder=email_folder)


@pytest.fixture
def email_personalization(db, email) -> EmailPersonalization:
    """Fixture for creating an EmailPersonalization instance."""
    return EmailPersonalizationFactory(email=email)


@pytest.fixture
def email_folder_personalization(db, email_folder) -> EmailFolderPersonalization:
    """Fixture for creating an EmailFolderPersonalization instance."""
    return EmailFolderPersonalizationFactory(folder=email_folder)


# API Test Fixtures


@pytest.fixture
def user(db) -> User:
    """Fixture for creating a test user."""
    return UserFactory()


@pytest.fixture
def api_client_authenticated(user) -> APIClient:
    """Fixture for creating an authenticated API client."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client
