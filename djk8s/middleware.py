from djk8s.conf import settings
from django.http import HttpResponse
from djk8s.probes import NotReady, ReadinessProbe
from django.core.exceptions import ImproperlyConfigured


class ProbeMiddleware(object):
    """
    This middleware handles Kubernetes liveness, readiness, and health probes.
    Middleware is used instead of a view to ensure that there are no database or cache
    calls that might cause a 500 error or prevent an actual health check. If the
    middleware detects an unhealthy or unready state, it will return a 503 error.

    If you're not concerned about database usage or cache calls, you can use the
    provided probe views in `djk8s.views` instead.
    """

    def __init__(self, get_response):
        self.get_response = get_response

        # Readiness probes used to check if the application is ready to serve requests.
        self.probes = [Probe() for Probe in settings.DJK8S_READINESS_PROBES]

        # Ensure all probes are instances of ReadinessProbe.
        for probe in self.probes:
            if not isinstance(probe, ReadinessProbe):
                raise ImproperlyConfigured(
                    f"probe {probe} is not an instance of ReadinessProbe."
                )

        # If no probes are configured, raise an error.
        if not self.probes:
            raise ImproperlyConfigured(
                "no readiness probes configured for Django Kubernetes ProbeMiddleware."
            )

        # Paths that the middleware will directly handle instead of passing to a view.
        self.handlers = {}

        for path in settings.DJK8S_READY_PATHS:
            self.handlers[path] = self.ready

        for path in settings.DJK8S_HEALTH_PATHS:
            self.handlers[path] = self.health

        # If no paths are configured, raise an error.
        if not self.handlers:
            raise ImproperlyConfigured(
                "no ready or health paths configured for Django Kubernetes ProbeMiddleware."
            )

    def __call__(self, request):
        if request.method == "GET" and request.path in self.handlers:
            return self.handlers[request.path](request)
        return self.get_response(request)

    def health(self, request):
        """
        Always returns a 200 Ok response. If the Django server can handle requests,
        then it is healthy and live.
        """
        return HttpResponse("Ok", status=200, content_type="text/plain")

    def ready(self, request):
        """
        Connects to each database and performs a generic SQL query to check that the
        database connection is available and responding to requests. Connects to any
        caches and calls get_stats to check if the cache is online.
        """
        try:
            for probe in self.probes:
                probe.ready(request)
        except NotReady as e:
            return e.response()

        return HttpResponse("Ok", status=200, content_type="text/plain")
