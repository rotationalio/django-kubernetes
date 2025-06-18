# Probes

Kubernetes uses [startup, liveness, and readiness probes](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/) to determine if a container has started, to determine when a container might need to be restarted, and to determine if a container is ready to have traffic sent to it. Application developers are particularly concerned with _liveness_ and _readiness_ probes in order to manage its state during orchestration.

For web services, probes are implemented as HTTP requests to the container; for non-web services an `exec` command can be used against the container. The `django-kubernetes` library implements middleware and views for HTTP probes and Django management commands for exec probes.

- **Liveness**: returns a 200 Ok or exit 0 response if the application is running.
- **Readiness**: returns a 503 Unavailable or exit 1 response if the application is waiting for resources; e.g. if it can't ping a database, the database doesn't have migrations applied, or if it can't ping caches, queues, etc; otherwise returns 200 Ok or exit 0.

`django-kubernetes` defines two readiness probes by default: database readiness and memcached readiness. The database readiness probe performs a `SELECT 1` against the database to determine if the database can be accessed and used. The Memcached probe loops through all cache instances and executes `cache_stats` to see if all cache instances ae responding. If neither of these raises an exception then the readiness probe reports ok. See the Advanced section below for other probes and how to define your own probes.

To configure your Django application _choose one_ of **middleware**, **views**, or **commands** to setup (it really doesn't make sense to choose more than one). Choose:

- **middleware**: when you want a quick and easy way to integrate probes into your application without fuss (the recommended methods).
- **views**: when you want to customize the behavior of the HTTP requests or ensure that middleware is executed before the request.
- **commands**: when you have a Django related non-web service running; e.g. Celery containers that are executing tasks on behalf of your Django server.

## Middleware

Middleware is the simplest and most convenient method to enable HTTP probes. As described in the quickstart, all you have to do to enable the middleware in your Django settings as follows:

```python
# Request Handling
MIDDLEWARE = [
    "djk8s.middleware.ProbeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # ...
]
```

The middleware checks to see if the request is a `GET` request to `/readyz`, `/livez`, or `/healthz` (or the liveness and readiness paths as configured by your settings) and if so, performs a liveness check for `/livez` or `/healthz` and a readiness check for `/readyz`, then aborts the request; otherwise it simply passes through the request to the next handler in the chain.

It is important that the middleware is added before any other middleware that might access the database or other resources being probed; if those middleware are involved then resources may be used before the readiness check and logging or exceptions that you don't want reported during readiness will be returned.

## Views

The alternative to middleware is to use views; you'll have to specify the views in your urls.py by including them:

```python
urlpatterns = [
    path("", include("djk8s.urls")),
    # ...
]
```

This will create the `/livez`, `/healthz`, and `/readyz` handlers. Alternatively you can specify exactly what paths you want to use with the views themselves:

```python
from djk8s.views import LivenessView, ReadinessView

urlpatterns = [
    path("/live", LivenessView.as_view(), name="liveness-probe"),
    path("/health", LivenessView.as_view(), name="health-probe"),
    path("/ready", ReadinessView.as_view(), name="readiness-probe"),
    # ...
]
```

Using the views is less desirable than the middleware as any middleware that accesses probed resources such as databases or caches will be enabled before the view can respond. However, if you need to reference probe URLs in templates or you want to be able to manually change the state of liveness or readiness, it may be preferred to use the views.

## Commands

If you have a Django-related app that does not implement a web service (e.g. Celery workers) you can use the Django management `probe` command that comes with `django-kubernetes` for liveness and readiness probes.

For a liveness check:

```
$ python manage.py probe --live
```

And for a readiness check:

```
$ python manage.py probe --ready
```

You can use the `-q` or `--quiet` to suppress any text written to `stdout` so that only the exit code is returned. The full help listing for the command is:

```
$ python manage.py probe -h
usage: manage.py probe [-h] [-R] [-L] [-H] [-q] [--version] [-v {0,1,2,3}] [--settings SETTINGS]
                       [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color] [--skip-checks]

Allows Kubernetes to probe the readiness and liveness state of the container with an exec instead of an HTTP request.

options:
  -h, --help            show this help message and exit
  -R, --ready           Check the readiness state of the container
  -L, --live            Check the liveness state of the container
  -H, --health          Check the health state of the container
  -q, --quiet           Suppress output for the probe check
  --version             Show program's version number and exit.
  -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output
  --settings SETTINGS   The Python path to a settings module, e.g. "myproject.settings.main". If this isn't provided,
                        the DJANGO_SETTINGS_MODULE environment variable will be used.
  --pythonpath PYTHONPATH
                        A directory to add to the Python path, e.g. "/home/djangoprojects/myproject".
  --traceback           Display a full stack trace on CommandError exceptions.
  --no-color            Don't colorize the command output.
  --force-color         Force colorization of the command output.
  --skip-checks         Skip system checks.
```

## Kubernetes

To use the HTTP probes in your Kubernetes containers, you would define your Pod spec as follows:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      containers:
      - name: myapp
        image: myapp:v1.0.0
        ports:
        - name: http
          containerPort: 8000
          protocol: TCP
        livenessProbe:
          httpGet:
            path: /livez
            port: 8000
            httpHeaders:
            - name: X-Kubernetes-Probe
              value: liveness
          initialDelaySeconds: 2
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /readyz
            port: 8000
            httpHeaders:
            - name: X-Kubernetes-Probe
              value: readiness
          initialDelaySeconds: 2
          periodSeconds: 10
```

To use the Django management probe command with your container, define your Kubernetes pod templates as follows:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myworker
spec:
  template:
    spec:
      containers:
      - name: myworker
        image: myworker:v1.0.0
        livenessProbe:
          exec:
            command:
            - python
            - manage.py
            - probe
            - --live
          initialDelaySeconds: 2
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - python
            - manage.py
            - probe
            - --ready
          initialDelaySeconds: 2
          periodSeconds: 10
```

## Advanced

Readiness probes perform system checks before reporting ready or not. By default, `django-kubernetes` implements the `djk8s.probes.DatabaseProbe` and `djk8s.probes.MemcachedProbe` but you can configure which probes are used by modifying the `DJK8S_READINESS_PROBES` setting.

You can also define your own probe by subclassing `djk8s.probes.ReadinessProbe` and implementing the `ready` method, then adding your probe to the list of probes in `DJK8S_READINESS_PROBES`. The `ready` method should check whatever state or service you're trying to probe and raise a `djk8s.probes.NotReady` exception if the state is not ready or the service is not available.

For example, if you want to implement a Redis probe for your application, in `myapp/probes.py` you might write the following code:

```python
import logging

from djk8s.probes import NotReady, ReadinessProbe

logger = logging.getLogger("myapp.probe")


class RedisProbe(ReadinessProbe):

    def ready(self, request):
        try:
            redis_client.ping()
        except Exception as e:
            logger.exception(f"redis probe failed: {str(e)}")
            raise NotReady("redis: could not connect")
```

Then in your `settings.py` file:

```python
DJK8S_READINESS_PROBES = (
    'djk8s.probes.DatabaseProbe',
    'djk8s.probes.MemcachedProbe',
    'myapp.probes.RedisProbe',
)
```

If you would like to add probes to this package; please feel free to open a PR!
