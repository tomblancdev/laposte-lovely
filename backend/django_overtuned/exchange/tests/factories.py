import os

from factory import Faker
from factory import LazyAttribute
from factory import SubFactory
from factory.django import DjangoModelFactory

from django_overtuned.emails.tests.factories import EmailAccountFactory
from django_overtuned.exchange.models import ExchangeAccount
from django_overtuned.exchange.models import ExchangeEmailAccount
from django_overtuned.users.tests.factories import UserFactory


class ExchangeAccountFactory(DjangoModelFactory[ExchangeAccount]):
    """Factory for creating ExchangeAccount instances."""

    server_address = Faker("url")
    username = Faker("user_name")
    email_address = Faker("email")
    password = "test_password_123"

    class Meta:
        model = ExchangeAccount


class ExchangeEmailAccountFactory(DjangoModelFactory[ExchangeEmailAccount]):
    """Factory for creating ExchangeEmailAccount instances."""

    user = SubFactory(UserFactory)
    name = Faker("company")
    exchange_account = SubFactory(ExchangeAccountFactory)

    class Meta:
        model = ExchangeEmailAccount
        django_get_or_create = ["user"]
