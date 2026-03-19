#!/home/ly1868/Temp_Pylot/docvenv/bin/python3
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

# Add project root to sys.path so autodoc can import prfpylot and submodules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../prfpylot")))

project = "PROFFASTpylot"
copyright = "2023, Lena Feld, Benedikt Herkommer Karlsruhe Institut of Technology"
author = "Lena Feld, Benedikt Herkommer"
release = "2.4.1-4"


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


def remove_module_docstring(app, what, name, obj, options, lines):
    if what == "module":
        del lines[:]


def setup(app):
    app.connect("autodoc-process-docstring", remove_module_docstring)


extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_mdinclude",
]

napoleon_use_rtype = False
autodoc_default_options = {
    "members": True,
    # "undoc-members": True,
    "private-members": False,
    "show-inheritance": True,
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_theme_options = {
    "caption_font_family": "Roboto",
    "head_font_family": "Roboto",
}

html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
