# Probes

Kubernetes uses [startup, liveness, and readiness probes](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/) to determine if a container has started, to determine when a container might need to be restarted, and to determine if a container is ready to have traffic sent to it. Application developers are particularly concerned with _liveness_ and _readiness_ probes in order to manage its state during orchestration.

For web services, probes are implemented as HTTP requests to the container; for non-web services an `exec` command can be used against the container. The `django-kubernetes` library implements middleware and views for HTTP probes and Django management commands for exec probes.

To configure your Django application _choose one_ of **middleware**, **views**, or **commands** to setup (it really doesn't make sense to choose more than one). Choose:

- **middleware**: when you want a quick and easy way to integrate probes into your application without fuss (the recommended methods).
- **views**: when you want to customize the behavior of the HTTP requests or ensure that middleware is executed before the request.
- **commands**: when you have a Django related non-web service running; e.g. Celery containers that are executing tasks on behalf of your Django server.

## Middleware

Middleware is the simplest and most convenient method to enable HTTP probes.
