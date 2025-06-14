from djk8s.conf import settings
from django.http import HttpResponse
from django.views.generic import View
from djk8s.probes import NotReady, ReadinessProbe
from django.utils.functional import classproperty
from django.utils.decorators import classonlymethod
from django.core.exceptions import ImproperlyConfigured


class LivenessView(View):
    """
    A view that always returns a 200 OK response for liveness and health check probes.
    """

    def get(self, *args, **kwargs):
        return HttpResponse("Ok", status=200, content_type="text/plain")


class ReadinessView(View):
    """
    A view that checks readiness using configured probes. If any probe raises NotReady,
    it returns a 503 Service Unavailable response. Otherwise it returns a 200 OK.
    """

    @classproperty
    def probes(cls):
        if not hasattr(cls, "__probes"):
            cls.__probes = [Probe() for Probe in settings.DJK8S_READINESS_PROBES]
        return cls.__probes

    @classonlymethod
    def as_view(cls, **kwargs):
        """
        Override the as_view method to ensure probes are initialized.
        """
        if not cls.probes:
            raise ImproperlyConfigured(
                "No readiness probes configured for ReadinessView."
            )

        for probe in cls.probes:
            if not isinstance(probe, ReadinessProbe):
                raise ImproperlyConfigured(
                    f"Probe {probe} is not an instance of ReadinessProbe."
                )

        return super().as_view(**kwargs)

    def get(self, request, *args, **kwargs):
        """
        Check readiness by executing all configured probes.
        If any probe is not ready, return a 503 Service Unavailable response.
        """
        try:
            for probe in self.probes:
                probe.ready(request)
        except NotReady as e:
            return e.response()

        return HttpResponse("Ok", status=200, content_type="text/plain")
