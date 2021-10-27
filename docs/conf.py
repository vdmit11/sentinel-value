# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("../"))


# -- Project information -----------------------------------------------------

project = "sentinel-value"
copyright = "2021, Dmitry Vasilyanov"  # pylint: disable=redefined-builtin
author = "Dmitry Vasilyanov"


# -- General configuration ---------------------------------------------------

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Don't add module names to functions/classes.
add_module_names = False
python_use_unqualified_type_names = True

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx_copybutton",
    "sphinx_toggleprompt",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__call__,__init__",
}

# Remove type hints from function signatures (and instead put them to function description).
autodoc_typehints = "description"

# Don't evaluate default values for function parameters.
# This way they usually look nicer in the docs.
autodoc_preserve_defaults = True

# Don't generate files when using sphinx.ext.autosummary
# I just don't use this feature (that enabled by default).
autosummary_generate = False


# Configure sphinx_copybutton extensions to work with Python doctest code snippets
copybutton_prompt_text = r">>> |\.\.\. | $"
copybutton_prompt_is_regexp = True
copybutton_remove_prompts = True
copybutton_only_copy_prompt_lines = False

# Shift '>>>' button away from corner, otherwise it conflicts with sphinx_copybutton
toggleprompt_offset_right = 40

# Allow links to standard Python docs and other documentation sites.
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
