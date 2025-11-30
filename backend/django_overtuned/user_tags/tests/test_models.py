from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.db import IntegrityError

from django_overtuned.users.tests.factories import UserFactory

from .factories import UserTagFactory
from .factories import UserTaggedItemFactory

if TYPE_CHECKING:
    from django_overtuned.users.models import User

# Import models conditionally - skip tests if taggit not installed
try:
    from django_overtuned.user_tags.models import UserTag
    from django_overtuned.user_tags.models import UserTaggedItem
except ImportError:
    pytest.skip("django-taggit not installed", allow_module_level=True)


@pytest.mark.django_db
class TestUserTag:
    def test_user_tag_unique_per_user(self, user: User):
        """Two tags with the same name for the same user should be disallowed."""
        UserTag.objects.create(name="duplicate", user=user)
        with pytest.raises(IntegrityError):
            UserTag.objects.create(name="duplicate", user=user)

    def test_same_tag_name_different_users(self, user: User):
        """Different users may have tags with the same name."""
        user2 = UserFactory()
        tag1 = UserTagFactory(name="shared", user=user)
        tag2 = UserTagFactory(name="shared", user=user2)

        assert tag1.name == tag2.name
        assert tag1.user_id != tag2.user_id

    def test_user_tag_str(self, user: User):
        """UserTag string representation should return the tag name."""
        tag = UserTagFactory(name="testtag", user=user)
        assert str(tag) == "testtag"

    def test_user_relationship(self, user: User):
        """UserTag should have a proper foreign key relationship with User."""
        tag = UserTagFactory(user=user)
        assert tag.user == user
        assert tag in user.tags.all()


@pytest.mark.django_db
class TestUserTaggedItem:
    def test_user_tagged_item_links_object(self, user: User):
        """UserTaggedItem links tag to content object via GenericForeignKey."""
        tag = UserTagFactory(user=user)
        target_user = UserFactory()
        uti = UserTaggedItemFactory(tag=tag, content_object=target_user)

        assert uti.tag == tag
        assert uti.content_object == target_user
        assert uti in tag.tagged_items.all()

    def test_tagged_item_cascade_delete(self, user: User):
        """When a tag is deleted, its tagged items should also be deleted."""
        tag = UserTagFactory(user=user)
        uti = UserTaggedItemFactory(tag=tag, content_object=user)
        uti_id = uti.id

        tag.delete()

        assert not UserTaggedItem.objects.filter(id=uti_id).exists()
