from django.urls import path
from djk8s.views import LivenessView, ReadinessView


urlpatterns = [
    path("livez", LivenessView.as_view(), name="liveness-probe"),
    path("healthz", LivenessView.as_view(), name="health-probe"),
    path("readyz", ReadinessView.as_view(), name="readiness-probe"),
]
