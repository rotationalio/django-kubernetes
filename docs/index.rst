.. Django Kubernetes documentation master file, created by
   sphinx-quickstart on Mon Jun 16 17:41:52 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Django Kubernetes
=================

Let's face it; running a Django app on a Kubernetes cluster is a bit difficult - Django was built by folks who were running it on virtual machines or even bare metal hardware! They expected a shell environment available to them to be able to run management commands and influence how Django started up when in production.

When Django is orchestrated, we somehow have to manage these commands in our clusters; either by manually running the commands or creating init containers or Jobs that our deployments depend on. Moreover, once the pods are up and running, we need to ensure that the Kubernetes control layer can manipulate them as needed.

That's where this package comes in, it provides middleware and views for Kubernetes liveness and readiness probes and Django management commands for Kubernetes jobs such as waiting for the database to be ready or ensuring an admin user exists or is created from environment variables.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   setup
   settings
   probes
   commands
   api

