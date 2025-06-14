# Django Kubernetes

Middleware and Views for Kubernetes liveness and readiness probes and Django management commands for Kubernetes jobs such as waiting for the database to be ready or ensuring an admin user exists or is created from environment variables.

Let's face it; running a Django app on a Kubernetes cluster is a bit difficult - Django was built by folks who were running it on virtual machines or even bare metal hardware! They expected a shell environment available to them to be able to run management commands and influence how Django started up when in production.

When Django is orchestrated, we somehow have to manage these commands in our clusters; either by manually running the commands or creating init containers or Jobs that our deployments depend on. Moreover, once the pods are up and running, we need to ensure that the Kubernetes control layer can manipulate them as needed.

That's where this package comes in, it provides the following helpers to make your Django deployments on Kubernetes easier:

**Readiness Probes**

- `DatabaseProbe`: Checks that a connection can be established to the database
- `MemcachedProbe`: Checks that the cache nodes are available and ready

**Views**

- `LivenessView`: responds Ok to `/livez` and `/healthz` path requests
- `ReadinessView`: respond Ok if readiness probes are fine, else 503

**Middleware**

- `ProbeMiddleware`: performs `/livez`, `/healthz`, and `/readyz` checks with readiness probes before any middleware or views might interact with those services and raise a 500 error or some other error.

**Management Commands**

- `./manage.py probe`: a CLI version of the probes with `--live`, `--health`, and `--ready` checks that can be used by Kubernetes probe `exec` commands.
- `./manage.py wait4db`: sleeps until the database is ready and available
- `./manage.py ensureadmin`: reads environment variables for an admin user and creates that super user if the record does not already exist in the database.

More documentation coming soon!

