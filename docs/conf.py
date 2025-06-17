# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

from pathlib import Path

# Add the project root to the system path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


project = 'Django Kubernetes'
copyright = '2025, Rotational Labs'
author = 'Rotational Labs'
release = 'v1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_rtd_theme',
    'myst_parser',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autodoc',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']
html_baseurl = os.environ.get("READTHEDOCS_CANONICAL_URL", "/")

# -- Options for intersphinx extension --------------------------------------
intersphinx_mapping = {
    "django": (
        "https://docs.djangoproject.com/en/stable/",
        None,
    ),
}
