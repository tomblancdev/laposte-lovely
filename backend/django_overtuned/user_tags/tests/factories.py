from __future__ import annotations

import pytest
from factory import Faker
from factory import SubFactory
from factory.django import DjangoModelFactory

from django_overtuned.users.tests.factories import UserFactory

# Import models conditionally - skip tests if taggit not installed
try:
    from django_overtuned.user_tags.models import UserTag
    from django_overtuned.user_tags.models import UserTaggedItem

    class UserTagFactory(DjangoModelFactory[UserTag]):
        name = Faker("word")
        user = SubFactory(UserFactory)

        class Meta:
            model = UserTag
            django_get_or_create = ["name", "user"]

    class UserTaggedItemFactory(DjangoModelFactory[UserTaggedItem]):
        tag = SubFactory(UserTagFactory)

        class Meta:
            model = UserTaggedItem

except ImportError:
    pytest.skip("django-taggit not installed", allow_module_level=True)
