from django.test import TestCase, override_settings


class TestAppSettings(TestCase):
    """
    Test the AppSettings class to ensure it correctly retrieves settings from Django's settings module.
    """

    def test_default_settings(self):
        from djk8s.conf import settings

        self.assertEqual(settings.DJK8S_READY_PATHS, ("/readyz",))
        self.assertEqual(settings.DJK8S_HEALTH_PATHS, ("/healthz", "/livez"))

    @override_settings(
        DJK8S_READY_PATHS=["/custom_ready"],
        DJK8S_HEALTH_PATHS=["/custom_health"],
    )
    def test_custom_settings(self):
        from djk8s.conf import settings

        self.assertEqual(settings.DJK8S_READY_PATHS, ["/custom_ready"])
        self.assertEqual(settings.DJK8S_HEALTH_PATHS, ["/custom_health"])
