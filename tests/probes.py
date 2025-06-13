from djk8s.probes import ReadinessProbe, NotReady


class NeverReady(ReadinessProbe):

    def ready(self, request):
        raise NotReady("test is not ready", status=503)
