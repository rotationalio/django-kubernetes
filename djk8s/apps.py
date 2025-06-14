from django.apps import AppConfig


class Djk8SConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "djk8s"
    label = "kubernetes"
    verbose_name = "Django Kubernetes"
