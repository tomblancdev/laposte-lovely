from collections.abc import Sequence
from typing import Any

from django.utils import timezone
from factory import Faker
from factory import LazyAttribute
from factory import SubFactory
from factory import post_generation
from factory.django import DjangoModelFactory

from django_overtuned.emails.models import Email
from django_overtuned.emails.models import EmailAccount
from django_overtuned.emails.models import EmailAddresses
from django_overtuned.emails.models import EmailFolder
from django_overtuned.emails.models import EmailFolderPersonalization
from django_overtuned.emails.models import EmailPersonalization
from django_overtuned.users.tests.factories import UserFactory


class EmailAccountFactory(DjangoModelFactory[EmailAccount]):
    """Factory for creating EmailAccount instances."""

    user = SubFactory(UserFactory)
    name = Faker("company")

    class Meta:
        model = EmailAccount
        django_get_or_create = ["user"]


class EmailAddressesFactory(DjangoModelFactory[EmailAddresses]):
    """Factory for creating EmailAddresses instances."""

    address = Faker("email")

    class Meta:
        model = EmailAddresses
        django_get_or_create = ["address"]


class EmailFolderFactory(DjangoModelFactory[EmailFolder]):
    """Factory for creating EmailFolder instances."""

    account = SubFactory(EmailAccountFactory)
    base_name = Faker("word")
    parent = None

    class Meta:
        model = EmailFolder
        django_get_or_create = ["base_name"]


class EmailFactory(DjangoModelFactory[Email]):
    """Factory for creating Email instances."""

    message_id = Faker("uuid4")
    json_data = LazyAttribute(lambda obj: {})
    from_address = SubFactory(EmailAddressesFactory)
    date_received = LazyAttribute(lambda _: timezone.now())
    date_sent = LazyAttribute(lambda _: timezone.now())
    body_text = Faker("text")
    body_html = Faker("text")
    is_read = False
    folder = SubFactory(EmailFolderFactory)
    priority = 1
    subject = Faker("sentence", nb_words=6)

    @post_generation
    def to_addresses(self, create: bool, extracted: Sequence[Any], **kwargs):  # noqa: FBT001
        """Add to_addresses after email creation."""
        if not create:
            return

        if extracted:
            for address in extracted:
                self.to_addresses.add(address)
        else:
            # Add a default to_address
            self.to_addresses.add(EmailAddressesFactory())

    class Meta:
        model = Email
        django_get_or_create = ["message_id"]


class EmailPersonalizationFactory(DjangoModelFactory[EmailPersonalization]):
    """Factory for creating EmailPersonalization instances."""

    email = SubFactory(EmailFactory)
    notes = Faker("text", max_nb_chars=200)
    importance_level = Faker("random_int", min=1, max=5)

    class Meta:
        model = EmailPersonalization


class EmailFolderPersonalizationFactory(DjangoModelFactory[EmailFolderPersonalization]):
    """Factory for creating EmailFolderPersonalization instances."""

    folder = SubFactory(EmailFolderFactory)
    display_color = Faker("hex_color")
    display_name = Faker("word")

    class Meta:
        model = EmailFolderPersonalization
