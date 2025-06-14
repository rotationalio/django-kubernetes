import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, connections, ValidationError
from django.contrib.auth.password_validation import validate_password


DJANGO_ADMIN_USERNAME = os.environ.get("DJANGO_ADMIN_USERNAME", None)
DJANGO_ADMIN_PASSWORD = os.environ.get("DJANGO_ADMIN_PASSWORD", None)
DJANGO_ADMIN_EMAIL = os.environ.get("DJANGO_ADMIN_EMAIL", None)


class Command(BaseCommand):

    help = "Ensures that a Django superuser exists with credentials from environment variables."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.UserModel = get_user_model()

        self.username_field = self.UserModel._meta.get_field(
            self.UserModel.USERNAME_FIELD
        )

        self.email_field = self.UserModel._meta.get_field(self.UserModel.EMAIL_FIELD)
        self.password_field = "password"

    def add_arguments(self, parser):
        args = {
            ("-u", "--username"): {
                "type": str,
                "default": DJANGO_ADMIN_USERNAME,
                "help": "The username for the Django admin, $DJANGO_ADMIN_USERNAME",
            },
            ("-p", "--password"): {
                "type": str,
                "default": DJANGO_ADMIN_PASSWORD,
                "help": "The password for the Django admin, $DJANGO_ADMIN_PASSWORD",
            },
            ("-e", "--email"): {
                "type": str,
                "default": DJANGO_ADMIN_EMAIL,
                "help": "The email for the Django admin, $DJANGO_ADMIN_EMAIL",
            },
            ("-d", "--database"): {
                "default": DEFAULT_DB_ALIAS,
                "choices": tuple(connections),
                "help": "Specifies the database to use. Default is 'default'.",
            },
        }

        for pargs, kwargs in args.items():
            if isinstance(pargs, str):
                pargs = (pargs,)
            parser.add_argument(*pargs, **kwargs)

    def handle(self, *args, **options):
        if not options["username"]:
            raise CommandError("Username is required. Set DJANGO_ADMIN_USERNAME or use --username.")

        if not options["password"]:
            raise CommandError("Password is required. Set DJANGO_ADMIN_PASSWORD or use --password.")

        info = {
            self.username_field: options["username"],
            self.password_field: options["password"],
            self.email_field: options["email"],
        }

        # Validate the password
        try:
            validate_password(password=info[self.password_field], user=None)
        except ValidationError as e:
            raise CommandError(f"Password validation error: {e}")

        db = self.UserModel._default_manager.db_manager(options["database"])

        # Check if the user already exists, create if not.
        try:
            db.get(username=info[self.username_field])
            self.stdout.write("Admin user already exists, service is ready.")
        except self.UserModel.DoesNotExist:
            db.create_superuser(**info)
            self.stdout.write("Admin user created from environment variables.")
