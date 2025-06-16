from djk8s.conf import settings
from django.db import connections
from django.core.management.commands.migrate import Command as MigrateCommand


class Command(MigrateCommand):

    help = (
        "Run Django migrations against postgres with an "
        "advisory lock; safe across multiple processes."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "-L",
            "--lock-id",
            type=int,
            default=settings.DJK8S_MIGRATE_LOCK_ID,
            help=(
                "The advisory lock ID to use for migrations."
            ),
        )
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        database = options["database"]
        if not options["skip_checks"]:
            self.check(databases=[database])

        conn = connections[database]
        conn.prepare_database()

        lock_id = options["lock_id"]
        with conn.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_lock(%s);", [lock_id])
            try:
                super().handle(*args, **options)
            finally:
                cursor.execute("SELECT pg_advisory_unlock(%s);", [lock_id])
