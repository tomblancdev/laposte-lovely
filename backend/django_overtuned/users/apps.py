import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "django_overtuned.users"
    verbose_name = _("Users")

    def ready(self):
        with contextlib.suppress(ImportError):
            import django_overtuned.users.signals  # noqa: F401
