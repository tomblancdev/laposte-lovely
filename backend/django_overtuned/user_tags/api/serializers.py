from rest_framework import serializers
from taggit.serializers import TaggitSerializer
from taggit.serializers import TagListSerializerField

from django_overtuned.user_tags.models import UserTag


class UserTagSerializer(serializers.ModelSerializer[UserTag]):
    class Meta:
        model = UserTag
        fields = ["id", "name", "slug"]
        read_only_fields = ["id", "slug"]


class UserTagListSerializerField(TagListSerializerField):
    """
    A field for user tags that extends TagListSerializerField from django-taggit.
    Automatically associates tags with the authenticated user.
    """


class UserTaggitSerializer(TaggitSerializer):
    """
    Base serializer class for models using UserTag with TaggableManager.
    Extends TaggitSerializer to work with user-specific tags.

    Example:
        class MyModelSerializer(UserTaggitSerializer, serializers.ModelSerializer):
            tags = UserTagListSerializerField()

            class Meta:
                model = MyModel
                fields = '__all__'
    """

    def _save_tags(self, instance, tag_list):
        """Override to create user-specific tags."""
        if not hasattr(instance, "tags"):
            return None

        # Get the user from context
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            # Fall back to default behavior if no authenticated user
            return super()._save_tags(instance, tag_list)

        user = request.user

        # Get or create UserTag objects for this user
        tag_objects = []
        for tag_name in tag_list:
            tag, _ = UserTag.objects.get_or_create(
                name=tag_name,
                user=user,
            )
            tag_objects.append(tag)

        # Set the tags on the instance
        instance.tags.set(*tag_objects)
        return None


# Export for use in other apps
__all__ = ["UserTagListSerializerField", "UserTagSerializer", "UserTaggitSerializer"]
