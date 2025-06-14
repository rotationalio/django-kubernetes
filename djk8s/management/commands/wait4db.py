import sys
from time import time, sleep

from django.db.utils import OperationalError
from django.db import DEFAULT_DB_ALIAS, connections
from django.core.management.base import BaseCommand, CommandError


def wait_for_database(
    timeout=180, stable=5, interval=1, database=DEFAULT_DB_ALIAS, **kwargs
):
    """
    Waits for the database to be ready and stable before returning.

    :param timeout: Maximum time to wait for the database to be ready (in seconds).
    :param stable: Time to wait for the database to remain stable (in seconds).
    :param interval: Time between checks for database readiness (in seconds).
    :param database: The database alias to check.
    """
    alive_start = None
    connection = connections[database]
    start = time()

    while True:
        # loop until we have a connection or timeout is reached
        while True:
            try:
                connection.cursor().execute("SELECT 1")
                if not alive_start:
                    alive_start = time()
                break
            except OperationalError as e:
                alive_start = None

                elapsed = time() - start
                if elapsed > timeout:
                    raise TimeoutError("Could not establish database connection") from e

                msg = str(e).strip()
                sys.stderr.write(
                    f"Database not ready: (cause: {msg}, elapsed: {elapsed}s\n"
                )
                sys.stderr.flush()

                sleep(interval)

        uptime = int(time() - alive_start)
        sys.stdout.write(f"Connection alive for > {uptime}s\n")

        if uptime >= stable:
            break
        sleep(interval)


class Command(BaseCommand):

    help = "Waits for the database to be ready before exiting."

    def add_arguments(self, parser):
        args = {
            ("-t", "--timeout"): {
                "type": int,
                "default": 180,
                "metavar": "SEC",
                "help": "number of seconds to wait for database until timeout, default: 180",
            },
            ("-s", "--stable"): {
                "type": int,
                "default": 5,
                "metavar": "SEC",
                "help": "stability timeout to wait for continuous database connection, default: 5",
            },
            ("-i", "--interval"): {
                "type": int,
                "default": 1,
                "metavar": "SEC",
                "help": "number of seconds to wait between database checks, default: 1",
            },
            ("-d", "--database"): {
                "default": DEFAULT_DB_ALIAS,
                "help": "which database to wait for, default: 'default'",
            },
        }

        for pargs, kwargs in args.items():
            if isinstance(pargs, str):
                pargs = (pargs,)
            parser.add_argument(*pargs, **kwargs)

    def handle(self, *args, **options):
        self.validate(**options)
        wait_for_database(**options)

    def validate(self, **options):
        if options.get("timeout", 0) <= 0:
            raise CommandError("Timeout must be greater than 0 seconds.")

        if options.get("stable", 0) <= 0:
            raise CommandError("Stability timeout must be greater than 0 seconds.")

        if options.get("interval", 0) <= 0:
            raise CommandError("Interval must be greater than 0 seconds.")

        if not options.get("database"):
            raise CommandError("Database must be specified.")
