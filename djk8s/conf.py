from typing import Sequence
from dataclasses import dataclass
from django.conf import settings as django_settings
from django.utils.module_loading import import_string


# All settings prefixed with DJK8S_ are considered part of the djk8s app.
PREFIX = "DJK8S_"

# All settings that are import strings should be imported when accessed.
IMPORT_STRINGS = (
    "DJK8S_READINESS_PROBES",
)


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

    DJK8S_READINESS_PROBES: Sequence[str] = (
        "djk8s.probes.DatabaseProbe",
        "djk8s.probes.MemcachedProbe",
    )
    """A list of readiness probes to check before responding to a readiness request."""

    def __getattribute__(self, name: str) -> any:
        """
        Check if a Django project setting should override the app default.
        """
        if name.startswith(PREFIX) and hasattr(django_settings, name):
            val = getattr(django_settings, name)
        else:
            val = super().__getattribute__(name)

        if name in IMPORT_STRINGS:
            return perform_import(val, name)
        return val


def perform_import(val: str, name: str) -> any:
    """
    If the given setting is a string import notation, then perform the import or imports
    """
    if val is None:
        return None
    if isinstance(val, str):
        return import_from_string(val, name)
    if isinstance(val, (list, tuple)):
        return [import_from_string(v, name) for v in val]
    return val


def import_from_string(val: str, name: str) -> any:
    try:
        return import_string(val)
    except ImportError as e:
        msg = f"Could not import '{val}' for Django Kubernetes setting '{name}'. {e.__class__.__name__}: {e}"
        raise ImportError(msg)


settings = AppSettings()
