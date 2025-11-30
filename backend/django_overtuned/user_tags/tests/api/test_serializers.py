import pytest
from rest_framework.exceptions import ValidationError

from django_overtuned.user_tags.api.serializers import UserTagListSerializerField
from django_overtuned.user_tags.api.serializers import UserTagSerializer
from django_overtuned.user_tags.tests.factories import UserTagFactory
from django_overtuned.users.models import User


class TestUserTagSerializer:
    def test_serializer_fields(self, user: User):
        """Test that the serializer includes the correct fields."""
        tag = UserTagFactory(user=user, name="test")

        serializer = UserTagSerializer(tag)

        assert "id" in serializer.data
        assert "name" in serializer.data
        assert "slug" in serializer.data
        assert serializer.data["name"] == "test"

    def test_read_only_fields(self, user: User):
        """Test that id and slug are read-only."""
        tag = UserTagFactory(user=user, name="test")

        serializer = UserTagSerializer(tag)

        # These fields should be in read_only_fields
        assert "id" in serializer.Meta.read_only_fields
        assert "slug" in serializer.Meta.read_only_fields


class TestUserTagListSerializerField:
    def test_to_representation(self):
        """Test converting tags to list of names."""
        field = UserTagListSerializerField()

        # Mock a TaggableManager-like object
        class MockTag:
            def __init__(self, name):
                self.name = name

        class MockTagManager:
            def all(self):
                return [MockTag("tag1"), MockTag("tag2"), MockTag("tag3")]

        tags = MockTagManager()
        result = field.to_representation(tags)

        assert result == ["tag1", "tag2", "tag3"]

    def test_to_representation_empty(self):
        """Test converting empty tags."""
        field = UserTagListSerializerField()

        # Mock an empty TaggableManager-like object
        class MockTagManager:
            def all(self):
                return []

        tags = MockTagManager()
        result = field.to_representation(tags)

        assert result == []

    def test_to_internal_value_valid(self):
        """Test validating valid tag list."""
        field = UserTagListSerializerField()

        data = ["tag1", "tag2", "tag3"]
        result = field.to_internal_value(data)

        assert result == data

    def test_to_internal_value_invalid_not_list(self):
        """Test error when data is not a list."""
        field = UserTagListSerializerField()

        with pytest.raises(ValidationError):
            field.to_internal_value("not-a-list")

    def test_to_internal_value_invalid_not_strings(self):
        """Test error when tags are not strings."""
        field = UserTagListSerializerField()

        with pytest.raises(ValidationError):
            field.to_internal_value([1, 2, 3])
