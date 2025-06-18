# Installation

At the command line:

```
$ pip install django-kubernetes
```

Once you've installed the dependency from PyPI you'll need to add the app to your `INSTALLED_APPS` Django settings; this will enable the management commands to be run from your `manage.py` file.

```python
# Add 'djk8s' to INSTALLED_APPS
INSTALLED_APPS = (
    # ...
    'djk8s',
    # ...
)
```

Note that the order of `'djk8s'` in the `INSTALLED_APPS` setting does not matter.

## Quickstart

The quickest and simplest way to get started is to enable liveness and readiness probes with middleware; modify your settings as follows:

```python
# Request Handling
MIDDLEWARE = [
    "djk8s.middleware.ProbeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # ...
]
```

We strongly recommend that you make the `djk8s.middleware.ProbeMiddleware` the first middleware in the list so that there are no database or caches accesses before the probe is handled.

If you prefer, you can also use views for the liveness and readiness probes; but these views will be subject to any middleware that occurs before they are handled.

## Dependencies

`django-kubernetes` has been tested on Django 5.2 and on Python 3.11, 3.12, and 3.13. There is no reason to believe that it wouldn't work on Django 3.2+ and other versions of Python; if you need a compatibility release that reduces the dependencies; please open an issue.

## Logging

The `django-kubernetes` liveness and readiness probes use the `"djk8s.probe"` logger. Enable that logger in settings to see log messages during probes to help you debug errors:

```python
LOGGING = {
    ...
    'loggers': {
        'djk8s.probe': {
            'handlers': ['console'],
            'level': 'DEBUG'
        },
    ...
}
```

Make sure to use the appropriate handler for your app.