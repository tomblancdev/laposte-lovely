from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()

# Create your models here.
# User personal tags model
try:
    from taggit.models import GenericTaggedItemBase
    from taggit.models import TagBase

    class UserTag(TagBase):
        """
        A tag that belongs to a single user.
        """

        # Override the name and slug fields to remove unique constraint
        name = models.CharField(verbose_name=_("name"), max_length=100)
        slug = models.SlugField(verbose_name=_("slug"), unique=False, max_length=100)

        user: models.ForeignKey[User] = models.ForeignKey(
            User,
            on_delete=models.CASCADE,
            related_name="tags",
        )

        class Meta:
            unique_together = ("name", "user")
            verbose_name = _("User Tag")
            verbose_name_plural = _("User Tags")

    class UserTaggedItem(GenericTaggedItemBase):
        """
        The intermediate table that links your content objects to UserTag.
        """

        tag: models.ForeignKey[UserTag] = models.ForeignKey(
            UserTag,
            on_delete=models.CASCADE,
            related_name="tagged_items",
        )


except ImportError:
    pass
