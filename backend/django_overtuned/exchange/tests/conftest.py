import pytest

from django_overtuned.exchange.models import ExchangeAccount
from django_overtuned.exchange.models import ExchangeEmailAccount
from django_overtuned.exchange.tests.factories import ExchangeAccountFactory
from django_overtuned.exchange.tests.factories import ExchangeEmailAccountFactory


@pytest.fixture
def exchange_account(db) -> ExchangeAccount:
    """Fixture for creating an ExchangeAccount instance."""
    return ExchangeAccountFactory()


@pytest.fixture
def exchange_email_account(db) -> ExchangeEmailAccount:
    """Fixture for creating an ExchangeEmailAccount instance."""
    return ExchangeEmailAccountFactory()
