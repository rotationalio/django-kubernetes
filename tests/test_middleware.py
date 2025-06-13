from django.test import TestCase


class TestProbeMiddleware(TestCase):
    """
    Test the ProbeMiddleware to ensure it correctly handles liveness and readiness probes.
    """

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
