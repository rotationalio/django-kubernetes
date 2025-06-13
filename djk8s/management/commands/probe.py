import sys

from djk8s.conf import settings
from djk8s.probes import NotReady, ReadinessProbe
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    help = "Allows Kubernetes to probe the readiness and liveness state of the container with an exec instead of an HTTP request."

    def add_arguments(self, parser):
        args = {
            "readiness": ("-R", "--ready"),
            "liveness": ("-L", "--live"),
            "health": ("-H", "--health"),
        }

        for name, pargs in args.items():
            parser.add_argument(
                *pargs,
                action="store_true",
                default=False,
                help=f"Check the {name} state of the container",
            )

        parser.add_argument(
            "-q", "--quiet",
            action="store_true",
            default=False,
            help="Suppress output for the probe check",
        )

    def handle(self, *args, **options):
        if (options["live"] or options["health"]) and options["ready"]:
            raise CommandError("cannot specify both a live/health and readiness check")

        if options["live"] or options["health"]:
            return self.livez(quiet=options["quiet"])

        if options["ready"]:
            return self.readyz(quiet=options["quiet"])

        raise CommandError("specify one of --live, --health, or --ready")

    def livez(self, quiet=False):
        if not quiet:
            self.stdout.write("Ok\n")
        sys.exit(0)

    def readyz(self, quiet=False):
        # Perform readiness checks
        probes = [
            Probe() for Probe in settings.DJK8S_READINESS_PROBES
        ]

        # Ensure all probes are instances of ReadinessProbe.
        for probe in probes:
            if not isinstance(probe, ReadinessProbe):
                raise CommandError(
                    f"probe {probe} is not an instance of ReadinessProbe."
                )

        # If no probes are configured, raise an error.
        if not probes:
            raise CommandError(
                "no readiness probes configured for Django Kubernetes ProbeMiddleware."
            )

        try:
            for probe in probes:
                probe.ready(None)  # Pass None as request since we don't have one
        except NotReady as e:
            if not quiet:
                self.stdout.write(str(e)+"\n")
            sys.exit(1)

        if not quiet:
            self.stdout.write("Ok\n")
        sys.exit(0)
