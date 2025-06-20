from django.test import TestCase
from django.test import override_settings


@override_settings(
    ROOT_URLCONF="tests.nourls",
)
class TestProbeMiddleware(TestCase):
    """
    Test the ProbeMiddleware to ensure it correctly handles liveness and readiness probes.
    """

    @override_settings(MIDDLEWARE=[])
    def test_no_views(self):
        # View tests won't work if views are enabled
        for path in ["/livez", "/healthz", "/readyz"]:
            response = self.client.get(path)
            self.assertEqual(
                response.status_code, 404, f"Expected 404 for {path} without views"
            )

    def test_ready_response(self):
        response = self.client.get("/readyz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Ok")

    def test_health_response(self):
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Ok")

    def test_live_response(self):
        response = self.client.get("/livez")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Ok")

    @override_settings(
        DJK8S_READINESS_PROBES=[
            "djk8s.probes.DatabaseProbe",
            "djk8s.probes.MemcachedProbe",
            "tests.probes.NeverReady"
        ]
    )
    def test_not_ready(self):
        response = self.client.get("/readyz")
        self.assertEqual(response.status_code, 503)
        self.assertIn("test is not ready", response.content.decode())

        response = self.client.get("/livez")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Ok")
