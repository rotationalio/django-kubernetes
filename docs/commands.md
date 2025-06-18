# Management Commands

`django-kubernetes` provides some additional management commands that are useful for executing as Kubernetes jobs or as init containers. These are standard Django management commands that can be executed via the `manage.py` script so long as the `djk8s` app is listed in your `INSTALLED_APPS` setting.

## Ensure Admin

In order to create a superuser, you generally have to run the `python manage.py createsuperuser` command; this would mean using `kubectl exec` to execute this command against one of your running pods. However if you're in a continuous deployment environment or you're managing multiple environments, it's nicer to have a Kubernetes job that checks if the admin user doesn't exist and creates it using values from a Kubernetes secret if it doesn't.

The `ensureadmin` management command does exactly that -- and is configured from the environment so you can attach superuser credentials from a Secret object. This streamlines deployments and ensures that a superuser is always available for you to access the Django CMS.

```
$ python manage.py ensureadmin -h
usage: manage.py ensureadmin [-h] [-u USERNAME] [-p PASSWORD] [-e EMAIL] [-d {default}] [--version] [-v {0,1,2,3}] [--settings SETTINGS]
                             [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color] [--skip-checks]

Ensures that a Django superuser exists with credentials from environment variables.

options:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        The username for the Django admin, $DJANGO_ADMIN_USERNAME
  -p PASSWORD, --password PASSWORD
                        The password for the Django admin, $DJANGO_ADMIN_PASSWORD
  -e EMAIL, --email EMAIL
                        The email for the Django admin, $DJANGO_ADMIN_EMAIL
  -d {default}, --database {default}
                        Specifies the database to use. Default is 'default'.
  --version             Show program's version number and exit.
  -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output
  --settings SETTINGS   The Python path to a settings module, e.g. "myproject.settings.main". If this isn't provided, the
                        DJANGO_SETTINGS_MODULE environment variable will be used.
  --pythonpath PYTHONPATH
                        A directory to add to the Python path, e.g. "/home/djangoprojects/myproject".
  --traceback           Display a full stack trace on CommandError exceptions.
  --no-color            Don't colorize the command output.
  --force-color         Force colorization of the command output.
  --skip-checks         Skip system checks.
```

And example Kubernetes job to ensure the admin user exists:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: myapp-ensure-admin
spec:
  template:
    spec:
      containers:
        - name: myapp
          image: myapp:v1.0.0
          command: ["python", "manage.py", "ensureadmin"]
          env:
          - name: DJANGO_SETTINGS_MODULE
            value: myapp.settings
          - name: DATABASE_URL
            valueFrom:
              secretKeyRef:
                name: myapp
                key: databaseURL
          - name: DJANGO_ADMIN_USERNAME
            value: admin
          - name: DJANGO_ADMIN_PASSWORD
            valueFrom:
              secretKeyRef:
                name: myapp
                key: adminUsername
          - name: DJANGO_ADMIN_EMAIL
            valueFrom:
              secretKeyRef:
                name: myapp
                key: adminEmail
      restartPolicy: Never
  backoffLimit: 3
```

## Locked Migrate

Django migrations must be run before your app can start. Most of the time this is handled in Kubernetes by either creating a migrate Job or using init containers. The init containers method is convenient because you don't have to constantly run a job and all you have to do is restart your pods to apply a migration. However, if you have a deployment with more than 1 replica then the migration will be run for each pod in the replica set.

The `python manage.py migrate` command does use a transaction to apply migrations safely; however depending on the schema and operations, it might not protect from multiple processes applying the migration simultaneously, which is what would happen if a Deployment with multiple replicas is launched. The locked migrate command uses a Postgres advisory lock before applying migrations, ensuring the migration is safe across processes.

```
$ python manage.py lockedmigrate -h
usage: manage.py lockedmigrate [-h] [-L LOCK_ID] [--noinput] [--database {default}] [--fake] [--fake-initial] [--plan] [--run-syncdb]
                               [--check] [--prune] [--version] [-v {0,1,2,3}] [--settings SETTINGS] [--pythonpath PYTHONPATH]
                               [--traceback] [--no-color] [--force-color] [--skip-checks]
                               [app_label] [migration_name]

Run Django migrations against postgres with an advisory lock; safe across multiple processes.

positional arguments:
  app_label             App label of an application to synchronize the state.
  migration_name        Database state will be brought to the state after that migration. Use the name "zero" to unapply all migrations.

options:
  -h, --help            show this help message and exit
  -L LOCK_ID, --lock-id LOCK_ID
                        The advisory lock ID to use for migrations.
  --noinput, --no-input
                        Tells Django to NOT prompt the user for input of any kind.
  --database {default}  Nominates a database to synchronize. Defaults to the "default" database.
  --fake                Mark migrations as run without actually running them.
  --fake-initial        Detect if tables already exist and fake-apply initial migrations if so. Make sure that the current database
                        schema matches your initial migration before using this flag. Django will only check for an existing table name.
  --plan                Shows a list of the migration actions that will be performed.
  --run-syncdb          Creates tables for apps without migrations.
  --check               Exits with a non-zero status if unapplied migrations exist and does not actually apply migrations.
  --prune               Delete nonexistent migrations from the django_migrations table.
  --version             Show program's version number and exit.
  -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output
  --settings SETTINGS   The Python path to a settings module, e.g. "myproject.settings.main". If this isn't provided, the
                        DJANGO_SETTINGS_MODULE environment variable will be used.
  --pythonpath PYTHONPATH
                        A directory to add to the Python path, e.g. "/home/djangoprojects/myproject".
  --traceback           Display a full stack trace on CommandError exceptions.
  --no-color            Don't colorize the command output.
  --force-color         Force colorization of the command output.
  --skip-checks         Skip system checks.
```

## Wait for Database

This command waits for the database to become ready and migrated before returning (or erroring after some timeout). This is useful for init containers to make sure migration jobs are applied before the application pods boot up.

```
$ python manage.py wait4db -h
usage: manage.py wait4db [-h] [-t SEC] [-s SEC] [-i SEC] [-d DATABASE] [--version] [-v {0,1,2,3}] [--settings SETTINGS]
                         [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color] [--skip-checks]

Waits for the database to be ready before exiting.

options:
  -h, --help            show this help message and exit
  -t SEC, --timeout SEC
                        number of seconds to wait for database until timeout, default: 180
  -s SEC, --stable SEC  stability timeout to wait for continuous database connection, default: 5
  -i SEC, --interval SEC
                        number of seconds to wait between database checks, default: 1
  -d DATABASE, --database DATABASE
                        which database to wait for, default: 'default'
  --version             Show program's version number and exit.
  -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output
  --settings SETTINGS   The Python path to a settings module, e.g. "myproject.settings.main". If this isn't provided, the
                        DJANGO_SETTINGS_MODULE environment variable will be used.
  --pythonpath PYTHONPATH
                        A directory to add to the Python path, e.g. "/home/djangoprojects/myproject".
  --traceback           Display a full stack trace on CommandError exceptions.
  --no-color            Don't colorize the command output.
  --force-color         Force colorization of the command output.
  --skip-checks         Skip system checks.
```