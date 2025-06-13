import abc
import logging

from django.http import HttpResponseServerError


logger = logging.getLogger("djk8s.probe")


class NotReady(Exception):
    """
    Exception raised when the application is not ready to serve requests.
    """

    def __init__(self, content: str = "Not ready", status: int = 503):
        """
        Initialize the NotReady exception with a message and status code.

        :param content: The message to return.
        :param status: The HTTP status code to return.
        """
        self.content = content
        self.status = status
        super().__init__(content)

    def response(self):
        """
        Return an HTTP response for the exception.
        """
        return HttpResponseServerError(
            content=self.content,
            status=self.status,
            content_type="text/plain",
        )


class ReadinessProbe(abc.ABC):
    """
    Base classes for all readiness probes.
    """

    @abc.abstractmethod
    def ready(self, request):
        """
        Check if the application is ready to serve requests.

        :param request: The HTTP request object.
        :raises NotReady: If the application is not ready.
        """
        return None


class DatabaseProbe(ReadinessProbe):

    def ready(self, request):
        """
        Check if the database is ready to serve requests.

        :param request: The HTTP request object.
        :raises NotReady: If the database is not ready.
        """
        try:
            from django.db import connections

            for name in connections:
                with connections[name].cursor() as cursor:
                    cursor.execute("SELECT 1")
                    if cursor.fetchone() is None:
                        raise NotReady(
                            f"db: database '{name}' is not responding"
                        )
        except Exception as e:
            logger.exception(f"database readiness check failed: {str(e)}")
            raise NotReady("db: could not connect to database")


class MemcachedProbe(ReadinessProbe):

    def ready(self, request):
        """
        Check if memcached caches are ready to serve requests.

        :param request: The HTTP request object.
        :raises NotReady: If the cache is not ready.
        """
        try:
            from django.core.cache import caches
            from django.core.cache.backends.memcached import BaseMemcachedCache

            for cache in caches.all():
                if isinstance(cache, BaseMemcachedCache):
                    stats = cache.get_stats()
                    if len(stats) != len(cache._servers):
                        raise NotReady("cache: memcache is not responding")
        except Exception as e:
            logger.exception(f"cache readiness check failed: {str(e)}")
            raise NotReady("cache: could not connect to cache")
