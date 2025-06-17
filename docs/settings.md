# Settings

`django-kubernetes` works flexibly with environment variables and the Django settings module to allow you to have the most control over your Kubernetes objects that manage your web application.

Any settings that are specific to the `django-kubernetes` app are prefixed with `DJK8S_`. All settings have reasonable defaults, but they can be changed by adding those setting values to your `settings.py` in your Django project or wherever your `$DJANGO_SETTINGS_MODULE` is pointed to.

## Liveness Probe Paths

If you've setup liveness probes using the middleware, you can modify which paths respond to readiness and liveness probes.

- `DJK8S_HEALTH_PATHS` (default `/livez` and `/healthz`): the path(s) that you'd like the middleware to respond 200 Ok if the apps is running for heartbeats and liveness checks.
- `DJK8S_READY_PATHS` (default: `/readyz`): the path(s) that you'd like the middleware to first perform readiness probes (e.g. database and caches) before returning either a 503 or 200 if the application is ready to be used.

## Readiness Probes

- `DJK8S_READINESS_PROBES`: A list of the readiness checks that you'd like performed before responding to a readiness probe request. The list is of classes that can be imported that implement the `ReadinessProbe` ABC. The defaults are `djk8s.probes.DatabaseProbe` and `djk8s.probes.MemcachedProbe`.

## API Reference

Below is the auto-generated documentation from the `djk8s.conf` module; if there is a discrepency between what is described below vs. what is in the configuration guide; the description below is probably more accurate. Please file a documentation issue if you discover such a discrepancy!

```{eval-rst}
.. automodule:: djk8s.conf
    :noindex:

    .. autoclass:: AppSettings()
        :members:
```