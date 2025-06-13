from typing import Sequence
from dataclasses import dataclass
from django.conf import settings as django_settings

# All settings prefixed with DJK8S_ are considered part of the djk8s app.
PREFIX = "DJK8S_"


@dataclass(frozen=True)
class AppSettings(object):
    """
    This class defines the default settings for the djk8s app. These settings can be
    overridden using similar names in the Django settings module.

    Access this instance as ``djk8s.conf.settings`` to ensure that you can get the
    default values for the django kubernetes app without them specifically being set
    in the Django settings module.
    """

    DJK8S_READY_PATHS: Sequence[str] = ("/readyz",)
    """The ProbeMiddleware will respond to GET requests at thyese paths after doing database and cache checks."""

    DJK8S_HEALTH_PATHS: Sequence[str] = ("/healthz", "/livez")
    """The ProbeMiddleware will respond to GET requests at these paths with a 200 Ok and will abort the request."""

    def __getattribute__(self, name: str) -> any:
        """
        Check if a Django project setting should override the app default.
        """
        if name.startswith(PREFIX) and hasattr(django_settings, name):
            return getattr(django_settings, name)
        return super().__getattribute__(name)


settings = AppSettings()
